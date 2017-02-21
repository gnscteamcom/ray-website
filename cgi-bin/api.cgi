#!/usr/bin/perl
use strict;
use lib '.';
use XFSConfig;
use CGI::Carp qw(fatalsToBrowser);
use CGI;
use File::Path;
use LWP::UserAgent;
use HTTP::Request::Common;
$HTTP::Request::Common::DYNAMIC_FILE_UPLOAD = 1;
use File::Copy;
use Digest::MD5;
#use XUpload;
#use POSIX qw( :signal_h :errno_h :sys_wait_h setsid );

die"Error1" unless $ENV{REQUEST_METHOD} eq 'POST';

my $q = CGI->new();
my $f;
$f->{$_}=$q->param($_) for $q->param;

&CompileChunks if $f->{op} eq 'compile';## && $ENV{HTTP_USER_AGENT} eq 'XFS-FSUploader';

&Send( "OK:0:ERROR: fs_key is wrong or not empty") if $f->{fs_key} ne $c->{fs_key};

&TransferFiles if $f->{op} eq 'transfer';


die"Error2" unless $ENV{HTTP_USER_AGENT} eq 'XFS-FSServer';

my $sub={
         gen_link       => \&GenerateLink,
         expire_sym     => \&ExpireSymlinks,
         del_files      => \&DeleteFiles,
         test           => \&Test,
         update_conf    => \&UpdateConfig,
         check_files    => \&CheckFiles,
         check_files_reverse  => \&CheckFilesReverse,
         get_file_stats => \&GetFileStats,
         import_list    => \&ImportList,
         import_list_do => \&ImportListDo,
         torrent_delete => \&TorrentDelete,
         torrent_kill   => \&TorrentKill,
         torrent_status => \&TorrentStatus,
         rar_password   => \&rarPasswordChange,
         rar_file_del   => \&rarFilesDelete,
         rar_file_extract => \&rarFilesExtract,
         transfer2      => \&TransferFiles2,
	}->{ $f->{op} };
if($sub)
{
   &$sub;
}
else
{
   die"Error4";
}


sub GenerateLink
{
   my $file_code = $f->{file_code};
   my $file_name = $f->{file_name};
   my $ip        = $f->{ip};
   my $dx = sprintf("%05d",$f->{file_id}/$c->{files_per_folder});
   &Send("ERROR:no_file") unless -f "$c->{upload_dir}/$dx/$file_code";
   my $x1 = int(rand(10));
   my $rand = &randchar(14);
   unless(-d "$c->{htdocs_dir}/$x1")
   {
      mkdir("$c->{htdocs_dir}/$x1") || &Send("ERROR:mkdir0");
      chmod 0777, "$c->{htdocs_dir}/$x1";
   }
   $rand="$x1/$rand";
   while(-d "$c->{htdocs_dir}/$rand"){$rand = &randchar(14);}
   mkdir("$c->{htdocs_dir}/$rand") || &Send("ERROR:mkdir");
   chmod 0777, "$c->{htdocs_dir}/$rand";
   symlink("$c->{upload_dir}/$dx/$file_code","$c->{htdocs_dir}/$rand/$file_name") || &Send("ERROR:sym_create_failed");

   if($ip)
   {
      open(FILE,">$c->{htdocs_dir}/$rand/.htaccess");
      $ip=~s/\./\\./g;
      $file_name=~s/\s/_/g;
      print FILE qq[RewriteEngine on\nRewriteCond %{REMOTE_ADDR} !^$ip\nRewriteRule ^.*\$ "$c->{site_url}/404.html?$c->{site_url}/$f->{file_code1}/$file_name.html"];
      close FILE;
   }

   &Send("OK:$rand");
}

sub ExpireSymlinks
{
   my $hours = $f->{hours};
   &daemonize;
   $|++;
   print"Content-type:text/html\n\n";
   for my $i (0..9)
   {
      next unless -d "$c->{htdocs_dir}/$i";
      opendir(DIR, "$c->{htdocs_dir}/$i") || next;
      my $time = time;
      while( defined(my $fn=readdir(DIR)) )
      {
         next if $fn =~ /^\.{1,2}$/;
         my $file = "$c->{htdocs_dir}/$i/$fn";
         my $ftime = (lstat($file))[9];
         next if ($time - $ftime) < 3600*$hours;
         if(-f $file)
         {
            unlink($file);
         }
         else
         {
            rmtree($file);
         }
         print"\n";
      }
      closedir(DIR);
   }
   print"OK";
   exit;
}

sub DeleteFiles
{
   my $list = $f->{list};
   &Send('OK') unless $list;
   &daemonize;
   $|++;
   print"Content-type:text/html\n\n";
   my @arr = split(/:/,$list);
   my $idir = $c->{htdocs_dir};
   $idir=~s/^(.+)\/.+$/$1\/i/;
   for my $x (@arr)
   {
      my ($file_id,$file_code)=split('-',$x);
      my $dx = sprintf("%05d",$file_id/$c->{files_per_folder});
      unlink("$c->{upload_dir}/$dx/$file_code") if -f "$c->{upload_dir}/$dx/$file_code";
      unlink <$idir/$dx/$file_code*>;
      print"\n";
   }
   print"OK";
   exit;
}

sub CheckFiles
{
   my $list = $f->{list};
   &Send('OK') unless $list;
   my @arr = split(/:/,$list);
   my @nofiles;
   for my $x (@arr)
   {
      my ($file_id,$file_code)=split('-',$x);
      my $dx = sprintf("%05d",$file_id/$c->{files_per_folder});
      push @nofiles,$file_code unless -f "$c->{upload_dir}/$dx/$file_code";
   }
   &Send("OK:".join ',',@nofiles );
}

sub CheckFilesReverse
{
   my $deleted=0;
   $|++;
   print"Content-type:text/html\n\n";
   print"Starting...";
   opendir(DIR, "$c->{upload_dir}") || &Send("Error:cant open upload_dir");
   foreach my $fn (readdir(DIR))
   {
      next if $fn =~ /^\.{1,2}$/;
      next unless -d "$c->{upload_dir}/$fn";
      next unless $fn=~/^\d{5}$/;
      opendir(DIR2, "$c->{upload_dir}/$fn")||next;
      my @arr;
      while( defined(my $fn2=readdir(DIR2)) )
      {
         next if $fn2 =~ /^\.{1,2}$/;
         push @arr, $fn2;
      }
      closedir(DIR2);
      my $ua = LWP::UserAgent->new(agent => "XFS-FSAgent",timeout => 360);
      my $res = $ua->post("$c->{site_cgi}/fs.cgi",
                          {
                             fs_key => $c->{fs_key},
                             op     => 'check_codes',
                             codes  => join(',',@arr),
                          }
                         );
      &Send("Error: fs bad answer: ".$res->content) unless $res->content=~/^OK/;
      my ($bad) = $res->content=~/^OK:(.+?)$/;
      for( split(/\,/,$bad) )
      {
         unlink("$c->{upload_dir}/$fn/$_");
         $deleted++;
      }
      print"+"
   }
   closedir(DIR);
   print"<br>Files removed from disk: $deleted<br><br>";
   exit;
}

sub GetFileStats
{
   opendir(DIR, "$c->{upload_dir}") || &Send("Error:cant open upload_dir");
   my ($files,$size)=(0,0);
   while( defined(my $fn=readdir(DIR)) )
   {
      next if $fn=~/^\.{1,2}$/ || !-d "$c->{upload_dir}/$fn";
      opendir(DIR2, "$c->{upload_dir}/$fn")||next;
      foreach my $fn2 (readdir(DIR2))
      {
         next if $fn2 =~ /^\.{1,2}$/;
         $files++;
         $size += -s "$c->{upload_dir}/$fn/$fn2";
      }
      closedir(DIR2);
   }
   &Send("OK:$files:$size");
}

sub ImportList
{
   opendir(DIR, "$c->{cgi_dir}/ImportFiles") || &Send("Error:cant open ImportFiles dir");
   my @arr;
   while( defined(my $fn=readdir(DIR)) )
   {
      next if $fn=~/^\.{1,2}$/;
      next unless -f "$c->{cgi_dir}/ImportFiles/$fn";
      push @arr, $fn.'-'.(-s "$c->{cgi_dir}/ImportFiles/$fn");
   }
   &Send("OK:".join(':',@arr));
}

sub ImportListDo
{
   my $usr_id = $f->{usr_id};
   my $pub    = $f->{pub};
   my $import_dir = "$c->{cgi_dir}/ImportFiles";
   opendir(DIR, $import_dir) || &Send("Error:cant open ImportFiles dir:$!");
   my $ua = LWP::UserAgent->new(keep_alive => 1,agent => "XFS-FSAgent",timeout => 180,);
   my $cx=0;
   require XUpload;
   while( defined(my $fn=readdir(DIR)) )
   {
      next if $fn=~/^\.{1,2}$/;
      next unless -f "$import_dir/$fn";

      my $file = {file_tmp=>"$import_dir/$fn", file_name_orig=>$fn, file_public=>$pub, usr_id=>$usr_id, no_limits=>1};
      $f->{ip}='1.1.1.1';
      # --------------------
      $file = &XUpload::ProcessFile($file,$f) unless $file->{file_status};
      # --------------------
      &Send("Error: $file->{file_status}") if $file->{file_status};

      $cx++;
   }
   &Send("OK:$cx");
}

sub Test
{
   my @tests;
   # Try to CHMOD first
   chmod 0777, $c->{temp_dir};
   chmod 0777, $c->{upload_dir};
   chmod 0777, $c->{htdocs_dir};
   chmod 0755, 'upload.cgi';
   chmod 0755, 'upload_status.cgi';
   chmod 0666, 'XFSConfig.pm';
   chmod 0666, 'logs.txt';

   # temp dir
   push @tests, -d $c->{temp_dir} ? 'temp dir exist: OK' : 'temp dir exist: ERROR';
   push @tests, mkdir("$c->{temp_dir}/test") ? 'temp dir mkdir: OK' : 'temp dir mkdir: ERROR';
   push @tests, rmdir("$c->{temp_dir}/test") ? 'temp dir rmdir: OK' : 'temp dir rmdir: ERROR';
   # url temp dir
   push @tests, -d $c->{htdocs_tmp_dir} ? 'tmp dir exist: OK' : 'tmp dir exist: ERROR';
   push @tests, mkdir("$c->{htdocs_tmp_dir}/test") ? 'tmp dir mkdir: OK' : 'tmp dir mkdir: ERROR';
   push @tests, rmdir("$c->{htdocs_tmp_dir}/test") ? 'tmp dir rmdir: OK' : 'tmp dir rmdir: ERROR';
   # upload dir
   push @tests, -d $c->{upload_dir} ? 'upload dir exist: OK' : 'upload dir exist: ERROR';
   push @tests, mkdir("$c->{upload_dir}/test") ? 'upload dir mkdir: OK' : 'upload dir mkdir: ERROR';
   push @tests, rmdir("$c->{upload_dir}/test") ? 'upload dir rmdir: OK' : 'upload dir rmdir: ERROR';
   # htdocs dir
   push @tests, -d $c->{htdocs_dir} ? 'htdocs dir exist: OK' : 'htdocs dir exist: ERROR';
   push @tests, mkdir("$c->{htdocs_dir}/test") ? 'htdocs dir mkdir: OK' : 'htdocs dir mkdir: ERROR';
   push @tests, symlink("upload.cgi","$c->{htdocs_dir}/test/test.avi") ? 'htdocs dir symlink: OK' : 'htdocs dir symlink: ERROR';
   push @tests, unlink("$c->{htdocs_dir}/test/test.avi") ? 'htdocs dir symlink del: OK' : 'htdocs dir symlink del: ERROR';
   push @tests, rmdir("$c->{htdocs_dir}/test") ? 'htdocs dir rmdir: OK' : 'htdocs dir rmdir: ERROR';
   # XFSConfig.pm
   push @tests, open(F,'XFSConfig.pm') ? 'config read: OK' : 'config read: ERROR';
   push @tests, open(F,'>>XFSConfig.pm') ? 'config write: OK' : 'config write: ERROR';

   my $site_cgi = $f->{site_cgi};
   my $ua = LWP::UserAgent->new(agent => "XFS-FSAgent",timeout => 90);
   my $res = $ua->post("$site_cgi/fs.cgi",
                       {
                          op => 'test'
                       }
                      );
   push @tests, $res->content =~ /^OK/ ? 'fs.cgi: OK' : 'fs.cgi: ERROR '.$res->content;
   my ($ip) = $res->content =~ /^OK:(.*)/;
   
   &Send( "OK:$ip:".join('|',@tests) );
}

sub UpdateConfig
{
   my $str = $f->{data};
   my $cc;
   for(split(/\~/,$str))
   {
      /^(.+?):(.*)$/;
      $cc->{$1}=$2;
   }

   my $conf;
   open(F,"$c->{cgi_dir}/XFSConfig.pm")||&Send("Can't read Config");
   $conf.=$_ while <F>;
   close F;

   for my $x (keys %{$cc})
   {
      my $val = $cc->{$x};
      $conf=~s/$x\s*=>\s*(\S+)\s*,/"$x => '$val',"/e;
   }
   open(F,">$c->{cgi_dir}/XFSConfig.pm")||&Send("Can't write Config");
   print F $conf;
   close F;

   $conf='';
   open(F,"$c->{htdocs_dir}/.htaccess");
   $conf.=$_ while <F>;
   close F;
   $conf=~s/ErrorDocument 404 .+/"ErrorDocument 404 $cc->{site_url}\/404.html"/e;
   open(F,">$c->{htdocs_dir}/.htaccess");
   print F $conf;
   close F;

   &Send('OK');
}

sub CompileChunks
{
   my $fname = $f->{fname};
   my $sid = $f->{sid};
   my $sess_id = $f->{session_id};

   &SendXML("<Error>Upload session expired</Error>") unless -e "$c->{temp_dir}/$sid";
   my $cx=0;
   open(F, ">$c->{temp_dir}/$sid/result") || &SendXML("<Error>Can't create result file</Error>");
   my $buf;
   $|++;
   print"Content-type:text/html\n\n";
   while(-f "$c->{temp_dir}/$sid/file_$cx")
   {
      open(my $fh,"$c->{temp_dir}/$sid/file_$cx") || &SendXML("<Error>Can't open chunk</Error>");
      print F $buf while read($fh, $buf, 4096);
      close $fh;
      unlink("$c->{temp_dir}/$sid/file_$cx");
      $cx++;
      print"\#\n";
   }
   close F;
   print("<Error>No chunks were found</Error>"),exit unless $cx;

   open(FILE,"$c->{temp_dir}/$sid/result");
   my $data;
   read(FILE,$data,4096);
   seek(FILE,-4096,2);
   read(FILE,$data,4096,4096);
   my $md5 = Digest::MD5::md5_base64 $data;

   my $ua = LWP::UserAgent->new(agent => "XFS-FSAgent",timeout => 180);
   my $res=$ua->post("$c->{site_cgi}/fs.cgi",
                      {file_name   => $fname,
                       file_size    => -s "$c->{temp_dir}/$sid/result",
                       sess_id      => $sess_id,
                       file_ip      => $ENV{REMOTE_ADDR},
                       fs_key       => $c->{fs_key},
                       file_md5     => $md5,
                       compile      => 1,
                       }
                      );
   my ($file_id,$file_code,$file_real,$msg) = $res->content=~/^(\d+):(\w+):(\w+):(.*)$/;
   #print $res->content;
   print("<Error>".$res->content."</Error>"),exit unless $msg=~/^OK/;
   my ($link,$del_link) = $msg=~/^OK=(.+?)\|(.+)$/;
   print("<Error>Can't generate link</Error>"),exit unless $link;
   my $dx = sprintf("%05d",$file_id/$c->{files_per_folder});
   unless(-d "$c->{upload_dir}/$dx")
   {
      my $mode = 0777;
      mkdir("$c->{upload_dir}/$dx",$mode);
      chmod $mode,"$c->{upload_dir}/$dx";
   }
   move("$c->{temp_dir}/$sid/result","$c->{upload_dir}/$dx/$file_code")||&SendXML("<Error>Can't move result:$!</Error>");
   rmdir("$c->{temp_dir}/$sid");
   print("<Links><Link>$link</Link>\n<DelLink>$del_link</DelLink></Links>");
   exit;
}

sub TorrentDelete
{
   print"Content-type:text/html\n\n";
   my $ua = LWP::UserAgent->new(timeout=>15);
   my $res = $ua->get("http://$c->{bitflu_address}/cancel/$f->{sid}")->content;
   $ua->get("http://$c->{bitflu_address}/history/forget/$f->{sid}");
   print $res ? $res : "OK";
   exit;
}

sub TorrentKill
{
   `kill -9 \`cat Torrents/bitflu.pid\``;
   #`killall bitflu.pl`;
   print"Content-type:text/html\n\nOK";
   exit;
}

sub TorrentStatus
{
   my $ua = LWP::UserAgent->new(timeout=>15);
   my $stat = $ua->get("http://$c->{bitflu_address}/stats")->content;
   print"Content-type:text/html\n\n";
   print $stat=~/sent/ ? 'ON' : '';
   exit;
}

sub TransferFiles
{
  $|++;
  my $idir = $c->{htdocs_dir};
  $idir=~s/^(.+)\/.+$/$1\/i/;
  print"Content-type:text/html\n\n";
  print"<HTML><BODY style='font: 12px Arial'>\n";
  print "<!--xxx-->\n"x50;
  for(split(/\|/,$f->{files}))
  {
     my ($file_id,$code) = split(/:/,$_);
     my $dx = sprintf("%05d",$file_id/$c->{files_per_folder});
     unless(-f "$c->{upload_dir}/$dx/$code"){print"No file $dx/$code<br>\n";next;}
     my $h;
     my ($ext) = join('',<$idir/$dx/$code.*>)=~/\.(\w+)$/;
     if(-f "$idir/$dx/$code\_t.jpg")
     {
        $h = [dx=>$dx,file1=>["$c->{upload_dir}/$dx/$code"],file2=>["$idir/$dx/$code\_t.jpg"],ext=>$ext];
     }
     else
     {
        $h = [dx=>$dx,file1=>["$c->{upload_dir}/$dx/$code"]];
     }
     print"Sending $dx/$code...";
     my $ua = LWP::UserAgent->new(agent=>"XFS-FSAgent",timeout=>300);
     my $req = POST "$f->{srv_cgi_url2}/uu.cgi", Content_Type => 'form-data', Content => $h, fs_key=>$f->{fs_key2};
     #my $gen = $req->content();
     #$req->content( sub {my $chunk = &$gen();return $chunk;} );
     my $res = $ua->request($req);
     print $res->content,"\n";
     next unless $res->content eq 'OK';

     $res=$ua->post("$c->{site_cgi}/fs.cgi",
                       {
                         op         => 'update_srv',
                         fs_key     => $c->{fs_key},
                         file_real  => $code,
                         srv_id     => $f->{srv_id2},
                       }
                      );
     print "  DB:".$res->content."<br>\n";
     if($res->content eq 'OK')
     {
        unlink("$c->{upload_dir}/$dx/$code");
        unlink("$idir/$dx/$code\_t.jpg");
        unlink("$idir/$dx/$code.$ext");
     }
  }
  print"All Done.";
  exit;
}

sub TransferFiles2
{
  $|++;
  my $idir = $c->{htdocs_dir};
  print"Content-type:text/html\n\n";
  my ($file_id,$code) = ($f->{file_id},$f->{file_code});
  my $dx = sprintf("%05d",$file_id/$c->{files_per_folder});
  print("No file $c->{upload_dir}/$dx/$code"),exit unless -f "$c->{upload_dir}/$dx/$code";
  my $h = [dx=>$dx,file1=>["$c->{upload_dir}/$dx/$code"]];
  my $ua = LWP::UserAgent->new(agent=>"XFS-FSAgent",timeout=>300);
  my $req = POST "$f->{srv_cgi_url2}/uu.cgi", Content_Type => 'form-data', Content => $h, fs_key=>$f->{fs_key2};
  #my $gen = $req->content();
  #$req->content( sub {my $chunk = &$gen();return $chunk;} );
  my $res = $ua->request($req)->content;
  if($res eq 'OK')
  {
     unlink("$c->{upload_dir}/$dx/$code");
  }
  print $res;
  exit;
}

sub rarPasswordChange
{
  require XUpload;
  my $dx = sprintf("%05d",$f->{file_id}/$c->{files_per_folder});
  my $file_code = $f->{file_code};

  my $res1 = `rar x -ow $c->{upload_dir}/$dx/$file_code $c->{upload_dir}/$dx/rar_$file_code/ -p"$f->{rar_pass}"`;
  #my $pass=qq[-p"$f->{}"]
  `rar a -ow $c->{upload_dir}/$dx/$file_code.rar -ep1 -df $c->{upload_dir}/$dx/rar_$file_code/*`;
  rmtree("$c->{upload_dir}/$dx/rar_$file_code");

  rename("$c->{upload_dir}/$dx/$file_code.rar","$c->{upload_dir}/$dx/$file_code") if -f "$c->{upload_dir}/$dx/$file_code.rar";

  my $file_spec = &XUpload::rarGetInfo("$c->{upload_dir}/$dx/$file_code");
  &Send($file_spec);
}

sub rarFilesDelete
{
  require XUpload;
  my $dx = sprintf("%05d",$f->{file_id}/$c->{files_per_folder});
  my $file_code = $f->{file_code};
  my $pass=qq[ -p"$f->{rar_pass}"] if $f->{rar_pass};
  #die qq[rar d $c->{upload_dir}/$dx/$file_code "$f->{files}"$pass];
  chdir("$c->{upload_dir}/$dx");
  `rar d -ow $c->{upload_dir}/$dx/$file_code $f->{files}$pass`;
  my $file_spec = &XUpload::rarGetInfo("$c->{upload_dir}/$dx/$file_code");
  &Send($file_spec);
}

sub rarFilesExtract
{
  require XUpload;
  my $dx = sprintf("%05d",$f->{file_id}/$c->{files_per_folder});
  my $file_code = $f->{file_code};
  my $pass=qq[ -p"$f->{rar_pass}"] if $f->{rar_pass};
  chdir("$c->{upload_dir}/$dx");
  mkdir("$c->{upload_dir}/$dx/rar_$file_code/");
  `rar x -ep -ow $c->{upload_dir}/$dx/$file_code $c->{upload_dir}/$dx/rar_$file_code/ $f->{files}$pass`;

  my $dir="$c->{upload_dir}/$dx/rar_$file_code";
  opendir(DIR, $dir) || &Send("Error:cant open $dir:$!");;
  while( defined(my $fn=readdir(DIR)) )
  {
     next if $fn=~/^\.{1,2}$/;
     next unless -f "$dir/$fn";

     my $file = {file_tmp=>"$dir/$fn", file_name_orig=>$fn, file_public=>1, usr_id=>$f->{usr_id}};
     $f->{ip}='1.1.1.1';
     # --------------------
     $file = &XUpload::ProcessFile($file,$f);
     # --------------------
     &Send("Error: $file->{file_status}") if $file->{file_status};
  }
  rmtree($dir);
  &Send("OK");
}

########################
sub Send
{
   my $txt = shift;
   print"Content-type:text/html\n\n";
   print $txt;
   exit;
}

sub SendXML
{
   print"Content-type:text/html\n\n",shift;
   exit;
}

sub randchar
{ 
   my @range = ('0'..'9','a'..'z');
   my $x = int scalar @range;
   join '', map $range[rand $x], 1..shift||1;
}

sub daemonize
{
    #chdir '/'                 or die "Can't chdir to /: $!";
    #close STDIN               or die "Can't close STDIN: $!";
    defined( my $pid = fork ) or die "Can't fork: $!";
    print("Content-type:text/html\n\nOK"),exit if $pid;
    #setsid                    or die "Can't start a new session: $!";
    close STDOUT              or die "Can't close STDOUT: $!";
    $SIG{CHLD} = 'IGNORE';
}

