package XUpload;

use strict;
use lib '.';
use XFSConfig;
use Digest::MD5;
use LWP::UserAgent;
use File::Copy;
use Encode;

# file_tmp, file_name_orig, file_descr, file_public
# optional: usr_id, no_limits
sub ProcessFile
{
   my ($file,$f) = @_;

   $f->{ip}||=$ENV{REMOTE_ADDR};

   unless(-f $file->{file_tmp})
   {
      $file->{file_status}="No file on disk";
      return $file;
   }

   $file->{file_size} = -s $file->{file_tmp};

   my $ua = LWP::UserAgent->new(agent => "XFS-FSAgent", timeout => 90);
   if($c->{enable_clamav_virus_scan})
   {
      my $clam = join '', `clamscan --no-summary $file->{file_tmp}`;
      if($clam=~/: (.+?) FOUND/)
      {
         $file->{file_status}="file contain $1 virus";
         return $file;
      }
   }

   if($file->{file_name_orig}=~/\.torrent$/i && $f->{torr_on})
   {
      $file->{type}='torrent';
      require BitTorrent;
      my $bt = BitTorrent->new();
      my $tt = $bt->getTrackerInfo($file->{file_tmp});
      my ($over,$files);
      foreach my $ff ( @{$tt->{files}} )
      {
         next if $ff->{name}=~/padding_file/;
         $over=1 if $ff->{size} > $c->{max_upload_filesize}*1048576;
         $files.="$ff->{name}:$ff->{size}\n";
      }
      if($over)
      {
         $file->{file_status}="One or more files in torrent exceed filesize limit of $c->{max_upload_filesize} Mb";
         return $file;
      }
      else
      {
         my $res = $ua->post("http://$c->{bitflu_address}/new_torrent_httpui",
                             Content_Type => 'form-data',
                             Content => [torrent=>[$file->{file_tmp}]] )->content;
         if($res=~/ok => 1/)
         {
            my $res = $ua->post("$c->{site_cgi}/fs.cgi",
                                {
                                op           => 'add_torrent',
                                fs_key       => $c->{fs_key},
                                sid          => $tt->{hash},
                                sess_id      => $f->{sess_id}||'',
                                files        => $files,
                                total_size   => $tt->{total_size},
                                }
                               )->content;
            if($res=~/^ERROR:(.+)/)
            {
               $file->{file_status} = "Can't start torrent ($1)";
               return $file;
            }
            print"Content-type:text/html\n\n";
            print"<HTML><HEAD><Script type='text/javascript'>top.location='$c->{site_url}/?op=my_files';</Script></HEAD></HTML>";
            exit;
         }
         else
         {
            $res=~/msg => "(.+?)"/;
            $file->{file_status} = "Can't start torrent ($res)";
            return $file;
         }
      }
   }

   open(FILE,$file->{file_tmp})||die"cant open file";
   my $data;
   read(FILE,$data,4096);
   seek(FILE,-4096,2);
   read(FILE,$data,4096,4096);
   $file->{md5} = Digest::MD5::md5_base64 $data;

   if($c->{m_v} && $file->{file_name_orig}=~/\.(avi|divx|xvid|mpg|mpeg|vob|mov|3gp|flv|mp4|wmv|mkv)$/i)
   {
      my $info = join '', `mplayer $file->{file_tmp} -identify -frames 0 -quiet -ao null -vo null 2>/dev/null | grep ^ID_`;
      my @fields = qw(ID_LENGTH ID_VIDEO_WIDTH ID_VIDEO_HEIGHT ID_VIDEO_BITRATE ID_AUDIO_BITRATE ID_AUDIO_RATE ID_VIDEO_CODEC ID_AUDIO_CODEC ID_VIDEO_FPS);
      do{($f->{$_})=$info=~/$_=([\w\.]{2,})/is} for @fields;
      $f->{ID_LENGTH} = int $f->{ID_LENGTH};
      if($f->{ID_VIDEO_WIDTH})
      {
         $f->{ID_VIDEO_BITRATE}=int($f->{ID_VIDEO_BITRATE}/1000);
         $f->{ID_AUDIO_BITRATE}=int($f->{ID_AUDIO_BITRATE}/1000);
         $file->{file_spec} = 'V|'.join('|', map{$f->{$_}}@fields );
      }
   }

   if($file->{file_name_orig}=~/\.mp3$/i)
   {
      $file->{type}='audio';
      require MP3::Info;
      my $info = MP3::Info::get_mp3info($file->{file_tmp});
      if($info)
      {
         my $tag = MP3::Info::get_mp3tag($file->{file_tmp},1);
         $tag->{$_}=encode_utf8($tag->{$_}) for keys %$tag;
         $tag->{$_}=~s/\|//g for keys %$tag;
         $info->{SECS} = sprintf("%.1f", $info->{SECS} );
         $file->{file_spec}="A|$info->{SECS}|$info->{BITRATE}|$info->{FREQUENCY}|$tag->{ARTIST}|$tag->{TITLE}|$tag->{ALBUM}|$tag->{YEAR}";
      }
   }

   if($file->{file_name_orig}=~/\.rar$/i && $c->{m_b})
   {
      $file->{file_spec} = &rarGetInfo($file->{file_tmp});
      
   }
   $f->{fld_name}=~s/[\"\<\>]+//g;

   ##### LWP
   my $res = $ua->post("$c->{site_cgi}/fs.cgi",
                       {
                       fs_key       => $c->{fs_key},
                       file_name    => $file->{file_name_orig},
                       file_descr   => $file->{file_descr},
                       file_size    => $file->{file_size},
                       file_public  => $file->{file_public},
                       rslee        => $file->{rslee},
                       file_md5     => $file->{md5},
                       file_spec    => $file->{file_spec},
                       usr_id       => $file->{usr_id},
                       no_limits    => $file->{no_limits},
                       sid          => $file->{sid},
                       torrent      => $file->{torrent},
                       sess_id      => $f->{sess_id}||'',
                       file_password=> $f->{link_pass}||'',
                       file_ip      => $f->{ip},
                       fld_name     => $f->{fld_name},
                       }
                      );
   my $info = $res->content;
   #die $info;
   &logit("INFO:$info");
   ($file->{file_id},$file->{file_code},$file->{file_real},$file->{msg}) = $info=~/^(\d+):(\w+):(\w+):(.*)$/;

   if($file->{msg} ne 'OK')
   {
      $file->{file_status}=$file->{msg};
      return $file;
   }

   if(!$file->{file_code})
   {
      $file->{file_status}="error connecting to DB";
      return $file;
   }

   &SaveFile( $file ) if $file->{file_code} eq $file->{file_real};

   if($file->{new_size})
   {
      my $res = $ua->post("$c->{site_cgi}/fs.cgi",
                       {
                       fs_key    => $c->{fs_key},
                       op        => 'file_new_size',
                       file_code => $file->{file_code},
                       file_size => $file->{file_size},
                       file_name => $file->{file_name_orig},
                       }
                      );
   }
   return $file;
}

sub rarGetInfo
{
   my ($file_tmp) = @_;
   my $txt = `rar v $file_tmp`;
   my ($comment) = $txt=~/Comment: (.+?)\n+Pathname/is;
   ($txt) = $txt=~/-{9,}\n(.*?)\-{9,}/s;
   
   my (@rf,$pass);
   while($txt=~/\s*(.+?)\n\s*(\d+).+?\n/gs)
   {
      next unless $2;
      my $fsize = $2 > 1048576 ? sprintf("%.1f MB",$2/1048576) : sprintf("%.0f KB",$2/1024);
      my $fname=$1;
      $pass=1 if $fname=~s/^\*//;
      push @rf, "$fname - $fsize";
   }

   my $file_spec;
   $file_spec="password protected\n" if $pass;
   $file_spec.=join "\n", @rf;
   $file_spec.="\n\n$comment" if $comment;
   
   return $file_spec;
}

########

sub SaveFile
{
   my ($file) = @_;
   my $dx = sprintf("%05d",$file->{file_id}/$c->{files_per_folder});
   $file->{dx} = $dx;
   unless(-d "$c->{upload_dir}/$dx")
   {
      my $mode = 0777;
      mkdir("$c->{upload_dir}/$dx",$mode) || do{&logit("Fatal Error: Can't copy file from temp dir ($!)");&xmessage("Fatal Error: Can't copy file from temp dir ($!)")};
      chmod $mode,"$c->{upload_dir}/$dx";
   }
   move($file->{file_tmp},"$c->{upload_dir}/$dx/$file->{file_code}") || copy($file->{file_tmp},"$c->{upload_dir}/$dx/$file->{file_code}") || do{&logit("Fatal Error: Can't copy file from temp dir ($!)");&xmessage("Fatal Error: Can't copy file from temp dir ($!)")};
   my $mode = 0666;
   chmod $mode,"$c->{upload_dir}/$dx/$file->{file_code}";

   my $idir = $c->{htdocs_dir};
   $idir=~s/^(.+)\/.+$/$1\/i/;
   $mode = 0777;
   mkdir($idir,$mode) unless -d $idir;
   mkdir("$idir/$dx",$mode) unless -d "$idir/$dx";
   chmod $mode,"$idir/$dx";

   if($c->{m_i} && $file->{file_name_orig}=~/\.(jpg|jpeg|gif|png|bmp)$/i)
   {
      $file->{type}='image';
      my $ext = lc $1;
      &ResizeImg("$c->{upload_dir}/$dx/$file->{file_code}",$c->{m_i_width},$c->{m_i_height});
      rename("$c->{upload_dir}/$dx/$file->{file_code}_t.jpg","$idir/$dx/$file->{file_code}_t.jpg");
      $file->{new_size} = 1;
      if($c->{m_i_wm_image})
      {
         &WatermarkImg("$c->{upload_dir}/$dx/$file->{file_code}");
         $file->{file_size} = -s "$c->{upload_dir}/$dx/$file->{file_code}";
         $file->{file_name_orig}=~s/\.\w+$/\.jpg/;
         #rename("$idir/$dx/$file->{file_code}.$ext","$idir/$dx/$file->{file_code}.jpg") unless $ext eq 'jpg';
         $ext='jpg';
      }
      symlink("$c->{upload_dir}/$dx/$file->{file_code}", "$idir/$dx/$file->{file_code}.$ext") if $c->{m_i_hotlink_orig};
   }
   if($c->{m_v} && $file->{file_spec}=~/^V/)
   {
      $file->{type}='video';
      `mplayer $c->{upload_dir}/$dx/$file->{file_code} -ss 00:05 -vo jpeg:outdir=$c->{temp_dir}:quality=65 -nosound -frames 1 -slave -really-quiet -nojoystick -nolirc -nocache -noautosub`;
      if(-e "$c->{temp_dir}/00000001.jpg")
      {
       move("$c->{temp_dir}/00000001.jpg","$idir/$dx/$file->{file_code}.jpg");
      }
      else
      {
        symlink("$idir/default.jpg","$idir/$dx/$file->{file_code}.jpg");
      }
      `mplayer $c->{upload_dir}/$dx/$file->{file_code} -ss 00:05 -vf scale=200:-3 -vo jpeg:outdir=$c->{temp_dir}:quality=65 -nosound -frames 1 -slave -really-quiet -nojoystick -nolirc -nocache -noautosub`;
      if(-e "$c->{temp_dir}/00000001.jpg")
      {
       move("$c->{temp_dir}/00000001.jpg","$idir/$dx/$file->{file_code}_t.jpg");
      }
      else
      {
        symlink("$idir/default.jpg","$idir/$dx/$file->{file_code}_t.jpg");
      }
   }
   if($c->{m_h} && $c->{m_h_login} && $c->{m_h_password} && $file->{file_name_orig}=~/\.(avi|divx|xvid|mpg|mpeg|vob|mov|3gp|flv|mp4|wmv|mkv)$/i)
   {
      open(FILE,">>enc_hey.list");
      print FILE "$dx:$file->{file_code}\n";
      close FILE;
   }
   if($c->{m_e} && $file->{file_name_orig}=~/\.(avi|divx|xvid|mpg|mpeg|vob|mov|3gp|flv|mp4|wmv|mkv)$/i)
   {
      open(FILE,">>enc.list");
      print FILE "$dx:$file->{file_code}\n";
      close FILE;
   }
}

sub ResizeImg
{
   my ($file,$width_max,$height_max) = @_;
   $width_max||=150;
   $height_max||=150;
   eval { require GD; };
   return if $@;
   GD::Image->trueColor(1);
   my $image = GD::Image->new($file);
   return unless $image;
   my ($width,$height) = $image->getBounds();
   my $thumb;
   if($c->{m_i_resize}) # Cropped
   {
      my ($dx,$dy)=(0,0);
      if($width/$height >= $width_max/$height_max) ### Horizontal
      {
         $dx = sprintf("%.0f", ($width-$width_max*$height/$height_max)/2 );
      }
      else
      {
         $dy = sprintf("%.0f", ($height-$height_max*$width/$width_max)/2 );
      }
      $thumb = GD::Image->newTrueColor($width_max,$height_max);
      $thumb->copyResampled($image,0,0,$dx,$dy,$width_max,$height_max,$width-2*$dx,$height-2*$dy);
   }
   else
   {
      $image->transparent($image->colorAllocate(255,255,255));
      my $k_w = $width_max / $width;
      my $k_h = $height_max / $height;
      my $k = ($k_h < $k_w ? $k_h : $k_w);
      my $width1  = int(0.99+$width * $k);
      my $height1 = int(0.99+$height * $k);
      $thumb = GD::Image->new($width1,$height1);
      $thumb->copyResampled($image, 0,0,0,0, $width1, $height1, $width, $height);
   }
   
   my $jpegdata = $thumb->jpeg(70);
   $file=~s/\.(jpg|jpeg|gif|png|bmp)$//i;
   open(FILE,">$file\_t.jpg")||die"can't write th:$!";
   binmode FILE;
   print FILE $jpegdata;
   close(FILE);
}

sub WatermarkImg
{
   my ($file) = @_;
   return unless -f "$c->{cgi_dir}/$c->{m_i_wm_image}";
   eval { require GD; };
   return if $@;
   GD::Image->trueColor(1);
   my $image = GD::Image->new("$file");
   my $mark = GD::Image->new("$c->{cgi_dir}/$c->{m_i_wm_image}");
   return unless $image && $mark;
   my ($x,$y);
   my $dx=$c->{m_i_wm_padding};
   $c->{m_i_wm_position}||='nw';
   if($c->{m_i_wm_position} eq 'nw')
   {
      $x = $dx;
      $y = $dx;
   }
   elsif($c->{m_i_wm_position} eq 'n')
   {
      $x = int ($image->width-$mark->width)/2;
      $y = $dx;
   }
   elsif($c->{m_i_wm_position} eq 'ne')
   {
      $x = $image->width - $mark->width - $dx;
      $y = $dx;
   }
   elsif($c->{m_i_wm_position} eq 'w')
   {
      $x = $dx;
      $y = int ($image->height-$mark->height)/2;
   }
   elsif($c->{m_i_wm_position} eq 'c')
   {
      $x = int ($image->width-$mark->width)/2;
      $y = int ($image->height-$mark->height)/2;
   }
   elsif($c->{m_i_wm_position} eq 'e')
   {
      $x = $image->width - $mark->width - $dx;
      $y = int ($image->height-$mark->height)/2;
   }
   elsif($c->{m_i_wm_position} eq 'sw')
   {
      $x = $dx;
      $y = $image->height - $mark->height - $dx;
   }
   elsif($c->{m_i_wm_position} eq 's')
   {
      $x = int ($image->width-$mark->width)/2;
      $y = $image->height - $mark->height - $dx;
   }
   elsif($c->{m_i_wm_position} eq 'se')
   {
      $x = $image->width - $mark->width - $dx;
      $y = $image->height - $mark->height - $dx;
   }
   $image->copy($mark, $x, $y, 0, 0, $mark->width, $mark->height);
   open(FILE,">$file\_w")||die"can't write img:$!";
   print FILE $image->jpeg(85);
   close(FILE);
   rename("$file\_w",$file) if -f "$file\_w";
   unlink("$file\_w") if -f "$file\_w";
   undef $image;
}

sub logit
{
   my $msg = shift;
   return unless $c->{uploads_log};
   open(FILE,">>$c->{uploads_log}") || return;
   print FILE "$msg\n";
   close FILE;
}

1;
