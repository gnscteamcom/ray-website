#!/usr/bin/perl
### SibSoft.net ###
use strict;
use lib '.';
use XFSConfig;
use XUpload;

use CGI::Carp qw(fatalsToBrowser);
use CGI;
use Fcntl ':flock';
use LWP::UserAgent;
use HTTP::Cookies;
use HTML::Form;
use Encode;
$|++;

print("Content-type:text/html\n\nXFS"),exit if $ENV{QUERY_STRING}=~/mode=test/;

my ($utype) = $ENV{QUERY_STRING}=~/utype=([a-z]+)/;
$utype||='anon';
$c->{$_}=$c->{"$_\_$utype"} for qw(enabled max_upload_files max_upload_filesize remote_url);

my ($upload_type) = $ENV{QUERY_STRING}=~/upload_type=([a-z]+)/;
my $url_mode=1 if $upload_type eq 'url';
my $IP = &GetIP;
my $start_time = time;

&logit("Starting upload. Size: $ENV{'CONTENT_LENGTH'}");
my ($sid) = ($ENV{QUERY_STRING}=~/upload_id=(\d+)/); # get the random id for temp files
$sid ||= join '', map int rand 10, 1..7;         # if client has no javascript, generate server-side
unless($sid=~/^\d+$/) # Checking for invalid IDs (hacker proof)
{
   &xmessage("ERROR: Invalid Upload ID");
}
my $temp_dir = "$c->{temp_dir}/$sid";
my $mode = 0777;
mkdir $temp_dir, $mode;
chmod $mode,$temp_dir;

$CGITempFile::TMPDIRECTORY = $temp_dir;

my @urls;
my ($total_size,$buff_size,$buf,$fname_old,$current_bytes,$speed,$buff_old,$time,$time_spent,$total_old,$fname,$fname2,$base_old,$nosize);
my ($old_size,$old_time);
my $files_uploaded = 0;
my $time_start = $old_time = time;

$c->{ip_not_allowed}=~s/\./\\./g;
if( $c->{ip_not_allowed} && $IP=~/$c->{ip_not_allowed}/ )
{
   &DelData($temp_dir);
   &xmessage("ERROR: $c->{msg}->{ip_not_allowed}");
}
if(!$c->{enabled})
{
   &DelData($temp_dir);
   &xmessage("ERROR: Uploads not enabled for this type of users");
}
if($c->{srv_status} ne 'ON')
{
   &DelData($temp_dir);
   &xmessage("ERROR: Server don't allow uploads at the moment");
}
if($c->{max_upload_filesize} && $ENV{CONTENT_LENGTH} > 1048576*$c->{max_upload_filesize}*$c->{max_upload_files})
{
   &DelData($temp_dir);
   &xmessage("ERROR: $c->{msg}->{file_size_big}$c->{max_upload_filesize} Mb");
}

my $cg;
my $accs;

if($url_mode)
{
   print"Content-type: text/html\n\n";
   unless($c->{remote_url})
   {
      &DelData($temp_dir);
      &xmessage("ERROR: You can't use remote URL upload");
   }
   $cg = CGI->new();
   require HTTP::Request;
   my $ua = LWP::UserAgent->new(timeout => 90,
                                agent   => 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 (.NET CLR 3.5.30729)',
                                cookie_jar => HTTP::Cookies->new( hide_cookie2 => 1, ignore_discard => 1 ) );
   my @url_list;
   my $rslee=1 if $cg->param("up1oad_type") eq 'url' && $c->{"\x6d\x5f\x72"};

   
   #for('m_r','mu','nl','hf')
   #{
   #   #push @{$accs->{"$_\_logins"}}, &shuffle(split(/\|/,$c->{"$_\_logins"}));
   #   push @{$accs->{"$_\_logins"}}, split(/\|/,$c->{"$_\_logins"});
   #}

   my $url_mass = $cg->param("url_mass");
   $url_mass=~s/\r//gs;

   for my $url (split(/\n/,$url_mass))
   {
      next unless $url;
      next unless $url=~/:\/\//;
      my $u = {url => $url};
      ($u->{file_name_orig}) = $u->{url}=~/^.*\/([^\/]*)$/;
      $u->{file_name_orig}=~s/\?//g;

      ($u->{auth_login},$u->{auth_password})=($1,$2) if $u->{url}=~s/\/\/(.+?)\:(.+?)\@/\/\//;

      $u->{rslee}=$rslee;

      $u->{no_hdr}=1 
         if $u->{url}=~/(megaupload\.com|netload\.in|mediafire\.com|4shared\.com|2share\.com|depositfiles\.com|filefactory\.com|easy-share\.com|filesonic\.com|uploading\.com|fileserve\.com)/i;

      if($u->{url}=~/^ftp/i)
      {
         require Net::FTP;
         my ($serv,$path,$file)=$u->{url}=~m#^ftp://([^/]+)(.*)/([^/]+)$#i;
         my $ftp = Net::FTP->new($serv)||die $!;
         $ftp->login($u->{auth_login},$u->{auth_password})||die $ftp->message;
         if($path){$ftp->cwd($path)||die $ftp->message;}
         if($ftp->supported("STAT"))
         {
            $ftp->_STAT($file);
            my @msg=$ftp->message;
            for(@msg){s/^\s+//;$u->{file_size}=(split(/\s+/,$_))[4] if /^[-rwxSsTt]{10}/;}
         }
         unless($u->{file_size})
         {
            my @files = $ftp->dir($file);
            $files[0]=~s/^\s+//;
            $u->{file_size} = (split(/\s+/,$1))[4] if $files[0]=~/^([-rwxSsTt]{10}.*)$/;
         }
         
         $u->{url}=~s/ftp:\/\///i;
         $u->{url} = "ftp://$u->{auth_login}:$u->{auth_password}\@$u->{url}";
         $u->{auth_login}=$u->{auth_password}='';
         #$u->{file_size}=$ftp->size($file);
      }
      elsif(!$u->{no_hdr})
      {
         my $request  = HTTP::Request->new( HEAD => $u->{url} );
         my $response = $ua->request( $request );
         $u->{file_size} = $response->content_length;
         $u->{file_name_orig}=$1 if $response->header('Content-Disposition')=~/filename=(.+)/i;
      }
      
      
      if($c->{max_upload_filesize} && $u->{file_size} > $c->{max_upload_filesize}*1048576)
      {
         $u->{file_error}="$c->{msg}->{file_size_big}";
         push @urls, $u;
         next;
      }
      if(scalar(@urls)>=$c->{max_upload_files})
      {
         $u->{file_error}="$u->{file_name_orig} $c->{msg}->{too_many_files}";
         push @urls, $u;
         next;
      }
      $total_size+=$u->{file_size};
      $u->{file_tmp} = "$temp_dir/".join('', map int rand(10), 1..10);
      push(@urls, $u);
   }

   my $str=qq[new Object({"state":"uploading", "size":"$total_size", "received":"0","files_done":"0"})];
   open(F,">$c->{htdocs_tmp_dir}/$sid.html");
   print F $str;
   close F;
   my $mode = 0777;
   chmod $mode,"$c->{htdocs_tmp_dir}/$sid.html";

   unless($rslee)
   {
      for(qw(rs mu nl hf mf fs df ff es sm ug fe))
      {
         $c->{"my_$_\_logins"}=$cg->param("$_\_logins");
      }
   }
   #die $c->{"rs_logins"};
   for my $u (@urls)
   {
      down:
      if($u->{file_error}){ $files_uploaded++; next; }
      
      $u=preMegaupload($u,$ua,$c->{mu_logins})
         if $u->{url}=~/megaupload\.com/i;
      $u=preMediafire($u,$ua,$c->{mf_logins})
         if $u->{url}=~/mediafire\.com/i;
      $u=pre4shared($u,$ua,$c->{fs_logins})
         if $u->{url}=~/4shared\.com/i;
      $u=pre2shared($u,$ua)
         if $u->{url}=~/2shared\.com/i;
      $u=preDepositfiles($u,$ua,$c->{df_logins})
         if $u->{url}=~/depositfiles\.com/i;
      $u=preUploading($u,$ua,$c->{ug_logins})
         if $u->{url}=~/uploading\.com/i;
      $u=preFileserve($u,$ua,$c->{fe_logins})
         if $u->{url}=~/fileserve\.com/i;
      $u=preFilesonic($u,$ua,$c->{sm_logins})
         if $u->{url}=~/filesonic\.com/i;

      $u=preBasicAuth($u,$ua,'rs_logins')
         if $u->{url}=~/rapidshare\.com/i;
      $u=preBasicAuth($u,$ua,'nl_logins')
         if $u->{url}=~/netload\.in/i;
      $u=preBasicAuth($u,$ua,'hf_logins')
         if $u->{url}=~/hotfile\.com/i;
      $u=preBasicAuth($u,$ua,'ff_logins')
         if $u->{url}=~/filefactory\.com/i;
      $u=preBasicAuth($u,$ua,'es_logins')
         if $u->{url}=~/easy-share\.com/i;
      
      if($u->{file_error}){ $files_uploaded++; next; }      

      $nosize = $u->{file_size} ? 0 : 1;
      $base_old='';
      open FILE, ">$u->{file_tmp}" || die"Can't open dest file:$!";
      my $req = HTTP::Request->new(GET => $u->{url});
      $req->authorization_basic($u->{auth_login},$u->{auth_password}) if $u->{auth_login} && $u->{auth_password};
      my $resp = $ua->request($req, \&hook_url );
      close FILE;
      $u->{file_size}=-s $u->{file_tmp};
      $u->{file_name_orig}||=$fname2;
      $u->{file_name_orig}=~s/.+\/(.+)$/$1/;
      $u->{file_name_orig}=~s/\.html?$//i;
      $u->{file_name_orig}=~s/\?.*$//;
      $u->{file_name_orig}=~s/\?+//g;
      $u->{file_name_orig}=~s/\/$//g;
      $u->{file_name_orig}||=join('', map int rand(10), 1..5);

      if($u->{rslee} && $ua->{auth_login} && $resp->content_type eq 'text/html')
      {
         $u->{auth_login}=$u->{auth_password}=$ua->{auth_login}=$ua->{auth_password}='';
         goto down;
      }

      $u->{file_error}="Received HTML page instead of file" if $resp->content_type eq 'text/html' && $u->{url}!~/\.html$/i;
      $u->{file_error}="File download failed:".$resp->status_line unless $resp->is_success;

      $files_uploaded++;
   }
}
else
{
   $total_size = $ENV{CONTENT_LENGTH};
   my $str=qq[new Object({"state":"uploading", "size":"$total_size", "received":"0","files_done":"0"})];
   open(F,">$c->{htdocs_tmp_dir}/$sid.html");
   print F $str;
   close F;
   my $mode = 0777; chmod $mode,"$c->{htdocs_tmp_dir}/$sid.html";
   $cg = CGI->new(\&hook);
}

#########################
sub hook_url
{
  my ($buffer,$res) = @_;
  print FILE $buffer;
  $current_bytes+=length($buffer);
  
  if(time>$old_time)
  {
     $total_size += $res->content_length if $nosize && $base_old ne $res->base;
     $base_old = $res->base;
     $fname2 = $res->base;
     $old_time = time;
     my $str=qq[new Object({"state":"uploading", "size":"$total_size", "received":"$current_bytes","files_done":"$files_uploaded"})];
     open(F,">$c->{htdocs_tmp_dir}/$sid.html");
     print F $str;
     close F;
     print"<!--x-->\n" if $url_mode && $time%5==0;
  }
}
#########################
sub hook
{
  ($fname, $buf, undef) = @_;

  $current_bytes+=length($buf);

  if($fname_old ne $fname)
  {
     $files_uploaded++ if $fname_old;
     $fname_old=$fname;
  }

  if(time>$old_time)
  {
     $old_time = time;
     my $str=qq[new Object({"state":"uploading", "size":"$total_size", "received":"$current_bytes","files_done":"$files_uploaded"})];
     open(F,">$c->{htdocs_tmp_dir}/$sid.html");
     print F $str;
     close F;
  }
}

$files_uploaded++;
my $str=qq[new Object({"state":"done", "size":"$total_size", "received":"$total_size","files_done":"$files_uploaded"})];
open(F,">$c->{htdocs_tmp_dir}/$sid.html");
print F $str;
close F;

#########################

my $f;
$f->{$_}=$cg->param($_) for $cg->param();
$f->{ip} = &GetIP();
$f->{torr_on}=1 if $f->{up1oad_type} eq 'tt';

my (@file_inputs,@files);
if($url_mode)
{
   @file_inputs = @urls;
}
else
{
   for( $cg->param() )
   {
      next unless my $up=$cg->upload($_);
      my $u;
      ($u->{file_name_orig})=$cg->uploadInfo($up)->{'Content-Disposition'}=~/filename="(.+?)"/i;
      $u->{file_name_orig}=~s/^.*\\([^\\]*)$/$1/;
      $u->{file_size}   = -s $up;
      $u->{file_descr}  = $f->{"$_\_descr"};
      $u->{file_public} = $f->{"$_\_public"};
      $u->{file_tmp}    = $cg->tmpFileName($up);
      push @file_inputs, $u;
   }
}

for my $file ( @file_inputs )
{
   $file->{file_status}="null filesize or wrong file path"
      if $file->{file_size}==0;

   $file->{file_status}="filesize too big"
      if $c->{max_upload_filesize} && $file->{file_size}>$c->{max_upload_filesize}*1048576;

   $file->{file_status}="too many files"
      if $#files>=$c->{max_upload_files}-1;

   $file->{file_status}=$file->{file_error}
      if $file->{file_error};

   # --------------------
   $file = &XUpload::ProcessFile($file,$f) unless $file->{file_status};
   # --------------------

   $file->{file_status}||='OK';
   push @files, $file;
}


#sleep 1; ### Pause to sync messages with progress
&DelData($temp_dir);
unlink("$c->{htdocs_tmp_dir}/$sid.html");
&DeleteExpiredFiles( $c->{temp_dir}, 86400 );
&DeleteExpiredFiles( $c->{htdocs_tmp_dir}, 300, 'access');

# Generate parameters array for POST
my @har;
my $style=1;
for my $ff (@files)
{
   $style^=1;
   $ff->{file_descr}=~s/>/&gt;/g;
   $ff->{file_descr}=~s/</&lt;/g;
   $ff->{file_descr}=~s/"/&quote;/g;
   $ff->{file_descr}=substr($ff->{file_descr},0,128);
   push @har, { name=>"fn", 'value'=>$ff->{file_code}||$ff->{file_name_orig} };
   push @har, { name=>"st", 'value'=>$ff->{file_status} };
}

### Sending data to MAIN
my $url_post = "$c->{site_url}/";
push @har, { name=>'op', value=>'upload_result' };
for(qw(link_rcpt xbg xtxt))
{
   push @har, { name=>$_, value=>$cg->param($_) } if $cg->param($_);
}

if($ENV{QUERY_STRING}!~/js_on=1/)
{
  $url_post.='?';
  $url_post.="\&$_->{name}=$_->{value}" for @har;
  print $cg->redirect( $url_post );
  exit;
}

my $box="box" if $ENV{QUERY_STRING}=~/box=1/;
print"Content-type: text/html\n\n" unless $url_mode;
print"<HTML><BODY><Form name='F1' action='$c->{site_url}/$box' target='_parent' method='POST'>";
print"<textarea name='$_->{name}'>$_->{value}</textarea>" for @har;
print"</Form><Script>document.location='javascript:false';document.F1.submit();</Script></BODY></HTML>";
exit;

#############################################

sub shuffle (@) {
  my @a=\(@_);
  my $n;
  my $i=@_;
  map {
    $n = rand($i--);
    (${$a[$n]}, $a[$n] = $a[$i])[0];
  } @_;
}

sub DeleteExpiredFiles
{
   my ($dir,$lifetime,$access) = @_;
   return unless $lifetime;
   opendir(DIR, $dir) || &xmessage("Fatal Error: Can't opendir temporary folder ($dir)($!)");
   foreach my $fn (readdir(DIR))
   {
      next if $fn =~ /^\./;
      next if $fn eq 'status.html';
      my $file = $dir.'/'.$fn;
      my $ftime = $access ? (lstat($file))[8] : (lstat($file))[9];
      next if (time - $ftime) < $lifetime;
      -d $file ? &DelData($file) : unlink($file);
   }
   closedir(DIR);
}

sub DelData
{
   my ($dir) = @_;
   $cg->DESTROY if $cg; # WIN: unlock all files
   return unless -d $dir;
   opendir(DIR, $dir) || return;
   unlink("$dir/$_") for readdir(DIR);
   closedir(DIR);
   rmdir("$dir");
}

sub xmessage
{
   my ($msg) = @_;
   &lmsg($msg);
   $msg=~s/'/\\'/g;
   $msg=~s/<br>/\\n/g;
   print"Content-type: text/html\n\n";
   print"<HTML><HEAD><Script>alert('$msg');</Script></HEAD><BODY><b>$msg</b></BODY></HTML>";
   exit;
}

sub lmsg
{
   my $msg = shift;
   open(F,">$c->{htdocs_tmp_dir}/$sid.html");
   print F qq[new Object({"state":"error", "msg":"$msg"})];
   close F;
   &logit($msg);
}

sub logit
{
   my $msg = shift;
   return unless $c->{uploads_log};
   my @t = &getTime;
   open(FILE,">>$c->{uploads_log}") || return;
   print FILE $IP." $t[0]-$t[1]-$t[2] $t[3]:$t[4]:$t[5] $msg\n";
   close FILE;
}

sub getTime
{
    my @t = localtime();
    return ( sprintf("%04d",$t[5]+1900),
             sprintf("%02d",$t[4]+1), 
             sprintf("%02d",$t[3]), 
             sprintf("%02d",$t[2]), 
             sprintf("%02d",$t[1]), 
             sprintf("%02d",$t[0]) 
           );
}

sub GetIP
{
 return $ENV{REMOTE_ADDR};
}

sub preBasicAuth
{
   my ($u,$ua,$acc_name) = @_;
   
   $u->{auth_login}||=$ua->{auth_login};
   $u->{auth_password}||=$ua->{auth_password};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_$acc_name"}=~/^(.+):(.+)$/ if $c->{"my_$acc_name"};

   if($u->{rslee} && !($u->{auth_login} && $u->{auth_password}))
   {
      my @acc = shuffle(split(/\|/,$c->{$acc_name}));
      $u->{accs}||=\@acc;
      ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      unless($u->{auth_login} && $u->{auth_password})
      {
         $u->{file_error}="Can not leech file";
         $ua->{auth_login}=$ua->{auth_password}='';
         return $u;
      }
      ($ua->{auth_login},$ua->{auth_password}) = ($u->{auth_login},$u->{auth_password});
   }
   return $u;
}

sub preMegaupload
{
   my ($u,$ua,$accs) = @_;
   $u->{url}=~s/\/\/megaupload/\/\/www.megaupload/i;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_mu_logins"}=~/^(.+):(.+)$/ if $c->{"my_mu_logins"};

   while(!$ua->{mu_logged})
   {
      unless($u->{auth_login} && $u->{auth_password})
      {
         last unless $u->{rslee};
         ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      }

      my $res = $ua->get('http://www.megaupload.com/?c=login');
      my @forms = HTML::Form->parse($res);
      my $form = $forms[0];
      $form->value(username => $u->{auth_login});
      $form->value(password => $u->{auth_password});
      $res = $ua->request($form->click);
   
      unless($res->content=~/c=account"/)
      {
         if($u->{rslee})
         {
            ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
            next if $u->{auth_login} && $u->{auth_password};
         }
         $u->{file_error}="Can not leech megaupload file";
         return $u;
      }
      $ua->{mu_logged}=1;      
   }

   $u->{auth_login}=$u->{auth_password}='';
   $u->{file_name_orig}='';
   return $u;
}

sub preMediafire
{
   my ($u,$ua,$accs) = @_;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_mf_logins"}=~/^(.+):(.+)$/ if $c->{"my_mf_logins"};

   while(!$ua->{mf_logged})
   {
      unless($u->{auth_login} && $u->{auth_password})
      {
         last unless $u->{rslee};
         ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      }

      my $res = $ua->get('http://www.mediafire.com/');
      my @forms = HTML::Form->parse($res);
      my $form = $forms[0];
      $form->value('login_email' => $u->{auth_login});
      $form->value('login_pass'  => $u->{auth_password});
      #$form->value('login_remember' => 'On');
      $res = $ua->request($form->click);
      $res = $ua->get('http://www.mediafire.com/myaccount.php');
      #print $res->content;exit;
      unless($res->content=~/customize\.php/i)
      {
         if($u->{rslee})
         {
            ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
            next if $u->{auth_login} && $u->{auth_password};
         }
         
         $u->{file_error}="Can not leech mediafire file";
         return $u;
      }
      $ua->{mf_logged}=1;      
   }

   $u->{auth_login}=$u->{auth_password}='';
   $u->{file_name_orig}='';
   return $u;
}

sub preFilesonic
{
   my ($u,$ua,$accs) = @_;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_sm_logins"}=~/^(.+):(.+)$/ if $c->{"my_sm_logins"};

   while(!$ua->{sm_logged})
   {
      unless($u->{auth_login} && $u->{auth_password})
      {
         last unless $u->{rslee};
         ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      }
      #die"($u->{auth_login})($u->{auth_password})";
      my $res = $ua->get('http://www.filesonic.com/en/user/login');
      my @forms = HTML::Form->parse($res);
      my $form = $forms[0];
      $form->value('email'    => $u->{auth_login});
      $form->value('password' => $u->{auth_password});
      $res = $ua->request($form->click);

      #print $res->content;exit;

      if($res->content=~/rememberMe/i)
      {
         if($u->{rslee})
         {
            ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
            next if $u->{auth_login} && $u->{auth_password};
         }
         
         $u->{file_error}="Can not leech filesonic file";
         return $u;
      }
      $ua->{sm_logged}=1;      
   }

   $u->{auth_login}=$u->{auth_password}='';
   #$u->{file_name_orig}='';
   return $u;
}

sub pre4shared
{
   my ($u,$ua,$accs) = @_;
   $u->{url}=~s/\/\/4shared/\/\/www.4shared/i;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_fs_logins"}=~/^(.+):(.+)$/ if $c->{"my_fs_logins"};

   while(!$ua->{fs_logged})
   {
      unless($u->{auth_login} && $u->{auth_password})
      {
         last unless $u->{rslee};
         ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      }

      my $res = $ua->get('http://www.4shared.com');
      my @forms = HTML::Form->parse($res);
      my $form = $forms[2];
      $form->value('login' => $u->{auth_login});
            $form->value('password' => $u->{auth_password});
            $form->value('remember' => 'true');
      $res = $ua->request($form->click);
      #$res = $ua->get($1) if $res->content =~ /top\.location\.replace\("(.+)"/i;
      #unless($res->content=~/myAccount\.jsp/i)
      unless($res->content=~/top\.location\.replace\("/i)
      {
         if($u->{rslee})
         {
            ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
            next if $u->{auth_login} && $u->{auth_password};
         }
         $u->{file_error}="Can not leech 4shared file";
         return $u;
      }
      $ua->{fs_logged}=1;      
   }

   $u->{auth_login}=$u->{auth_password}='';
   $u->{file_name_orig}='';
   return $u;
}

sub pre2shared
{
   my ($u,$ua) = @_;
   my $res = $ua->get($u->{url})->decoded_content;
   if($res =~ /The file link that you requested is not valid/gis)
   {
      $u->{file_error} = '2shared.com: Invalid file link';
      return $u;
   }
   $res =~ /<div class="header">Download\s+(.*?)<\/div>/gis;
   $u->{file_name_orig} = $1;
   $u->{file_name_orig} =~ s/^\s+(.*)\s+$/$1/sim;
   ($u->{url}) = $res =~ /^.*?function startDownload\(\).*?"(.*?)";.*$/is;
   return $u;
}

sub preDepositfiles
{
   my ($u,$ua,$accs) = @_;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_df_logins"}=~/^(.+):(.+)$/ if $c->{"my_df_logins"};

   $ua->get("http://depositfiles.com/en/logout.php");
   if(!$u->{auth_login} && !$u->{auth_password} && $u->{rslee})
   {
      ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      $u->{file_error}="Can not leech depositfiles file" unless $u->{auth_login} && $u->{auth_password};
   }
   $u->{file_name_orig}='';
   return $u;

#  while(!$ua->{df_logged})
#  {
#     unless($u->{auth_login} && $u->{auth_password})
#     {
#        last unless $u->{rslee};
#        ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
#     }
#
#     my $req = HTTP::Request->new(GET => $u->{url});
#     $req->authorization_basic($u->{auth_login},$u->{auth_password});
#     my $res = $ua->request($req)->content;
#     #print"Content-type:text/html\n\n$res";exit;
#     my ($url) = $res =~ m#<div id="download_url">.*?<a href="(.*?)"#si;
#     unless($url)
#     {
#        if($u->{rslee})
#        {
#           ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
#           next if $u->{auth_login} && $u->{auth_password};
#        }
#        $u->{file_error}="Can not leech depositfiles file";
#        return $u;
#     }
#     $u->{url} = $url;
#     $ua->{df_logged}=1;
#  }

   $u->{auth_login}=$u->{auth_password}='';
   $u->{file_name_orig}='';
   return $u;
}

sub preUploading
{
   my ($u,$ua,$accs) = @_;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_ug_logins"}=~/^(.+):(.+)$/ if $c->{"my_ug_logins"};

   while(!$ua->{ug_logged})
   {
      unless($u->{auth_login} && $u->{auth_password})
      {
         last unless $u->{rslee};
         ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      }

      $ua->default_header('Referer' => 'http://uploading.com/');
      my $res = $ua->post('http://uploading.com/general/login_form/?JsHttpRequest='.int(rand(99999999999)+3264).'-xml', {email=>$u->{auth_login},password=>$u->{auth_password},remember=>'on'});
      sleep(2);
      $res = $ua->get('http://uploading.com/');

      if($res->content =~ /name="password"/i)
      {
         if($u->{rslee})
         {
            ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
            next if $u->{auth_login} && $u->{auth_password};
         }
         $u->{file_error}="Can not leech uploading.com file";
         return $u;
      }
      $ua->{ug_logged}=1;
   }

   my $res = $ua->get($u->{url});
   $u->{file_name_orig}=$1 if $res->content =~ m#<h2>(.+?)</h2>#i;
   $ua->default_header('Referer' => $u->{url});
   $res->content =~ m#action: 'get_link', file_id: (\d+), code: "(.*?)", pass:#si;
   my ($file_id,$code) = ($1,$2);
   $res = $ua->post('http://uploading.com/files/get/?JsHttpRequest='.int(rand(999999999999)+124367).'-xml',{action=>'get_link',file_id=>$file_id,code=>$code,pass=>'undefined'});
   $res->content =~ m#"link": "(http.*?)"#gis;
   $u->{url} = $1;
   $u->{url} =~ s/\\([^\\])/$1/g;

   unless($u->{url})
   {
      $u->{file_error}="Can not leech uploading.com file 2";
   }

   $u->{auth_login}=$u->{auth_password}='';
   return $u;
}

sub preFileserve
{
   my ($u,$ua,$accs) = @_;

   my @acc = shuffle(split(/\|/,$accs));
   $u->{accs}||=\@acc if $u->{rslee};

   ($u->{auth_login},$u->{auth_password})=$c->{"my_fe_logins"}=~/^(.+):(.+)$/ if $c->{"my_fe_logins"};

   while(!$ua->{fe_logged})
   {
      unless($u->{auth_login} && $u->{auth_password})
      {
         last unless $u->{rslee};
         ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
      }

      my $res = $ua->get('http://www.fileserve.com');
      my @forms = HTML::Form->parse($res);
      my $form = $forms[1];
      $form->value(loginUserName => $u->{auth_login});
      $form->value(loginUserPassword => $u->{auth_password});
      $res = $ua->request($form->click);

      unless($res->content=~/\/dashboard\.php/)
      {
         if($u->{rslee})
         {
            ($u->{auth_login},$u->{auth_password}) = shift(@{$u->{accs}})=~/^(.+):(.+)$/;
            next if $u->{auth_login} && $u->{auth_password};
         }
         $u->{file_error}="Can not leech fileserve file";
         return $u;
      }
      $ua->{fe_logged}=1;      
   }

   $u->{auth_login}=$u->{auth_password}='';
   $u->{file_name_orig}='';
   return $u;
}
