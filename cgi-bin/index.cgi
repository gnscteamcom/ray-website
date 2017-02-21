#!/usr/bin/perl
### SibSoft.net ###
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib '.';
use XFileConfig;
use Session;

$c->{ip_not_allowed}=~s/\./\\./g;
if($c->{ip_not_allowed} && $ENV{REMOTE_ADDR}=~/$c->{ip_not_allowed}/)
{
   print"Content-type:text/html\n\n";
   print"Your IP was banned by administrator";
   exit;
}

my $ses = Session->new();
my $f = $ses->f;
my $op = $f->{op};

if($f->{design}=~/^(\d+)$/)
{
   $ses->setCookie("design",$1,'+300d');
   $ses->redirect($c->{site_url});
}
&ChangeLanguage if $f->{lang};

my $db= $ses->db;
&CheckAuth() unless $op eq 'login';

#if($ENV{HTTP_CGI_AUTHORIZATION} && $ENV{HTTP_CGI_AUTHORIZATION} =~ s/basic\s+//i)
#{
#   &Login(undef,'instant');
#   print($ses->{cgi_query}->header(-status=>403)),exit unless $ses->{user};
#}

my $utype = $ses->getUser ? ($ses->getUser->{premium} ? 'prem' : 'reg') : 'anon';

$c->{$_}=$c->{"$_\_$utype"} for qw(max_upload_files
                                   disk_space
                                   max_upload_filesize
                                   download_countdown
                                   max_downloads_number
                                   captcha
                                   ads
                                   bw_limit
                                   remote_url
                                   direct_links
                                   down_speed
                                   max_rs_leech
                                   add_download_delay
                                   max_download_filesize
                                   torrent_dl
                                   torrent_dl_slots
                                   video_embed
                                   flash_upload
                                   rar_info);

my $sub={
    login         => \&LoginPage,
    news          => \&News,
    news_details  => \&NewsDetails,
    contact       => \&Contact,
    registration  => \&Register,
    register_save => \&RegisterSave,
    resend_activation => \&ResendActivationCode,
    upload_result => \&UploadResult,
    download1     => \&Download1,
    download2     => \&Download2,
    page          => \&Page,
    forgot_pass   => \&ForgotPass,
    contact_send  => \&ContactSend,
    user_public   => \&UserPublic,
    payments      => \&Payments,
    checkfiles    => \&CheckFiles,
    catalogue     => \&Catalogue,
    change_lang   => \&ChangeLanguage,
    report_file   => \&ReportFile,
    report_file_send => \&ReportFileSend,
    api_get_limits => \&APIGetLimits,
    comment_add   => \&CommentAdd,
    cmt_del       => \&CommentDel,
    del_file      => \&DelFile,
    links         => \&Links,
    video_embed   => \&VideoEmbed,
         }->{ $op };
&$sub if $sub;

&PaymentComplete($1) if $ENV{QUERY_STRING}=~/payment_complete=(.+)/;
&RegisterConfirm if $f->{confirm_account};

$sub={
        
    my_account       => \&MyAccount,
    my_referrals     => \&MyReferrals,
    my_files         => \&MyFiles,
    my_files_export  => \&MyFilesExport,
    my_reports       => \&MyReports,
    file_edit        => \&FileEdit,
    fld_edit         => \&FolderEdit,
    request_money    => \&RequestMoney,
    admin_files      => \&AdminFiles,
    admin_users      => \&AdminUsers,
    admin_user_edit  => \&AdminUserEdit,
    admin_users_add  => \&AdminUsersAdd,
    admin_servers    => \&AdminServers,
    admin_server_add => \&AdminServerAdd,
    admin_server_save=> \&AdminServerSave,
    admin_server_del => \&AdminServerDelete,
    admin_settings   => \&AdminSettings,
    admin_news       => \&AdminNews,
    admin_news_edit  => \&AdminNewsEdit,
    admin_reports    => \&AdminReports,
    admin_update_srv_stats  => \&AdminUpdateServerStats,
    admin_server_import     => \&AdminServerImport,
    admin_mass_email => \&AdminMassEmail,
    admin_downloads  => \&AdminDownloads,
    admin_downloads_all => \&AdminDownloadsAll,
    admin_comments   => \&AdminComments,
    admin_payments   => \&AdminPayments,
    admin_stats      => \&AdminStats,
    admin_check_db_file => \&AdminCheckDBFile,
    admin_check_file_db => \&AdminCheckFileDB,
    admin_torrents      => \&AdminTorrents,
    admin_anti_hack     => \&AdminAntiHack,
    admin_user_referrals=> \&AdminUserReferrals,
    moderator_files     => \&ModeratorFiles,
    logout           => sub{$ses->Logout},

	 }->{ $op };

if($sub && $ses->getUser)
{
   $ses->message("Access denied") if $op=~/^admin_/i && !$ses->getUser->{usr_adm} && $op!~/^(admin_reports|admin_comments)$/i;
   &$sub;
}
elsif($sub)
{
   $f->{redirect}=$ENV{REQUEST_URI};
   &LoginPage;
}
else
{
   &UploadForm;
}

sub LoginPage
{
   if($f->{login})
   {
      &Login();
      $f->{msg}=$ses->{lang}->{lang_login_pass_wrong} unless $ses->getUser;
   }
   $f->{login}||=$ses->getCookie('login');
   sleep 1 if $f->{msg};
   $ses->PrintTemplate("login.html",msg=>$f->{msg},login=>$f->{login},redirect=>$f->{redirect}||$ENV{HTTP_REFERER});
}

sub CheckAuth
{
  my $sess_id = $ses->getCookie( $ses->{auth_cook} );
  return undef unless $sess_id;
  return undef if $f->{id}&&!$ses->{dc};
  $ses->{user} = $db->SelectRow("SELECT u.*,
                                        UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec,
                                        UNIX_TIMESTAMP()-UNIX_TIMESTAMP(last_time) as dtt
                                 FROM Users u, Sessions s 
                                 WHERE s.session_id=? 
                                 AND s.usr_id=u.usr_id",$sess_id);
  unless($ses->{user})
  {
     sleep 1;
     return undef;
  }
  if($ses->{user}->{usr_status} eq 'BANNED')
  {
     delete $ses->{user};
     $ses->message("Your account was banned by administrator.");
  }
  if($ses->{user}->{dtt}>30)
  {
     $db->Exec("UPDATE Sessions SET last_time=NOW() WHERE session_id=?",$sess_id);
     $db->Exec("UPDATE Users SET usr_lastlogin=NOW(), usr_lastip=INET_ATON(?) WHERE usr_id=?", $ses->getIP, $ses->{user}->{usr_id} );
  }
  $ses->{user}->{premium}=1 if $ses->{user}->{exp_sec}>0;
  if($c->{m_d} && $ses->{user}->{usr_mod})
  {
      $ses->{lang}->{usr_mod}=1;
      $ses->{lang}->{m_d_f}=$c->{m_d_f};
      $ses->{lang}->{m_d_a}=$c->{m_d_a};
      $ses->{lang}->{m_d_c}=$c->{m_d_c};
  }
  #$ses->setCookie( $ses->{auth_cook} , $sess_id );
  return $ses->{user};
}

sub Login
{
  my ($no_redirect,$instant) = @_;

  ($f->{login}, $f->{password}) = split(':',$ses->decode_base64($ENV{HTTP_CGI_AUTHORIZATION})) if $instant;
  $ses->{user} = $db->SelectRow("SELECT *, UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec 
                                 FROM Users 
                                 WHERE usr_login=? 
                                 AND usr_password=ENCODE(?,?)", $f->{login}, $f->{password}, $c->{pasword_salt} );
  unless($ses->{user})
  {
     sleep 1;
     return undef;
  }
  
  $ses->{user}->{premium}=1 if $ses->{user}->{exp_sec}>0;
  if($ses->{user}->{usr_status} eq 'PENDING')
  {
     my $id = $ses->{user}->{usr_id}."-".$ses->{user}->{usr_login};
     delete $ses->{user};
     $ses->message("Your account haven't confirmed yet.<br>Check your e-mail for confirm link or contact site administrator.<br>Or try to <a href='?op=resend_activation&d=$id'>resend activation email</a>");
  }
  if($ses->{user}->{usr_status} eq 'BANNED')
  {
     delete $ses->{user};
     $ses->message("Your account was banned by administrator.");
  }
  return if $instant;

  my $sess_id = $ses->randchar(16);
  $db->Exec("DELETE FROM Sessions WHERE last_time + INTERVAL 5 DAY < NOW()");
  $db->Exec("INSERT INTO Sessions (session_id,usr_id,last_time) VALUES (?,?,NOW())",$sess_id,$ses->{user}->{usr_id});
  $db->Exec("UPDATE Users SET usr_lastlogin=NOW(), usr_lastip=INET_ATON(?) WHERE usr_id=?", $ses->getIP, $ses->{user}->{usr_id} );
  $ses->setCookie( $ses->{auth_cook} , $sess_id, '+30d' );
  $ses->setCookie('login',$f->{login},'+6M');
  $ses->redirect( $f->{redirect} ) if $f->{redirect};
  $ses->redirect( "$c->{site_url}/?op=my_files" ) unless $no_redirect;
  return $ses->{user};
};

sub Register
{
   my $msg = shift;
   #my $rand = $ses->randchar(8);
   #my %captcha = &GenerateCaptcha("rr$rand");
   #&SecSave( 0, $ses->getIP(), $captcha{number}, $rand );
   $c->{captcha}=1;
   my %secure = $ses->SecSave( 0, 2 );
   $f->{usr_login}=$ses->SecureStr($f->{usr_login});
   $f->{usr_email}=$ses->SecureStr($f->{usr_email});
   if($f->{aff_id}=~/^(\d+)$/i)
   {
      $ses->setCookie("aff",$1,'+14d');
   }
   $ses->PrintTemplate("registration.html",
                       #%captcha,
                       #'rand' => $rand,
                       %secure,
                       'usr_login' => $f->{usr_login},
                       'usr_email' => $f->{usr_email},
                       'usr_password'  => $f->{usr_password},
                       'usr_password2' => $f->{usr_password2},
                       'coupons'       => $c->{coupons}, 
                       'coupon_code'   => $f->{coupon_code}||$f->{coupon},
                       'usr_pay_email' => $f->{usr_pay_email},
                       "pay_type_$f->{usr_pay_type}"  => 1,
                       'msg'           => $f->{msg}||$msg,
                       'paypal_email'        => $c->{paypal_email},
                       'alertpay_email'      => $c->{alertpay_email},
                       'webmoney_merchant_id'=> $c->{webmoney_merchant_id},
                      );
}

sub RegisterSave
{
   $c->{captcha}=1;
   &Register unless $ses->SecCheck( $f->{'rand'}, 0, $f->{code} );
   &Register("Error: $ses->{lang}->{lang_login_too_short}") if length($f->{usr_login})<4;
   &Register("Error: $ses->{lang}->{lang_login_too_long}") if length($f->{usr_login})>32;
   &Register("Error: Invalid login: reserved word") if $f->{usr_login}=~/^(admin|images|captchas|files)$/;
   &Register("Error: $ses->{lang}->{lang_invalid_login}") unless $f->{usr_login}=~/^[\w\-\_]+$/;
   &Register("Error: Password contain bad symbols") if $f->{usr_password}=~/[<>"]/;
   &Register("Error: $ses->{lang}->{lang_pass_too_short}") if length($f->{usr_password})<4;
   &Register("Error: $ses->{lang}->{lang_pass_too_long}") if length($f->{usr_password})>32;
   &Register("Error: $ses->{lang}->{lang_pass_dont_match}") if $f->{usr_password} ne $f->{usr_password2};
   &Register("Error: $ses->{lang}->{lang_invalid_email}") unless $f->{usr_email}=~/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
   &Register("Error: $ses->{lang}->{lang_mailhost_banned}") if $c->{mailhosts_not_allowed} && $f->{usr_email}=~/\@$c->{mailhosts_not_allowed}/i;
   &Register("Error: $ses->{lang}->{lang_login_exist}")  if $db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{usr_login});
   &Register("Error: $ses->{lang}->{lang_email_exist}") if $db->SelectOne("SELECT usr_id FROM Users WHERE usr_email=?",$f->{usr_email});
   my $confirm_key = $ses->randchar(8) if $c->{registration_confirm_email};
   my $usr_status = $confirm_key ? 'PENDING' : 'OK';
   my $premium_days=0;
   $f->{coupon_code} = lc $f->{coupon_code};
   my $aff = $ses->getCookie('aff')||0;

   if($c->{coupons} && $f->{coupon_code})
   {
      my $hh;
      for(split(/\|/,$c->{coupons}))
      {
         $hh->{lc($1)}=$2 if /^(.+?)=(\d+)$/;
      }
      $premium_days = $hh->{$f->{coupon_code}};
      &Register("Invalid coupon code") unless $premium_days;
   }
   
   $db->Exec("INSERT INTO Users 
              SET usr_login=?, 
                  usr_email=?, 
                  usr_password=ENCODE(?,?),
                  usr_created=NOW(),
                  usr_premium_expire=NOW()+INTERVAL ? DAY,
                  usr_rapid_login=?,
                  usr_status=?,
                  usr_aff_id=?,
                  usr_pay_email=?, 
                  usr_pay_type=?",$f->{usr_login},
                                   $f->{usr_email},
                                   $f->{usr_password},
                                   $c->{pasword_salt},
                                   $premium_days,
                                   $confirm_key||'',
                                   $usr_status,
                                   $aff,
                                   $f->{usr_pay_email}||'',
                                   $f->{usr_pay_type}||'');
   my $usr_id=$db->getLastInsertId;
   $db->Exec("INSERT INTO Stats SET day=CURDATE(), registered=1 ON DUPLICATE KEY UPDATE registered=registered+1");
   if($confirm_key)
   {
      my $t = $ses->CreateTemplate("registration_email.html");
      $t->param( 'usr_login'=>$f->{usr_login}, 'usr_password'=>$f->{usr_password}, 'confirm_id'=>"$usr_id-$confirm_key" );
      $c->{email_text}=1;
      $ses->SendMail($f->{usr_email},$c->{email_from},"$c->{site_name} registration confirmation",$t->output);
      $ses->message($ses->{lang}->{lang_account_created}) if $confirm_key;
   }

   my $err = $ses->ApplyPlugins('user_new', $f->{usr_login}, $f->{usr_password}, $f->{usr_email});
   $ses->message("Registration complete but there were plugin errors:<br><br>$err") if $err;

   $f->{login}    = $f->{usr_login};
   $f->{password} = $f->{usr_password};
   &Login();

   $ses->redirect( $c->{site_url} );
}

sub RegisterConfirm
{
   my ($usr_id,$confirm_key)=split('-',$f->{confirm_account});
   my $user = $db->SelectRow("SELECT *,DECODE(usr_password,?) as usr_password FROM Users WHERE usr_id=? AND usr_rapid_login=?",$c->{pasword_salt},$usr_id,$confirm_key);
   unless($user)
   {
      sleep 1;
      $ses->message("Invalid confirm code");
   }
   $ses->message("Account already confirmed") if $user->{usr_status} ne 'PENDING';
   $db->Exec("UPDATE Users SET usr_status='OK', usr_rapid_login='' WHERE usr_id=?",$user->{usr_id});
   $f->{login}    = $user->{usr_login};
   $f->{password} = $user->{usr_password};
   &Login('no_redirect');

   $ses->redirect( $c->{site_url}.'?msg=Account confirmed' );
}

sub ResendActivationCode
{
   my ($adm_mode) = @_;
   sleep(1) unless $adm_mode;
   ($f->{usr_id},$f->{usr_login}) = split(/-/,$f->{d});
   my $user = $db->SelectRow("SELECT usr_id,usr_login,usr_email,usr_rapid_login,DECODE(usr_password,?) as usr_password
                              FROM Users
                              WHERE usr_id=?
                              AND usr_login=?",$c->{pasword_salt},$f->{usr_id},$f->{usr_login});
   sleep(3) && $ses->message("Invalid ID") unless $user;

   my $t = $ses->CreateTemplate("registration_email.html");
   $t->param( 'usr_login'=>$user->{usr_login}, 'usr_password'=>$user->{usr_password}, 'confirm_id'=>"$user->{usr_id}-$user->{usr_rapid_login}" );
   $c->{email_text}=1;
   $ses->SendMail($user->{usr_email},$c->{email_from},"$c->{site_name} registration confirmation",$t->output);
   $ses->redirect_msg("?op=admin_users","Activation email sent") if $adm_mode;
   $ses->message("Activation email just resent.<br>To activate it follow the activation link sent to your e-mail.");
}

sub ForgotPass
{
   if($f->{usr_login})
   {
      my $user = $db->SelectRow("SELECT *, DECODE(usr_password,?) as usr_password 
                                 FROM Users 
                                 WHERE usr_login=? 
                                 OR usr_email=?",$c->{pasword_salt},$f->{usr_login},$f->{usr_login});
      $ses->message($ses->{lang}->{lang_no_login_email}) unless $user;
      $c->{email_text}=1;
      $ses->SendMail( $user->{usr_email}, $c->{email_from}, "$c->{site_name}: password reminder", "Login: $user->{usr_login}\nPassword: $user->{usr_password}" );
      $ses->message($ses->{lang}->{lang_login_pass_sent});
   }
   $ses->PrintTemplate("forgot_pass.html");
}

sub UploadForm
{
   $ses->message("Register on site to be able to upload files") if !$c->{enabled_anon} && !$ses->getUser;
   my $type_filter = $utype eq 'prem' ? "AND srv_allow_premium=1" : "AND srv_allow_regular=1";
   my $server = $db->SelectRow("SELECT * FROM Servers 
                                WHERE srv_status='ON' 
                                AND srv_disk+? <= srv_disk_max
                                $type_filter
                                ORDER BY srv_last_upload 
                                LIMIT 1",$c->{max_upload_filesize}||100);

   my $server_torrent = $db->SelectRow("SELECT * FROM Servers 
                                WHERE srv_status='ON' 
                                AND srv_disk+? <= srv_disk_max
                                $type_filter
                                AND srv_torrent=1
                                ORDER BY srv_last_upload 
                                LIMIT 1",$c->{max_upload_filesize}||100);

   $server = $db->SelectRow("SELECT * FROM Servers WHERE srv_id=?",$f->{srv_id}) if $ses->getUser && $ses->getUser->{usr_adm} && $f->{srv_id};
   
   $ses->redirect('?op=admin_server_add') if !$server && $ses->getUser && $ses->getUser->{usr_adm};
   $ses->message("We're sorry, there are no servers available for upload at the moment.<br>Refresh this page in some minutes.") unless $server;
   $server->{srv_htdocs_url}=~s/\/(\w+)$//;
   $server->{srv_tmp_url} = "$server->{srv_htdocs_url}/tmp";
   $server_torrent->{srv_htdocs_url}=~s/\/(\w+)$//;
   $server_torrent->{srv_tmp_url} = "$server_torrent->{srv_htdocs_url}/tmp";
   my @url_fields = map{{ 'number'=>$_, 'enable_file_descr'=>$c->{enable_file_descr} }} (1..$c->{max_upload_files});
   my ($rapid_login,$rapid_pass)=($ses->getUser->{usr_rapid_login},$ses->getUser->{usr_rapid_pass}) if $ses->getUser;

   my $stats;
   if($c->{show_server_stats})
   {
      $stats = $db->SelectRow("SELECT SUM(srv_files) as files_total, ROUND(SUM(srv_disk)/1073741824,2) as used_total FROM Servers");
      $stats->{user_total} = $db->SelectOne("SELECT COUNT(*) FROM Users");
   }

   my $mmrr=$c->{"\x6d\x5f\x72"};
   my ($leech_on,$leech_left_mb);
   if($mmrr && $ses->getUser && $c->{max_rs_leech})
   {
      $leech_left_mb = $c->{max_rs_leech} - $db->SelectOne("SELECT ROUND(SUM(size)/1048576) FROM IP2RS WHERE created>NOW()-INTERVAL 24 HOUR AND (usr_id=? OR ip=INET_ATON(?))",$ses->getUserId,$ses->getIP);
      $leech_on=1 if $leech_left_mb>0;
   }
   my $mmtt=$ses->iPlg('t');
   my $mmtt_on = $mmtt && $c->{"\x74\x6f\x72\x72\x65\x6e\x74\x5f\x64\x6c"};
   #$mmtt=0 unless $server_torrent->{srv_id};
   my $tt_msg;
   if($mmtt && !$server_torrent->{srv_id})
   {
      $mmtt_on=0;
      $tt_msg.=$ses->{lang}->{lang_no_torrent_srv}."<br>";
   }
   if($mmtt && $c->{torrent_dl_slots} && $db->SelectOne("SELECT COUNT(*) FROM Torrents WHERE usr_id=? AND status='WORKING'",$ses->getUserId)>=$c->{torrent_dl_slots})
   {
      $mmtt_on=0;
      $tt_msg.=$ses->{lang}->{lang_full_torr_slots}." ($c->{torrent_dl_slots})<br>";
   }

   my $mmff=$ses->iPlg('f');
   my $mmff_on = $mmff && $c->{flash_upload};
   my $exts = join ';', map{"*.$_"} split(/\|/,$c->{ext_allowed});
   my $exts2 = join ':', map{"*.$_"} split(/\|/,$c->{ext_allowed});
   $exts2||='*.*';

   my @supported;
   my $sites = {rs => 'Rapidshare.com',
                mu => 'Megaupload.com',
                hf => 'Hotfile.com',
                nl => 'Netload.in',
                mf => 'Mediafire.com',
                fs => '4shared.com',
                df => 'Depositfiles.com',
                ff => 'Filefactory.com',
                es => 'Easy-share.com',
                sm => 'Filesonic.com',
                ug => 'Uploading.com',
                fe => 'Fileserve.com',
               };
   for(keys %$sites)
   {
      push @supported, $sites->{$_} if $c->{"$_\_logins"};
   }
   push @supported, '2shared.com';

   my $supported_sites = join ', ', sort @supported;

   my $data = $db->SelectARef("SELECT name,value FROM UserData WHERE usr_id=?",$ses->getUserId);
   my @site_logins = map{ {name=>$_->{name},value=>$_->{value}} } grep{$_->{name}=~/_logins$/i && $_->{value}} @$data;

   $ses->PrintTemplate("upload_form.html",
                       'ext_allowed'      => $c->{ext_allowed},
                       'ext_not_allowed'  => $c->{ext_not_allowed},
                       'max_upload_files' => $c->{max_upload_files},
                       'max_upload_files_rows' => $c->{max_upload_files}<=10 ? $c->{max_upload_files} : 10,
                       'max_upload_filesize' => $c->{max_upload_filesize},
                       'max_upload_filesize_bytes' => $c->{max_upload_filesize}*1024*1024,
                       'enable_file_descr'=> $c->{enable_file_descr},
                       'remote_url'       => $c->{remote_url},

                       'srv_cgi_url'      => $server->{srv_cgi_url},
                       'srv_tmp_url'      => $server->{srv_tmp_url},
                       'srv_htdocs_url'   => $server->{srv_htdocs_url},

                       'srv_torrent_cgi_url' => $server_torrent->{srv_cgi_url},
                       'srv_torrent_tmp_url' => $server_torrent->{srv_tmp_url},

                       'sess_id'          => $ses->getCookie( $ses->{auth_cook} ),
                       'mmrr'             => $mmrr,
                       'mmtt'             => $mmtt,
                       'mmtt_on'          => $mmtt_on,
                       'tt_msg'           => $tt_msg,
                       'mmff'             => $mmff,
                       'mmff_on'          => $mmff_on,
                       'utype'            => $utype,
                       'url_fields'       => \@url_fields,
                       'rapid_login'      => $rapid_login,
                       'rapid_pass'       => $rapid_pass,
                       'supported_sites'  => $supported_sites,
                       'exts'             => $exts,
                       'exts2'            => $exts2,
                       'leech_left_mb'    => $leech_left_mb,
                       'leech_on'         => $leech_on,
                       %{$stats},
                       'site_logins'      => \@site_logins,
                       'max_rs_leech'     => $c->{max_rs_leech},
                      );
}

sub UploadResult
{
   my $fnames      = &ARef($f->{'fn'});
   my $status      = &ARef($f->{'st'});

   my @arr;exit if $c->{site_url}!~/\/\/(www\.|)$ses->{dc}/i || !$ses->{dc};
   
   for(my $i=0;$i<=$#$fnames;$i++)
   {
      $fnames->[$i] = $ses->SecureStr($fnames->[$i]);
      $status->[$i] = $ses->SecureStr($status->[$i]);
      unless($status->[$i] eq 'OK')
      {
          push @arr, {file_name => $fnames->[$i],'error' => " $status->[$i]"};
          next;
      }
      my $file = $db->SelectRow("SELECT f.*, s.srv_htdocs_url
                                 FROM Files f, Servers s
                                 WHERE f.file_code=?
                                 AND f.srv_id=s.srv_id
                                 AND f.file_created > NOW()-INTERVAL 15 MINUTE",$fnames->[$i]);
      next unless $file;
      $file->{file_size2} = $file->{file_size};
      $file->{file_size} = $ses->makeFileSize($file->{file_size});
      $file->{download_link} = $ses->makeFileLink($file);
      $file->{delete_link} = "$file->{download_link}?killcode=$file->{file_del_id}";
      if($c->{m_i} && $file->{file_name}=~/\.(jpg|jpeg|gif|png|bmp)$/i)
      {
         $ses->getThumbLink($file);
      }
      if($c->{m_v} && $c->{video_embed} && $file->{file_spec}=~/^V/)
      {
         my @fields=qw(vid vid_length vid_width vid_height vid_bitrate vid_audio_bitrate vid_audio_rate vid_codec vid_audio_codec vid_fps);
         my @vinfo = split(/\|/,$file->{file_spec});
         $file->{$fields[$_]}=$vinfo[$_] for (0..$#fields);
         $file->{vid_width}||=400;
         $file->{vid_height}||=300;
         $file->{vid_height}+=24;
         $file->{video_embed_code}=1;
      }
      push @arr, $file;
   }
   exit unless $ses->{cq} eq $c->{$ses->{xq}};
   if($f->{link_rcpt}=~/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/ && $#arr>-1)
   {
      my $tmpl = $ses->CreateTemplate("confirm_email_user.html");
      $tmpl->param('files' => \@arr);
      $ses->SendMail( $f->{link_rcpt}, $c->{email_from}, "$c->{site_name}: File send notification", $tmpl->output() );
   }
   if($c->{deurl_site} && $c->{deurl_api_key})
   {
      require LWP::UserAgent;
      my $ua = LWP::UserAgent->new(timeout => 5);
      my $author = $ses->getUser ? $ses->getUser->{usr_login} : '';
      for(@arr)
      {
         my $res = $ua->post("$c->{deurl_site}/", 
                             {
                                op  => 'api',
                                api_key => $c->{deurl_api_key},
                                url => $_->{download_link},
                                size => sprintf("%.01f",$_->{file_size2}/1048576),
                                author => $author,
                             }
                            )->content;
         ($_->{deurl}) = $res=~/^OK:(.+)$/;
      }
   }
   if($ses->iPlg('w') && $c->{m_w} && $ses->getUser)
   {
      my $data = $db->SelectARef("SELECT name,value FROM UserData WHERE usr_id=?",$ses->getUserId);
      my $udata;
      $udata->{$_->{name}}=$_->{value} for @$data;
      if($udata->{twitter_login} && $udata->{twitter_password})
      {
         require Net::Twitter::Lite;
         my $nt = Net::Twitter::Lite->new(consumer_key        => $c->{twit_consumer1},
                                          consumer_secret     => $c->{twit_consumer2},
                                          access_token        => $udata->{twitter_login},
                                          access_token_secret => $udata->{twitter_password},
                                         );
         for(@arr)
         {
            my $descr = substr($_->{file_descr},0,100);
            $descr="$descr " if $descr;
            $descr.="$_->{file_name} " if $udata->{twitter_filename};
            eval { $nt->update("$descr$_->{download_link}") };
            die"Twitter error: $@" if $@;
         }
      }
   }

   if(-f "$c->{site_path}/catalogue.rss" && time-(lstat("$c->{site_path}/catalogue.rss"))[9]>3)
   {
     my $last = $db->SelectARef("SELECT file_code,file_name,file_descr,DATE_FORMAT(CONVERT_TZ(file_created, 'SYSTEM', '+0:00'),'%a, %d %b %Y %T GMT') as date FROM Files WHERE file_public=1 ORDER BY file_created DESC LIMIT 20");
     for (@$last)
     {
       $_->{download_link} = $ses->makeFileLink($_);
       $_->{download_link}=~s/\&/&amp;/gs;
       $_->{download_link}=$ses->SecureStr($_->{download_link});
       $_->{file_name}=~s/\&/&amp;/gs;
       $_->{file_name}=$ses->SecureStr($_->{file_name});
     }
     my $tt = $ses->CreateTemplate("feed.rss");
     $tt->param(list => $last);
     open FILE, ">$c->{site_path}/catalogue.rss";
     print FILE $tt->output;
     close FILE;
   }exit unless $ses->{dc};

   $ses->ApplyPlugins('file_new',$_,$ses->db) for @arr;
   
   $ses->PrintTemplate("upload_results.html",
                       'links' => \@arr,
                      );
}


sub AdminDownloads
{
   my $list = $db->SelectARef("SELECT *, INET_NTOA(ip) as ip FROM IP2Files WHERE file_id=? ORDER BY created DESC".$ses->makePagingSQLSuffix($f->{page}),$f->{file_id});
   my $total = $db->SelectOne("SELECT COUNT(*) FROM IP2Files WHERE file_id=?",$f->{file_id});
   $ses->PrintTemplate("admin_downloads.html",
                       'list'=>$list,
                       'paging' => $ses->makePagingLinks($f,$total),
                      );
}

sub AdminDownloadsAll
{
   $f->{usr_id}=$db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{usr_login}) if $f->{usr_login};
   $f->{owner_id}=$db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{owner_login}) if $f->{owner_login};
   my $filter_user = "AND i.usr_id=$f->{usr_id}" if $f->{usr_id}=~/^\d+$/;
   my $filter_owner = "AND i.owner_id=$f->{owner_id}" if $f->{owner_id}=~/^\d+$/;
   my $filter_ip = "AND i.ip=INET_ATON('$f->{ip}')" if $f->{ip}=~/^[\d\.]+$/;
   my $list = $db->SelectARef("SELECT i.*, INET_NTOA(i.ip) as ip, 
                                      f.file_name, f.file_code,
                                      u.usr_login
                               FROM (IP2Files i, Files f)
                               LEFT JOIN Users u ON i.usr_id = u.usr_id
                               WHERE i.file_id=f.file_id
                               $filter_user
                               $filter_owner
                               $filter_ip
                               ORDER BY created DESC".$ses->makePagingSQLSuffix($f->{page}));
   my $total = $db->SelectOne("SELECT COUNT(*)
                               FROM IP2Files i
                               WHERE 1
                               $filter_user
                               $filter_owner
                               $filter_ip
                              ");
   for(@$list)
   {
      $_->{download_link} = $ses->makeFileLink($_);

      $_->{money}= $_->{money} eq '0.0000' ? '' : "\$$_->{money}";
      $_->{money}=~s/0+$//;
      #$_->{referer}="http://$_->{referer}" unless $_->{referer}=~/^\//;
      #$_->{referer} = CGI::Simple::Util::unescape($_->{referer});
      #$_->{referer_txt} = length($_->{referer})>42 ? substr($_->{referer},0,42).'&#133;' : $_->{referer};
   }
   $ses->PrintTemplate("admin_downloads_all.html",
                       list      =>$list,
                       usr_login => $f->{usr_login},
                       ip        => $f->{ip},
                       paging    => $ses->makePagingLinks($f,$total),
                      );
}

sub News
{
   my $news = $db->SelectARef("SELECT n.*, DATE_FORMAT(n.created,'%M %dth, %Y') as created_txt,
                                      COUNT(c.cmt_id) as comments
                               FROM News n
                               LEFT JOIN Comments c ON c.cmt_type=2 AND c.cmt_ext_id=n.news_id
                               WHERE n.created<=NOW()
                               GROUP BY n.news_id
                               ORDER BY n.created DESC".$ses->makePagingSQLSuffix($f->{page}));
   my $total = $db->SelectOne("SELECT COUNT(*) FROM News WHERE created<NOW()");
   for(@$news)
   {
      $_->{site_url} = $c->{site_url};
      $_->{news_text} =~s/\n/<br>/gs;
      $_->{enable_file_comments} = $c->{enable_file_comments};
   }
   $ses->PrintTemplate("news.html",
                       'news' => $news,
                       'paging' => $ses->makePagingLinks($f,$total),
                      );
}

sub NewsDetails
{
   my $news = $db->SelectRow("SELECT *, DATE_FORMAT(created,'%M %e, %Y at %r') as date 
                              FROM News 
                              WHERE news_id=? AND created<=NOW()",$f->{news_id});
   $ses->message("No such news") unless $news;
   $news->{news_text} =~s/\n/<br>/gs;
   my $comments = &CommentsList(2,$f->{news_id});
   $ses->{page_title} = $ses->{meta_descr} = $news->{news_title};
   $ses->PrintTemplate("news_details.html",
                        %{$news},
                        'cmt_type'     => 2,
                        'cmt_ext_id'   => $news->{news_id},
                        'comments' => $comments,
                        'enable_file_comments' => $c->{enable_file_comments},
                      );
}

sub CommentsList
{
   my ($cmt_type,$cmt_ext_id) = @_;
   my $list = $db->SelectARef("SELECT *, INET_NTOA(cmt_ip) as ip, DATE_FORMAT(created,'%M %e, %Y at %r') as date
                               FROM Comments 
                               WHERE cmt_type=? 
                               AND cmt_ext_id=?
                               ORDER BY created",$cmt_type,$cmt_ext_id);
   for (@$list)
   {
      $_->{cmt_text}=~s/\n/<br>/gs;
      $_->{cmt_name} = "<a href='$_->{cmt_website}'>$_->{cmt_name}</a>" if $_->{cmt_website};
      if($ses->getUser && $ses->getUser->{usr_adm})
      {
         $_->{email} = $_->{cmt_email};
         $_->{adm} = 1;
      }
   }
   return $list;
}

sub ChangeLanguage
{
   $ses->setCookie('lang',$f->{lang});
   $ses->redirect($ENV{HTTP_REFERER}||$c->{site_url});
}

sub Page
{
   my $tmpl = shift || $f->{tmpl};
   $ses->{language}=$c->{default_language} unless -e "Templates/Pages/$ses->{language}/$tmpl.html";
   &UploadForm unless -e "Templates/Pages/$ses->{language}/$tmpl.html";
   $ses->PrintTemplate("Pages/$ses->{language}/$tmpl.html");
}

sub Contact
{
   $c->{captcha}=1;
   my %secure = $ses->SecSave( 1, 2 );
   $f->{$_}=$ses->SecureStr($f->{$_}) for keys %$f;
   $f->{email}||=$ses->getUser->{usr_email} if $ses->getUser;
   $ses->PrintTemplate("contact.html",
                       %{$f},
                       %secure,
                      );
}

sub ContactSend
{
   &Contact unless $ENV{REQUEST_METHOD} eq 'POST';
   $c->{captcha}=1;
   &Contact unless $ses->SecCheck( $f->{'rand'}, 1, $f->{code} );

   $f->{msg}.="Email is not valid. " unless $f->{email} =~ /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
   $f->{msg}.="Message required. " unless $f->{message};
   
   &Contact if $f->{msg};

   $f->{$_}=$ses->SecureStr($f->{$_}) for keys %$f;

   $f->{message} = "You've got new message from $c->{site_name}.\n\nName: $f->{name}\nE-mail: $f->{email}\nIP: $ENV{REMOTE_ADDR}\n\n$f->{message}";
   $c->{email_text}=1;
   $ses->SendMail($c->{contact_email}, $c->{email_from}, "New message from $c->{site_name} contact form", $f->{message});
   $ses->redirect("$c->{site_url}/?msg=Message sent successfully");
}

sub DelFile
{
   my ($id,$del_id) = @_;
   $id||=$f->{id};
   $del_id||=$f->{del_id};
   my $file = $db->SelectRow("SELECT * FROM Files f, Servers s
                              WHERE file_code=?
                              AND f.srv_id=s.srv_id",$id);
   $ses->message('No such file exist') unless $file;
   $ses->message('Server with this file is Offline') if $file->{srv_status} eq 'OFF';

   unless($file->{file_del_id} eq $del_id)
   {
      sleep 2;
      $ses->message('Wrong Delete ID')
   }
   if($f->{confirm} eq 'yes')
   {
      $ses->DeleteFile($file);
      $ses->PrintTemplate("delete_file.html", 'status'=>$ses->{lang}->{lang_file_deleted});
   }
   else
   {
      $ses->PrintTemplate("delete_file.html",
                          'confirm' =>1,
                          'id'      => $id,
                          'del_id'  => $del_id,
                          'fname'   => $file->{file_name},
                         );
   }
}

sub AdminFiles
{
   if($f->{del_code})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my $file = $db->SelectRow("SELECT f.*, u.usr_aff_id
                                 FROM Files f 
                                 LEFT JOIN Users u ON f.usr_id=u.usr_id
                                 WHERE file_code=?",$f->{del_code});
      $ses->message("No such file") unless $file;
      $file->{del_money}=$c->{del_money_file_del};
      $ses->DeleteFile($file);
      if($f->{del_info})
      {
         $db->Exec("INSERT INTO DelReasons SET file_code=?, file_name=?, info=?",$file->{file_code},$file->{file_name},$f->{del_info});
      }
      $ses->redirect("$c->{site_url}/?op=admin_files");
   }
   if($f->{del_selected} && $f->{file_id})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      die"security error" unless $ENV{REQUEST_METHOD} eq 'POST';
      my $files = $db->SelectARef("SELECT * FROM Files WHERE file_id IN (".join(',',@{&ARef($f->{file_id})}).")");
      $_->{del_money}=$c->{del_money_file_del} for @$files;
      $ses->DeleteFilesMass($files);
      if($f->{del_info})
      {
         for(@$files)
         {
            $db->Exec("INSERT INTO DelReasons SET file_code=?, file_name=?, info=?",$_->{file_code},$_->{file_name},$f->{del_info});
         }
      }
      
      $ses->redirect("$c->{site_url}/?op=admin_files");
   }
   if($f->{srv_id_to} && $f->{file_id})
   {
      my $server2 = $db->SelectRow("SELECT * FROM Servers WHERE srv_id=?",$f->{srv_id_to});
      my $files = $db->SelectARef("SELECT * FROM Files WHERE file_id IN (".join(',',@{&ARef($f->{file_id})}).") AND srv_id<>? GROUP BY file_real",$f->{srv_id_to});
      for(@$files)
      {
         $_->{file_real_id}||=$_->{file_id};
      }
      my %h;
      push(@{$h{$_->{srv_id}}},$_) for @$files;
      print"Content-type:text/html\n\n";
      print"<HTML><BODY>";
      for my $srv_id (keys %h)
      {
         my $server = $db->SelectRow("SELECT * FROM Servers WHERE srv_id=?",$srv_id);
         print"<b>Transfer from server $server->{srv_id} - $server->{srv_name}</b><br>\n";
         print"<iframe name='i$server->{srv_id}' style='width:640px;height:300px;border:1px solid black;' src='about:blank'></iframe>";
         print"<Form name='srv$server->{srv_id}' method='POST' action='$server->{srv_cgi_url}/api.cgi' target='i$server->{srv_id}'>";
         print"<input type='hidden' name='op' value='transfer'>\n";
         print"<input type='hidden' name='fs_key' value='$server->{srv_key}'>\n";
         print"<input type='hidden' name='fs_key2' value='$server2->{fs_key}'>\n";
         print"<input type='hidden' name='srv_id2' value='$server2->{srv_id}'>\n";
         print"<input type='hidden' name='srv_cgi_url2' value='$server2->{srv_cgi_url}'>\n";
         my $files = join('|',map{"$_->{file_real_id}:$_->{file_real}"}@{$h{$srv_id}});
         print"<input type='hidden' name='files' value='$files'>\n";
         print"</Form>";
         print"<script>document.srv$server->{srv_id}.submit();</script>"
      }
      print"<br><br><a href='?op=admin_files'>Back to Admin Files</a></BODY></HTML>";
      exit;
   }

   my $filter_files;
   $f->{mass_search}=~s/\r//gs;
   $f->{mass_search}=~s/\s+\n/\n/gs;
   if($f->{mass_search})
   {
      my @arr;
      push @arr,$1 while $f->{mass_search}=~/\/(\w{12})(\/|\n|$)/gs;
      $filter_files = "AND file_code IN ('".join("','",@arr)."')";
   }

   $f->{sort_field}||='file_created';
   $f->{sort_order}||='down';
   $f->{per_page}||=$c->{items_per_page};
   $f->{usr_id}=$db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{usr_login}) if $f->{usr_login};
   my $filter_key    = "AND (file_name LIKE '%$f->{key}%' OR file_code='$f->{key}')" if $f->{key};
   my $filter_user   = "AND f.usr_id='$f->{usr_id}'" if $f->{usr_id};
   my $filter_server = "AND f.srv_id='$f->{srv_id}'" if $f->{srv_id}=~/^\d+$/;
   my $filter_down_more = "AND f.file_downloads>$f->{down_more}" if $f->{down_more}=~/^\d+$/;
   my $filter_down_less = "AND f.file_downloads<$f->{down_less}" if $f->{down_less}=~/^\d+$/;
   my $filter_size_more = "AND f.file_size>".$f->{size_more}*1048576 if $f->{size_more}=~/^\d+$/;
   my $filter_size_less = "AND f.file_size<".$f->{size_less}*1048576 if $f->{size_less}=~/^\d+$/;

   my $filter_ip     = "AND f.file_ip=INET_ATON('$f->{ip}')" if $f->{ip}=~/^\d+\.\d+\.\d+\.\d+$/;
   my $files = $db->SelectARef("SELECT f.*, file_downloads*file_size as traffic,
                                       INET_NTOA(file_ip) as file_ip,
                                       u.usr_id, u.usr_login
                                FROM Files f
                                LEFT JOIN Users u ON f.usr_id = u.usr_id
                                WHERE 1
                                $filter_files
                                $filter_key
                                $filter_user
                                $filter_server
                                $filter_down_more
                                $filter_down_less
                                $filter_size_more
                                $filter_size_less
                                $filter_ip
                                ".&makeSortSQLcode($f,'file_created').$ses->makePagingSQLSuffix($f->{page},$f->{per_page}) );
   my $total = $db->SelectOne("SELECT COUNT(*) as total_count
                                FROM Files f 
                                WHERE 1 
                                $filter_files
                                $filter_key 
                                $filter_user 
                                $filter_server
                                $filter_down_more
                                $filter_down_less
                                $filter_size_more
                                $filter_size_less
                                $filter_ip
                                ");

   for(@$files)
   {
      $_->{site_url} = $c->{site_url};
      my $file_name = $_->{file_name};
      utf8::decode($file_name);
      $_->{file_name_txt} = length($file_name)>$c->{display_max_filename} ? substr($file_name,0,$c->{display_max_filename}).'&#133;' : $file_name;
      utf8::encode($_->{file_name_txt});
      $_->{file_size2} = $ses->makeFileSize($_->{file_size});
      $_->{traffic}    = $_->{traffic} ? $ses->makeFileSize($_->{traffic}) : '';
      $_->{download_link} = $ses->makeFileLink($_);
      $_->{file_downloads}||='';
      $_->{file_last_download}='' unless $_->{file_downloads};
      $_->{file_money} = $_->{file_money} eq '0.0000' ? '' : '$'.$_->{file_money};
      $_->{file_money}=~s/0+$//;
   }
   my %sort_hash = &makeSortHash($f,['file_name','usr_login','file_downloads','file_money','file_size','traffic','file_created','file_last_download']);

   my $servers = $db->SelectARef("SELECT srv_id,srv_name FROM Servers WHERE srv_status<>'OFF' ORDER BY srv_id");
   
   $ses->PrintTemplate("admin_files.html",
                       'files'   => $files,
                       'key'     => $f->{key},
                       'usr_id'  => $f->{usr_id},
                       'down_more'  => $f->{down_more},
                       'down_less'  => $f->{down_less},
                       'size_more'  => $f->{size_more},
                       'size_less'  => $f->{size_less},
                       "per_$f->{per_page}" => ' checked',
                       %sort_hash,
                       'paging'     => $ses->makePagingLinks($f,$total),
                       'items_per_page' => $c->{items_per_page},
                       'servers'    => $servers,
                       'usr_login'  => $f->{usr_login},
                      );
}

sub ModeratorFiles
{
   $ses->message("Access denied") if !$ses->getUser->{usr_adm} && !($c->{m_d} && $ses->getUser->{usr_mod} && $c->{m_d_f});
   if($f->{del_selected} && $f->{file_id})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my $files = $db->SelectARef("SELECT * FROM Files WHERE file_id IN (".join(',',@{&ARef($f->{file_id})}).")");
      $_->{del_money}=$c->{del_money_file_del} for @$files;
      $ses->DeleteFilesMass($files);
      if($f->{del_info})
      {
         for(@$files)
         {
            $db->Exec("INSERT INTO DelReasons SET file_code=?, file_name=?, info=?",$_->{file_code},$_->{file_name},$f->{del_info});
         }
      }
      $ses->redirect("$c->{site_url}/?op=moderator_files");
   }

   my $filter_files;
   if($f->{mass_search})
   {
      my @arr;
      push @arr,$1 while $f->{mass_search}=~/\/(\w{12})\//gs;
      $filter_files = "AND file_code IN ('".join("','",@arr)."')";
   }

   $f->{per_page}||=$c->{items_per_page};
   $f->{usr_id}=$db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{usr_login}) if $f->{usr_login};
   my $filter_key    = "AND (file_name LIKE '%$f->{key}%' OR file_code='$f->{key}')" if $f->{key};
   my $filter_user   = "AND f.usr_id='$f->{usr_id}'" if $f->{usr_id};
   my $filter_ip     = "AND f.file_ip=INET_ATON('$f->{ip}')" if $f->{ip}=~/^[\d\.]+$/;
   my $files = $db->SelectARef("SELECT f.*,
                                       INET_NTOA(file_ip) as file_ip,
                                       u.usr_id, u.usr_login
                                FROM Files f
                                LEFT JOIN Users u ON f.usr_id = u.usr_id
                                WHERE 1
                                $filter_files
                                $filter_key
                                $filter_user
                                $filter_ip
                                ORDER BY file_created DESC
                                ".$ses->makePagingSQLSuffix($f->{page},$f->{per_page}) );
   my $total = $db->SelectOne("SELECT COUNT(*) as total_count
                                FROM Files f 
                                WHERE 1 
                                $filter_files
                                $filter_key 
                                $filter_user 
                                $filter_ip
                                ");

   for(@$files)
   {
      $_->{site_url} = $c->{site_url};
      my $file_name = $_->{file_name};
      utf8::decode($file_name);
      $_->{file_name_txt} = length($file_name)>$c->{display_max_filename} ? substr($file_name,0,$c->{display_max_filename}).'&#133;' : $file_name;
      utf8::encode($_->{file_name_txt});
      $_->{file_size2} = sprintf("%.01f Mb",$_->{file_size}/1048576);
      $_->{download_link} = $ses->makeFileLink($_);
   }
  
   $ses->PrintTemplate("admin_files_moderator.html",
                       'files'   => $files,
                       'key'     => $f->{key},
                       'usr_id'  => $f->{usr_id},
                       "per_$f->{per_page}" => ' checked',
                       'paging'     => $ses->makePagingLinks($f,$total),
                       'items_per_page' => $c->{items_per_page},
                       'usr_login'  => $f->{usr_login},
                      );
}

sub AdminUsers
{
   if($f->{del_id})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my $files = $db->SelectARef("SELECT srv_id,file_code,file_id,file_real,file_real_id FROM Files WHERE usr_id=?",$f->{del_id});
      $ses->DeleteFilesMass($files);
      $ses->DeleteUserDB($f->{del_id});
      $ses->redirect("?op=admin_users");
   }
   if($f->{del_pending}=~/^\d+$/)
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my $users = $db->SelectARef("SELECT * FROM Users WHERE usr_status='PENDING' AND usr_created<CURDATE()-INTERVAL ? DAY",$f->{del_pending});
      for my $user (@$users)
      {
         my $files = $db->SelectARef("SELECT srv_id,file_code,file_id,file_real,file_real_id FROM Files WHERE usr_id=?",$user->{usr_id});
         $ses->DeleteFilesMass($files);
         $ses->DeleteUserDB($user->{usr_id});
      }
      $ses->redirect_msg("?op=admin_users","Deleted users: ".($#$users+1));
   }
   if($f->{del_inactive}=~/^\d+$/)
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my $users = $db->SelectARef("SELECT * FROM Users 
                                   WHERE usr_created<CURDATE()-INTERVAL ? DAY 
                                   AND usr_lastlogin<CURDATE() - INTERVAL ? DAY",$f->{del_inactive},$f->{del_inactive});
      for my $user (@$users)
      {
         my $files = $db->SelectARef("SELECT srv_id,file_code,file_id,file_real,file_real_id FROM Files WHERE usr_id=?",$user->{usr_id});
         $ses->DeleteFilesMass($files);
         $ses->DeleteUserDB($user->{usr_id});
      }
      $ses->redirect_msg("?op=admin_users","Deleted users: ".($#$users+1));
   }
   if($f->{del_users} && $f->{usr_id})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my $users = $db->SelectARef("SELECT * FROM Users WHERE usr_id IN (".join(',',@{&ARef($f->{usr_id})}).")");
      for my $user (@$users)
      {
         my $files = $db->SelectARef("SELECT srv_id,file_code,file_id,file_real,file_real_id FROM Files WHERE usr_id=?",$user->{usr_id});
         $ses->DeleteFilesMass($files);
         $ses->DeleteUserDB($user->{usr_id});
      }
      $ses->redirect("?op=admin_users");
   }
   if($f->{extend_premium_all})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      $db->Exec("UPDATE Users SET usr_premium_expire=usr_premium_expire + INTERVAL ? DAY WHERE usr_premium_expire>=NOW()",$f->{extend_premium_all});
      $ses->redirect("?op=admin_users");
   }
   if($f->{resend_activation})
   {
      my $user = $db->SelectRow("SELECT usr_id,usr_login FROM Users WHERE usr_id=?",$f->{resend_activation});
      $f->{d} = "$user->{usr_id}-$user->{usr_login}";
      &ResendActivationCode(1);
   }
   if($f->{activate})
   {
      $db->Exec("UPDATE Users SET usr_status='OK', usr_rapid_login='' WHERE usr_id=?",$f->{activate});
      $ses->redirect_msg("?op=admin_users","User activated");
   }

   $f->{sort_field}||='usr_created';
   $f->{sort_order}||='down';
   my $filter_key = "AND (usr_login LIKE '%$f->{key}%' OR usr_email LIKE '%$f->{key}%')" if $f->{key};
   $filter_key = "AND usr_lastip=INET_ATON('$f->{key}')" if $f->{key}=~/^\d+\.\d+\.\d+\.\d+$/;
   my $filter_prem= "AND usr_premium_expire>NOW()" if $f->{premium_only};
   my $filter_money= "AND usr_money>=$f->{money}" if $f->{money}=~/^[\d\.]+$/;
   my $users = $db->SelectARef("SELECT u.*,
                                       INET_NTOA(usr_lastip) as usr_ip,
                                       COUNT(f.file_id) as files,
                                       SUM(f.file_size) as disk_used,
                                       UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec,
                                       TO_DAYS(CURDATE())-TO_DAYS(usr_lastlogin) as last_visit
                                FROM Users u
                                LEFT JOIN Files f ON u.usr_id = f.usr_id
                                WHERE 1
                                $filter_key
                                $filter_prem
                                $filter_money
                                GROUP BY usr_id
                                ".&makeSortSQLcode($f,'usr_created').$ses->makePagingSQLSuffix($f->{page}) );
   my $totals = $db->SelectRow("SELECT COUNT(*) as total_count
                                FROM Users f WHERE 1 
                                $filter_key 
                                $filter_prem
                                $filter_money");

   for(@$users)
   {
      $_->{site_url} = $c->{site_url};
      $_->{disk_used} = $_->{disk_used} ? $ses->makeFileSize($_->{disk_used}) : '';
      $_->{premium} = $_->{exp_sec}>0;
      $_->{last_visit} = defined $_->{last_visit} ? "$_->{last_visit} $ses->{lang}->{lang_days_ago}" : $ses->{lang}->{lang_never};
      substr($_->{usr_created},-3)='';
      $_->{"status_$_->{usr_status}"}=1;
      $_->{usr_money} = $_->{usr_money}=~/^[0\.]+$/ ? '' : '$'.$_->{usr_money};
      $_->{usr_money}=~s/0+$//;
   }
   my %sort_hash = &makeSortHash($f,['usr_login','usr_email','files','usr_created','disk_used','last_visit','usr_money']);
   
   $ses->PrintTemplate("admin_users.html",
                       'users'  => $users,
                       %{$totals},
                       'key'    => $f->{key},
                       'premium_only' => $f->{premium_only},
                       'money' => $f->{money},
                       %sort_hash,
                       'paging' => $ses->makePagingLinks($f,$totals->{total_count}),
                      );
}

sub AdminUserEdit
{
    
    if($f->{save})
    {
       $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
       $db->Exec("UPDATE Users 
                  SET usr_login=?, 
                      usr_email=?, 
                      usr_premium_expire=?, 
                      usr_status=?, 
                      usr_money=?,
                      usr_disk_space=?,
                      usr_mod=?
                  WHERE usr_id=?",$f->{usr_login},$f->{usr_email},$f->{usr_premium_expire},$f->{usr_status},$f->{usr_money},$f->{usr_disk_space},$f->{usr_mod},$f->{usr_id});
       $db->Exec("UPDATE Users SET usr_password=ENCODE(?,'$c->{pasword_salt}') WHERE usr_id=?",$f->{usr_password},$f->{usr_id}) if $f->{usr_password};
       $ses->redirect("?op=admin_user_edit&usr_id=$f->{usr_id}");
    }
    my $user = $db->SelectRow("SELECT *, UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec, DECODE(usr_password,'$c->{pasword_salt}') as usr_password
                               FROM Users WHERE usr_id=?
                              ",$f->{usr_id});
    my $transactions = $db->SelectARef("SELECT * FROM Transactions WHERE usr_id=? AND verified=1 ORDER BY created DESC",$f->{usr_id});
    $_->{site_url}=$c->{site_url} for @$transactions;

    my $payments = $db->SelectARef("SELECT * FROM Payments WHERE usr_id=? ORDER BY created DESC",$f->{usr_id});

    my $referrals = $db->SelectARef("SELECT usr_id,usr_login,usr_created,usr_money,usr_aff_id 
                                     FROM Users 
                                     WHERE usr_aff_id=? 
                                     ORDER BY usr_created DESC 
                                     LIMIT 11",$f->{usr_id});
    $referrals->[10]->{more}=1 if $#$referrals>9;
    
    require Time::Elapsed;
    my $et  = new Time::Elapsed;
    $ses->PrintTemplate("admin_user_form.html",
                        %{$user},
                        expire_elapsed => $user->{exp_sec}>0 ? $et->convert($user->{exp_sec}) : '',
                        transactions   => $transactions,
                        payments       => $payments,
                        "status_$user->{usr_status}" => ' selected',
                        referrals      => $referrals,
                        m_d            => $c->{m_d},
                       );
}

sub AdminUserReferrals
{
   my $referrals = $db->SelectARef("SELECT usr_id,usr_login,usr_created,usr_money,usr_aff_id 
                                     FROM Users 
                                     WHERE usr_aff_id=? 
                                     ORDER BY usr_created DESC 
                                     ".$ses->makePagingSQLSuffix($f->{page}),$f->{usr_id});
   my $total = $db->SelectOne("SELECT COUNT(*) FROM Users WHERE usr_aff_id=?",$f->{usr_id});
   my $user = $db->SelectRow("SELECT usr_id,usr_login FROM Users WHERE usr_id=?",$f->{usr_id});
   $ses->PrintTemplate("admin_user_referrals.html",
                       referrals  => $referrals,
                       'paging' => $ses->makePagingLinks($f,$total),
                       %{$user},
                      );
}

sub AdminTorrents
{
   if($f->{del_torrent})
   {
      my $torr = $db->SelectRow("SELECT * FROM Torrents WHERE sid=?",$f->{del_torrent});
      $ses->redirect("$c->{site_url}/?op=admin_torrents") unless $torr;

      my $res = $ses->api2($torr->{srv_id},{
                                  op   => 'torrent_delete',
                                  sid  => $f->{del_torrent},
                                 });

      $ses->message("Error1:$res") unless $res eq 'OK';

      $db->Exec("DELETE FROM Torrents WHERE sid=? AND status='WORKING'",$f->{del_torrent});
      $ses->redirect("$c->{site_url}/?op=admin_torrents")
   }
   if($f->{'kill'})
   {
      $ses->api2($f->{srv_id},{op => 'torrent_kill'});
      $ses->redirect("$c->{site_url}/?op=admin_torrents");
   }

   my $servers = $db->SelectARef("SELECT * FROM Servers WHERE srv_torrent=1");
   for(@$servers)
   {
      my $res = $ses->api2($_->{srv_id},{ op => 'torrent_status' });
      $_->{active}=1 if $res eq 'ON';
   }

   my $torrents = $db->SelectARef("SELECT t.*, UNIX_TIMESTAMP()-UNIX_TIMESTAMP(t.created) as working, 
                                      u.usr_login
                               FROM Torrents t, Users u
                               WHERE t.status='WORKING'
                               AND t.usr_id=u.usr_id
                               ORDER BY created DESC
                               ");
   for my $t (@$torrents)
   {
      my @files = split("\n",$t->{files});
      $t->{file_list} = join('<br>',map{/^(.+):(\d+)$/;"$1 (<i>".sprintf("%.1f Mb",$2/1048576)."<\/i>)"}@files );
      $t->{file_list} =~ s/'/\\'/g;
      $t->{title}=$files[0];
      $t->{title}=~s/^(.+?)\/.+/$1/;
      $t->{title}=~s/:\d+$//;
      ($t->{done},$t->{total},$t->{down_speed},$t->{up_speed})=split(':',$t->{progress});
      $t->{percent}=sprintf("%.01f", 100*$t->{done}/$t->{total} );
      $t->{done} = sprintf("%.0f", $t->{done}/1048576 );
      $t->{total} = sprintf("%.0f", $t->{total}/1048576 );
      $t->{working} = $t->{working}>3600*3 ? sprintf("%.1f hours",$t->{working}/3600) : sprintf("%.0f mins",$t->{working}/60)
   }
   $ses->PrintTemplate("admin_torrents.html",
                       torrents  => $torrents,
                       servers   => $servers,
                      );
}

sub AdminServers
{
   my $servers = $db->SelectARef("SELECT s.*
                                  FROM Servers s
                                  ORDER BY srv_created
                                 ");
   for(@$servers)
   {
      $_->{srv_disk_percent} = sprintf("%.01f",100*$_->{srv_disk}/$_->{srv_disk_max});
      $_->{srv_disk} = sprintf("%.01f",$_->{srv_disk}/1073741824);
      $_->{srv_disk_max} = int $_->{srv_disk_max}/1073741824;
      my @a;
      push @a,"Regular" if $_->{srv_allow_regular};
      push @a,"Premium" if $_->{srv_allow_premium};
      $_->{user_types} = join '<br>', @a;
   }
   $ses->PrintTemplate("admin_servers.html",
                       'servers'  => $servers,
                      );
}

sub AdminServerAdd
{
   
   $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
   my $server;
   if($f->{srv_id})
   {
      $server = $db->SelectRow("SELECT * FROM Servers WHERE srv_id=?",$f->{srv_id});
      $server->{srv_disk_max}/=1024*1024*1024;
      $server->{"s_$server->{srv_status}"}=' selected';
   }
   elsif(!$db->SelectOne("SELECT srv_id FROM Servers LIMIT 1"))
   {
      $server->{srv_cgi_url}    = $c->{site_cgi};
      $server->{srv_htdocs_url} = "$c->{site_url}/files";
   }
   $server->{srv_allow_regular}=$server->{srv_allow_premium}=1 unless $f->{srv_id};

   $ses->PrintTemplate("admin_server_form.html",
                       %{$server},
                       'mmtt' => $ses->iPlg('t'),
                      );
}

sub AdminServerSave
{
   
   $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
   my (@tests,@arr);
   my $allow_save=1;
   require LWP::UserAgent;
   my $ua = LWP::UserAgent->new(timeout => 15,agent=>'Opera/9.51 (Windows NT 5.1; U; en)');
   $f->{srv_cgi_url}=~s/\/$//;
   $f->{srv_htdocs_url}=~s/\/$//;
   $ses->message("Server with same cgi-bin URL / htdocs URL already exist in DB") if !$f->{srv_id} && $db->SelectOne("SELECT srv_id FROM Servers WHERE srv_cgi_url=? OR srv_htdocs_url=?",$f->{srv_cgi_url},$f->{srv_htdocs_url});

   # max disk usage
   push @tests, 'max disk usage: ERROR' if !$f->{srv_disk_max} || $f->{srv_disk_max}<=0;

   $f->{srv_allow_regular}||=0;
   $f->{srv_allow_premium}||=0;
   $f->{srv_torrent}||=0;

   my @sflds = qw(srv_name srv_ip srv_cgi_url srv_htdocs_url srv_disk_max srv_status srv_key srv_allow_regular srv_allow_premium srv_torrent);
   $f->{srv_disk_max}*=1024*1024*1024;
   if($f->{srv_id})
   {
      my @dat = map{$f->{$_}}@sflds;
      push @dat, $f->{srv_id};
      $db->Exec("UPDATE Servers SET ".join(',',map{"$_=?"}@sflds)." WHERE srv_id=?", @dat );
      $c->{srv_status} = $f->{srv_status};
      my $data = join('~',map{"$_:$c->{$_}"}qw(site_url site_cgi max_upload_files max_upload_filesize ip_not_allowed srv_status));
      $ses->api2($f->{srv_id},{op=>'update_conf',data=>$data});
   }

   my $fs_key = $db->SelectOne("SELECT srv_key FROM Servers WHERE srv_id=?",$f->{srv_id}) if $f->{srv_id};

   # api.cgi multiple tests
   my $res = $ses->api($f->{srv_cgi_url}, {op => 'test', fs_key=>$fs_key, site_cgi=>$c->{site_cgi}} );
   if($res=~/^OK/)
   {
      push @tests, 'api.cgi: OK';
      $res=~s/^OK:(.*?)://;
      $f->{srv_ip} = $1;
      push @tests, split(/\|/,$res);
   }
   else
   {
      push @tests, "api.cgi: ERROR ($res)";
   }

   # upload.cgi
   $res = $ua->get("$f->{srv_cgi_url}/upload.cgi?mode=test");
   push @tests, $res->content eq 'XFS' ? 'upload.cgi: OK' : "upload.cgi: ERROR (problems with <a href='$f->{srv_cgi_url}/upload.cgi\?mode=test' target=_blank>link</a>)";

   # upload_status.cgi
   #my $res = $ua->get("$f->{srv_cgi_url}/upload_status.cgi?mode=test");
   #push @tests, $res->content eq 'XFS' ? 'upload_status.cgi: OK' : "upload_status.cgi: ERROR (problems with <a href='$f->{srv_cgi_url}/upload_status.cgi\?mode=test' target=_blank>link</a>)";

   # htdocs URL accessibility
   $res = $ua->get("$f->{srv_htdocs_url}/index.html");
   push @tests, $res->content eq 'XFS' ? 'htdocs URL accessibility: OK' : "htdocs URL accessibility: ERROR (should see XFS on <a href='$f->{srv_htdocs_url}/index.html' target=_blank>link</a>)";

   for(@tests)
   {
      $allow_save=0 if /ERROR/;
      push @arr, {'text' => $_,
                  'class'=> /ERROR/ ? 'err' : 'ok'
                 };
   }

   unless($allow_save)
   {
      $f->{srv_disk_max}/=1024*1024*1024;
      $ses->PrintTemplate("admin_server_form.html",
                          'tests'      => \@arr,
                          %{$f},
                          "s_$f->{srv_status}" => ' selected',
                         );
   }

   unless($f->{srv_id})
   {
      $f->{srv_key} = $c->{fs_key} = $ses->randchar(8);
      $c->{srv_status} = $f->{srv_status};
      #my @sflds = qw(srv_name srv_ip srv_cgi_url srv_htdocs_url srv_key srv_disk_max srv_status srv_allow_regular srv_allow_premium srv_torrent);
      $db->Exec("INSERT INTO Servers SET srv_created=CURDATE(), ".join(',',map{"$_=?"}@sflds), map{$f->{$_}}@sflds );
      my $data = join('~',map{"$_:$c->{$_}"}qw(fs_key dl_key site_url site_cgi max_upload_files max_upload_filesize ext_allowed ext_not_allowed ip_not_allowed srv_status));
      my $res = $ses->api($f->{srv_cgi_url},{op=>'update_conf',data=>$data});
      $ses->message("Server created. But was unable to update FS config.<br>Probably fs_key was not epty. Update fs_key manually and save Site Settings to sync.($res)") unless $res eq 'OK';
   }

   $ses->redirect('?op=admin_servers');
}

sub AdminCheckDBFile
{
   
   $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
   $|++;
   print"Content-type:text/html\n\n<HTML><BODY>";
   print"Starting DB-File consistancy check...<br><br>";

   my $servers = $db->SelectARef("SELECT * FROM Servers WHERE srv_status<>'OFF' ");
   my $deleted_db=0;
   for my $s (@$servers)
   {
      print"Server $s->{srv_name} (ID=$s->{srv_id})<br>";
      my $cx=0;
      while( my $files=$db->Select("SELECT file_id, file_real_id, file_real
                                    FROM Files
                                    WHERE srv_id=? LIMIT $cx,100",$s->{srv_id}) )
      {
         $cx+=100;
         $files=&ARef($files);
         $_->{file_real_id}||=$_->{file_id} for @$files;
         my $list = join ':', map{ "$_->{file_real_id}-$_->{file_real}" } @$files;
         my $res = $ses->api($s->{srv_cgi_url},
                             {
                                fs_key => $s->{srv_key},
                                op     => 'check_files',
                                list   => $list,
                             }
                            );
         $ses->AdminLog("Error when requesting API.<br>$res") unless $res=~/^OK/;
         my ($codes) = $res=~/^OK:(.*)$/;
         my $ids = join ',', map{"'$_'"} split(/\,/,$codes);
         if($ids)
         {
            my $list = $db->SelectARef("SELECT * FROM Files WHERE file_real IN ($ids)");
            $ses->DeleteFilesMass($list);
            $deleted_db+=$#$list+1;
         }
         print"+";
      }
      print"<br>Files removed from DB: $deleted_db<br><br>";
   }
   print"DONE.<br><br><a href='$c->{site_url}/?op=admin_servers'>Back to site</a>";
   print"</BODY></HTML>";
   exit;
}

sub AdminCheckFileDB
{
   
   $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
   $|++;
   print"Content-type:text/html\n\n<HTML><BODY>";
   print"Starting File-DB consistancy check...<br><br>";
   my $servers = $db->SelectARef("SELECT * FROM Servers WHERE srv_status<>'OFF' ");
   my $deleted_db=0;
   for my $s (@$servers)
   {
      print"Server $s->{srv_name} (ID=$s->{srv_id})<br>";
      my $res = $ses->api2($s->{srv_id}, { op => 'check_files_reverse' } );
      #$ses->AdminLog("Error when requesting API check_files_reverse.<br>$res") unless $res=~/^OK:/;
      #$res=~/^OK:(.*)$/ ? print" OK. Found & fixed bad files2: $1<br>" : print" Error: $res";
      print"<br>";
   }
   print"DONE.<br><br><a href='$c->{site_url}/?op=admin_servers'>Back to site</a>";
   print"</BODY></HTML>";
   exit;
}

sub AdminUpdateServerStats
{
   
   $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
   my $servers = $db->SelectARef("SELECT * FROM Servers WHERE srv_status<>'OFF' ");
   for my $s (@$servers)
   {
      my $res = $ses->api($s->{srv_cgi_url},
                          {
                             fs_key => $s->{srv_key},
                             op     => 'get_file_stats',
                          }
                         );
      $ses->message("Error when requesting API.<br>$res") unless $res=~/^OK/;
      my ($files,$size) = $res=~/^OK:(\d+):(\d+)$/;
      $ses->message("Invalid files,size values: ($files)($size)") unless $files=~/^\d+$/ && $size=~/^\d+$/;
      my $file_count = $db->SelectOne("SELECT COUNT(*) FROM Files WHERE srv_id=?",$s->{srv_id});
      $db->Exec("UPDATE Servers SET srv_files=?, srv_disk=? WHERE srv_id=?",$file_count,$size,$s->{srv_id});
   }
   $ses->redirect('?op=admin_servers');
}

sub AdminServerImport
{
   
   if($f->{'import'})
   {
      my $usr_id = $db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{usr_login});
      $ses->message("No such user '$f->{usr_login}'") unless $usr_id;
      my $res = $ses->api2($f->{srv_id},{op=>'import_list_do','usr_id'=>$usr_id,'pub'=>$f->{pub}});
      $ses->message("Error happened: $res") unless $res=~/^OK/;
      $res=~/^OK:(\d+)/;
      $ses->message("$1 files were completely imported to system");
   }
   my $res = $ses->api2($f->{srv_id},{op=>'import_list'});
   $ses->message("Error when requesting API.<br>$res") unless $res=~/^OK/;
   my ($data) = $res=~/^OK:(.*)$/;
   my @files;
   for(split(/:/,$data))
   {
      /^(.+?)\-(\d+)$/;
      push @files, {name=>$1,size=>sprintf("%.02f Mb",$2/1048576)};
   }
   $ses->PrintTemplate("admin_server_import.html",
                       'files'   => \@files,
                       'srv_id'  => $f->{srv_id},
                      );
}

sub AdminServerDelete
{
   $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
   
   if($f->{password})
   {
      $f->{login}=$ses->getUser->{usr_login};
      $ses->message("Wrong password") unless &Login('no_redirect');
   }
   else
   {
      $ses->PrintTemplate("confirm_password.html",
                          'msg'=>"Delete File Server and all files on it?",
                          'btn'=>"DELETE",
                          'op'=>'admin_server_del',
                          'id'=>$f->{srv_id});
   }

   my $srv = $db->SelectRow("SELECT * FROM Servers WHERE srv_id=?",$f->{id});
   $ses->message("No such server") unless $srv;

   my $res = $ses->api($srv->{srv_cgi_url},
                       {
                          fs_key => $srv->{srv_key},
                          op     => 'expire_sym',
                          hours  => 0,
                       }
                      );

   my $files = $db->SelectARef("SELECT srv_id,file_id,file_real,file_real_id FROM Files WHERE srv_id=?",$srv->{srv_id});
   $ses->DeleteFilesMass($files);

   $db->Exec("DELETE FROM Servers WHERE srv_id=?",$srv->{srv_id});

   $ses->redirect('?op=admin_servers');
}

sub AdminSettings
{
   if($f->{save})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      my @fields = qw(license_key
                      site_name
                      enable_file_descr
                      enable_file_comments
                      ext_allowed
                      ext_not_allowed
                      ip_not_allowed
                      fnames_not_allowed
                      captcha_mode
                      email_from
                      contact_email
                      symlink_expire
                      items_per_page
                      payment_plans
                      paypal_email
                      alertpay_email
                      item_name
                      currency_code
                      link_format
                      enable_catalogue
                      pre_download_page
                      bw_limit_days
                      registration_confirm_email
                      mailhosts_not_allowed
                      sanitize_filename
                      bad_comment_words
                      add_filename_postfix
                      image_mod
                      mp3_mod
                      mp3_mod_no_download
                      mp3_mod_autoplay
                      recaptcha_pub_key
                      recaptcha_pri_key
                      coupons
                      tla_xml_key
                      m_i
                      m_v
                      m_r
                      m_w
                      m_s
                      m_d
                      m_a
                      m_d_f
                      m_d_a
                      m_d_c
                      m_s_reg
                      m_v_page
                      m_i_width
                      m_i_height
                      m_i_resize
                      m_i_wm_position
                      m_i_wm_image
                      m_i_wm_padding
                      m_i_hotlink_orig
                      m_u
                      webmoney_merchant_id
                      webmoney_secret_key
                      ping_google_sitemaps
                      deurl_site
                      deurl_api_key
                      smscoin_id
                      show_last_news_days
                      link_ip_logic
                      daopay_app_id
                      cashu_merchant_id
                      paypal_subscription
                      m_h
                      m_h_login
                      m_h_password
                      m_v_width
                      m_v_height
                      m_n
                      rs_logins
                      mu_logins
                      nl_logins
                      hf_logins
                      mf_logins
                      fs_logins
                      df_logins
                      ff_logins
                      es_logins
                      sm_logins
                      ug_logins
                      fe_logins
                      payout_systems
                      m_e
                      m_e_vid_width
                      m_e_vid_quality
                      m_e_audio_bitrate
                      m_b

                      enabled_anon
                      max_upload_files_anon
                      max_upload_filesize_anon
                      max_downloads_number_anon
                      download_countdown_anon
                      captcha_anon
                      ads_anon
                      add_download_delay_anon
                      bw_limit_anon
                      remote_url_anon
                      direct_links_anon
                      down_speed_anon
                      max_download_filesize_anon
                      video_embed_anon
                      flash_upload_anon
                      files_expire_access_anon
                      file_dl_delay_anon
                      mp3_embed_anon
                      rar_info_anon

                      enabled_reg
                      max_upload_files_reg
                      disk_space_reg
                      max_upload_filesize_reg
                      max_downloads_number_reg
                      download_countdown_reg
                      captcha_reg
                      ads_reg
                      add_download_delay_reg
                      bw_limit_reg
                      remote_url_reg
                      direct_links_reg
                      down_speed_reg
                      max_download_filesize_reg
                      max_rs_leech_reg
                      torrent_dl_reg
                      torrent_dl_slots_reg
                      video_embed_reg
                      flash_upload_reg
                      files_expire_access_reg
                      file_dl_delay_reg
                      mp3_embed_reg
                      rar_info_reg

                      enabled_prem
                      max_upload_files_prem
                      disk_space_prem
                      max_upload_filesize_prem
                      max_downloads_number_prem
                      download_countdown_prem
                      captcha_prem
                      ads_prem
                      add_download_delay_prem
                      bw_limit_prem
                      remote_url_prem
                      direct_links_prem
                      down_speed_prem
                      max_download_filesize_prem
                      max_rs_leech_prem
                      torrent_dl_prem
                      torrent_dl_slots_prem
                      video_embed_prem
                      flash_upload_prem
                      files_expire_access_prem
                      file_dl_delay_prem
                      mp3_embed_prem
                      rar_info_prem

                      tier_sizes
                      tier1_countries
                      tier2_countries
                      tier1_money
                      tier2_money
                      tier3_money
                      image_mod_no_download
                      video_mod_no_download
                      external_links
                      show_server_stats
                      clean_ip2files_days
                      anti_dupe_system
                      two_checkout_sid
                      plimus_contract_id
                      moneybookers_email
                      max_money_last24
                      sale_aff_percent
                      referral_aff_percent
                      min_payout
                      del_money_file_del
                      convert_money
                      convert_days
                      money_filesize_limit
                      dl_money_anon
                      dl_money_reg
                      dl_money_prem
                     );

            my @fields_fs = qw(site_url 
                         site_cgi 
                         ext_allowed 
                         ext_not_allowed 
                         ip_not_allowed
                         dl_key
                         m_i
                         m_v
                         m_r
                         m_i_width
                         m_i_height
                         m_i_resize
                         m_i_wm_position
                         m_i_wm_image
                         m_i_wm_padding
                         m_i_hotlink_orig
                         m_h
                         m_h_login
                         m_h_password
                         rs_logins
                         mu_logins
                         nl_logins
                         hf_logins
                         mf_logins
                         fs_logins
                         df_logins
                         ff_logins
                         es_logins
                         sm_logins
                         ug_logins
                         fe_logins
                         m_e
                         m_e_vid_width
                         m_e_vid_quality
                         m_e_audio_bitrate
                         m_b

                         enabled_anon
                         max_upload_files_anon
                         max_upload_filesize_anon
                         remote_url_anon

                         enabled_reg
                         max_upload_files_reg
                         max_upload_filesize_reg
                         remote_url_reg

                         enabled_prem
                         max_upload_files_prem
                         max_upload_filesize_prem
                         remote_url_prem
                        );
      $f->{payment_plans}=~s/\s//gs;
      $f->{item_name} = $ses->{cgi_query}->url_encode($f->{item_name});

      my $conf;
      open(F,"$c->{cgi_path}/XFileConfig.pm")||$ses->message("Can't read XFileConfig");
      $conf.=$_ while <F>;
      close F;

      $f->{ip_not_allowed}=~s/\r//gs;
      my @ips=grep{/^[\d\.]+$/}split(/\n/,$f->{ip_not_allowed});
      if($#ips>-1 && open(F,"$c->{site_path}/.htaccess"))
      {
         my @arr=<F>;
         @arr=grep{$_!~/deny from/i}@arr;
         unshift @arr,"deny from $_\n" for @ips;
         close F;
         if( open(F,">$c->{site_path}/.htaccess") )
         {
            print F @arr;
            close F;
         }
      }

      $f->{external_links}=~s/\r//gs;
      $f->{external_links}=~s/\n/~/gs;
      $f->{external_links}=~s/'/&#39;/gs;

      $f->{ip_not_allowed}=~s/\r//gs;
      $f->{ip_not_allowed}=~s/\n/|/gs;
      $f->{ip_not_allowed}=~s/\|{2,99}/|/gs;
      $f->{ip_not_allowed}=~s/\|$//gs;
      $f->{ip_not_allowed}=~s/\*/\\d+/gs;
      $f->{ip_not_allowed}="^($f->{ip_not_allowed})\$" if $f->{ip_not_allowed};

      $f->{fnames_not_allowed}=~s/\r//gs;
      $f->{fnames_not_allowed}=~s/\n/|/gs;
      $f->{fnames_not_allowed}=~s/\|{2,99}/|/gs;
      $f->{fnames_not_allowed}=~s/\|$//gs;
      $f->{fnames_not_allowed}="($f->{fnames_not_allowed})" if $f->{fnames_not_allowed};

      $f->{mailhosts_not_allowed}=~s/\r//gs;
      $f->{mailhosts_not_allowed}=~s/\n/|/gs;
      $f->{mailhosts_not_allowed}=~s/\|{2,99}/|/gs;
      $f->{mailhosts_not_allowed}=~s/\|$//gs;
      $f->{mailhosts_not_allowed}="($f->{mailhosts_not_allowed})" if $f->{mailhosts_not_allowed};

      $f->{bad_comment_words}=~s/\r//gs;
      $f->{bad_comment_words}=~s/\n/|/gs;
      $f->{bad_comment_words}=~s/\|{2,99}/|/gs;
      $f->{bad_comment_words}=~s/\|$//gs;
      $f->{bad_comment_words}="($f->{bad_comment_words})" if $f->{bad_comment_words};

      $f->{coupons}=~s/\r//gs;
      $f->{coupons}=~s/\n/|/gs;
      $f->{coupons}=~s/\|{2,99}/|/gs;
      $f->{coupons}=~s/\|$//gs;

      for(qw(rs mu nl hf mf fs df ff es sm ug))
      {
         $f->{"$_\_logins"}=~s/\r//gs;
         $f->{"$_\_logins"}=~s/\n/|/gs;
         $f->{"$_\_logins"}=~s/\|{2,99}/|/gs;
         $f->{"$_\_logins"}=~s/\|$//gs;
      }

      for my $x (@fields)
      {
         my $val = $f->{$x};
         
         $conf=~s/$x\s*=>\s*('.*?')\s*,/"$x => '$val',"/e;
      }
      open(F,">$c->{cgi_path}/XFileConfig.pm")||$ses->message("Can't write XFileConfig");
      print F $conf;
      close F;

      $f->{site_url}=$c->{site_url};
      $f->{site_cgi}=$c->{site_cgi};
      $f->{dl_key}  =$c->{dl_key};

      my $data = join('~',map{"$_:$f->{$_}"}@fields_fs);
      
      my $servers = $db->SelectARef("SELECT * FROM Servers WHERE srv_status<>'OFF'");
      $|++;
      print"Content-type:text/html\n\n<HTML><BODY style='font:13px Arial;background:#eee;text-align:center;'>Have ".($#$servers+1)." servers to update.<br><br>";
      my $failed=0;
      for(@$servers)
      {
         print"ID=$_->{srv_id} $_->{srv_name}...";
         my $res = $ses->api($_->{srv_cgi_url},{ fs_key=>$_->{srv_key}, op=>'update_conf', data=>$data });
         if($res eq 'OK')
         {
            print"OK<br>";
         }
         else
         {
            print"FAILED!<br>";
            $failed++;
         }
         #$ses->message("Can't update config for server ID: $_->{srv_id}:$res") unless $res eq 'OK';
      }
      print"<br><br>Done.<br>$failed servers failed to update.<br><br><a href='?op=admin_settings'>Back to Site Settings</a>";
      print"<Script>window.location='$c->{site_url}/?op=admin_settings';</Script>" unless $failed;
      print"</BODY></HTML>";
      exit;
      #print $ses->redirect('?op=admin_settings');
   }

   $c->{ip_not_allowed}=~s/[\^\(\)\$\\]//g;
   $c->{ip_not_allowed}=~s/\|/\n/g;
   $c->{ip_not_allowed}=~s/d\+/*/g;
   $c->{fnames_not_allowed}=~s/[\^\(\)\$\\]//g;
   $c->{fnames_not_allowed}=~s/\|/\n/g;
   $c->{mailhosts_not_allowed}=~s/[\^\(\)\$\\]//g;
   $c->{mailhosts_not_allowed}=~s/\|/\n/g;
   $c->{bad_comment_words}=~s/[\^\(\)\$\\]//g;
   $c->{bad_comment_words}=~s/\|/\n/g;
   $c->{coupons}=~s/\|/\n/g;
   $c->{"link_format$c->{link_format}"}=' selected';
   $c->{"enp_$_"}=$ses->iPlg($_) for split('',$ses->{plug_lett});
   #die $c->{"enp_h"};
   $c->{tier_sizes}||='0|10|100';
   $c->{tier1_countries}||='US|CA';
   $c->{tier1_money}||='1|2|3';
   $c->{tier2_countries}||='DE|FR|GB';
   $c->{tier2_money}||='1|2|3';
   $c->{tier3_money}||='1|2|3';
   $c->{"lil_$c->{link_ip_logic}"}=' checked';
   $c->{external_links}=~s/~/\n/gs;
   $c->{"m_i_wm_position_$c->{m_i_wm_position}"}=1;
   $c->{m_m} = $ses->iPlg('m');
   $c->{cliid} = $ses->{cliid};
   $c->{"m_v_page_".$c->{m_v_page}}=1;
   for(qw(rs mu nl hf mf fs df ff es sm ug))
   {
      $c->{"$_\_logins"}=~s/\|/\n/g;
   }

   if($c->{tla_xml_key})
   {
      my $chmod = (stat("$c->{cgi_path}/Templates/text-link-ads.html"))[2] & 07777;
      my $chmod_txt = sprintf("%04o", $chmod);
      $c->{tla_msg}="Set chmod 666 to this file: Templates/text-link-ads.html" unless $chmod_txt eq '0666';
   }
   

   #push @{$f->{cookies}}, cookie(-name=>'admhash',-value=>$passcook,-expire=>'+30m');
   $ses->PrintTemplate("admin_settings.html",
                       %{$c},
                       "captcha_$c->{captcha_mode}" => ' checked',
                       'item_name'     => $ses->{cgi_query}->url_decode($c->{item_name}),
                      );
}

sub MyReports
{
   $ses->message("Not allowed") unless $c->{m_s};
   $ses->message("Premium account required") if !$ses->getUser->{premium} && !$c->{m_s_reg};
   my @d1 = $ses->getTime();
   $d1[2]='01';
   my @d2 = $ses->getTime();
   my $day1 = $f->{date1}=~/^\d\d\d\d-\d\d-\d\d$/ ? $f->{date1} : "$d1[0]-$d1[1]-$d1[2]";
   my $day2 = $f->{date2}=~/^\d\d\d\d-\d\d-\d\d$/ ? $f->{date2} : "$d2[0]-$d2[1]-$d2[2]";
   my $list = $db->SelectARef("SELECT *, DATE_FORMAT(day,'%e') as day2
                               FROM Stats2
                               WHERE usr_id=?
                               AND day>=?
                               AND  day<=?
                               ORDER BY day",$ses->getUserId,$day1,$day2);
   $ses->message("Not enough reports data") if $#$list<0;
   my %totals;
   my (@days,@profit_dl,@profit_sales,@profit_refs);
   for my $x (@$list)
   {
      $x->{profit_total} = $x->{profit_dl}+$x->{profit_sales}+$x->{profit_refs};
      for(qw(profit_dl profit_sales profit_refs profit_total))
      {
         $x->{$_}=~s/\.?0+$//;
      }
      $totals{"sum_$_"}+=$x->{$_} for qw(downloads sales profit_dl profit_sales profit_refs profit_total);
   }

   my $divlines = $#$list-1;
   $divlines=1 if $divlines<1;
   my $xml = $ses->CreateTemplate("my_reports.xml");
   $xml->param(list=>$list, divlines=>$divlines);
   my $data_xml = $xml->output;
   $data_xml=~s/[\n\r]+//g;
   $data_xml=~s/\s{2,16}/ /g;

   $ses->PrintTemplate("my_reports.html",
                       list => $list,
                       date1 => $day1,
                       date2 => $day2,
                       %totals,
                       data_xml => $data_xml,
                      );
}

sub AdminStats
{
   my @d1 = $ses->getTime(time-10*24*3600);
   my @d2 = $ses->getTime();
   my $day1 = $f->{date1}=~/^\d\d\d\d-\d\d-\d\d$/ ? $f->{date1} : "$d1[0]-$d1[1]-$d1[2]";
   my $day2 = $f->{date2}=~/^\d\d\d\d-\d\d-\d\d$/ ? $f->{date2} : "$d2[0]-$d2[1]-$d2[2]";
   my $list = $db->SelectARef("SELECT *, ROUND(bandwidth/1048576) as bandwidth, DATE_FORMAT(day,'%b%e') as x
                               FROM Stats
                               WHERE day>=?
                               AND  day<=?",$day1,$day2);
   $ses->message("Not enough stat data") if $#$list<1;
   my $dxp=sprintf("%.01f",100/$#$list);
   my ($max_up,$max_dl,$max_reg,$max_pay,$max_bw);
   for(@$list)
   {
      $max_up= $_->{uploads}     if $_->{uploads}>$max_up;
      $max_dl= $_->{downloads}   if $_->{downloads}>$max_dl;
      $max_reg=$_->{registered}  if $_->{registered}>$max_reg;
      $max_bw= $_->{bandwidth}   if $_->{bandwidth}>$max_bw;
      $max_pay=$_->{paid}        if $_->{paid}>$max_pay;
   }
   $max_up||=1;
   $max_dl||=1;
   $max_bw||=1;
   $max_reg||=1;
   $max_pay||=1;
   my $url="http://chart.apis.google.com/chart?cht=lc&chco=303030&chls=1,1,0&chs=500x200&chxt=x,y&chg=$dxp,25";

   my $up_url=$url."&chtt=File+uploads&chd=t:".join(',', map{sprintf("%.01f",100*$_->{uploads}/$max_up)}@$list );
      $up_url.="&chxl=0:|".join('|', map{$_->{x}}@$list )."|1:|0|".int($max_up/4)."|".int($max_up/2)."|".int(3*$max_up/4)."|$max_up";

   my $dl_url=$url."&chtt=File+downloads&chd=t:".join(',', map{sprintf("%.01f",100*$_->{downloads}/$max_dl)}@$list );
      $dl_url.="&chxl=0:|".join('|', map{$_->{x}}@$list )."|1:|0|".int($max_dl/4)."|".int($max_dl/2)."|".int(3*$max_dl/4)."|$max_dl";

   my $reg_url=$url."&chtt=New+users&chd=t:".join(',', map{sprintf("%.01f",100*$_->{registered}/$max_reg)}@$list );
      $reg_url.="&chxl=0:|".join('|', map{$_->{x}}@$list )."|1:|0|".int($max_reg/4)."|".int($max_reg/2)."|".int(3*$max_reg/4)."|$max_reg";

   my $bw_url=$url."&chtt=Bandwidth,+Mb&chd=t:".join(',', map{sprintf("%.01f",100*$_->{bandwidth}/$max_bw)}@$list );
      $bw_url.="&chxl=0:|".join('|', map{$_->{x}}@$list )."|1:|0|".int($max_bw/4)."|".int($max_bw/2)."|".int(3*$max_bw/4)."|$max_bw";

   my $pay_url=$url."&chtt=Payments+received&chd=t:".join(',', map{sprintf("%.01f",100*$_->{paid}/$max_pay)}@$list );
      $pay_url.="&chxl=0:|".join('|', map{$_->{x}}@$list )."|1:|0|".int($max_pay/4)."|".int($max_pay/2)."|".int(3*$max_pay/4)."|$max_pay";

   $ses->PrintTemplate("admin_stats.html",
                       'up_url'     => $up_url,
                       'dl_url'     => $dl_url,
                       'reg_url'    => $reg_url,
                       'bw_url'     => $bw_url,
                       'pay_url'    => $pay_url,
                       'date1'      => $day1,
                       'date2'      => $day2,
                      );
}

sub AdminComments
{
   $ses->message("Access denied") if !$ses->getUser->{usr_adm} && !($c->{m_d} && $ses->getUser->{usr_mod} && $c->{m_d_c});
   if($f->{del_selected} && $f->{cmt_id})
   {
      $db->Exec("DELETE FROM Comments WHERE cmt_id IN (".join(',',@{&ARef($f->{cmt_id})}).")");
      $ses->redirect("?op=admin_comments");
   }
   if($f->{rr})
   {
      $ses->redirect( &CommentRedirect(split(/-/,$f->{rr})) );
   }
   my $filter;
   $filter="WHERE c.cmt_ip=INET_ATON('$f->{ip}')" if $f->{ip};
   $filter="WHERE c.usr_id=$f->{usr_id}" if $f->{usr_id};
   $filter="WHERE c.cmt_name LIKE '%$f->{key}%' OR c.cmt_email LIKE '%$f->{key}%' OR c.cmt_text LIKE '%$f->{key}%'" if $f->{key};
   my $list = $db->SelectARef("SELECT c.*, INET_NTOA(c.cmt_ip) as ip, u.usr_login, u.usr_id
                               FROM Comments c
                               LEFT JOIN Users u ON c.usr_id=u.usr_id
                               $filter
                               ORDER BY created DESC".$ses->makePagingSQLSuffix($f->{page},$f->{per_page}));
   my $total = $db->SelectOne("SELECT COUNT(*) FROM Comments c $filter");
   $ses->PrintTemplate("admin_comments.html",
                       'list'   => $list,
                       'key'    => $f->{key}, 
                       'paging' => $ses->makePagingLinks($f,$total),
                      );
}

sub AdminPayments
{
   
   if($f->{export_file} && $f->{pay_id})
   {
      my $list = $db->SelectARef("SELECT p.*, u.usr_id, u.usr_pay_email, u.usr_pay_type
                                  FROM Payments p, Users u
                                  WHERE id IN (".join(',',@{&ARef($f->{pay_id})}).")
                                  AND status='PENDING'
                                  AND p.usr_id=u.usr_id");
      my $date = sprintf("%d-%d-%d",&getTime());
      print qq{Content-Type: application/octet-stream\n};
      print qq{Content-Disposition: attachment; filename="paypal-mass-pay-$date.txt"\n};
      print qq{Content-Transfer-Encoding: binary\n\n};
      for my $x (@$list)
      {
         next unless $x->{usr_pay_type} =~ /paypal/i;
         print"$x->{usr_pay_email}\t$x->{amount}\t$c->{currency_code}\tmasspay_$x->{usr_id}\tPayment\r\n";
      }
      exit;
   }
   if($f->{mark_paid} && $f->{pay_id})
   {
      $db->Exec("UPDATE Payments SET status='PAID' WHERE id IN (".join(',',@{&ARef($f->{pay_id})}).")" );
      $ses->redirect_msg("$c->{site_url}/?op=admin_payments","Selected payments marked as Paid");
   }
   if($f->{mark_rejected} && $f->{pay_id})
   {
      $db->Exec("UPDATE Payments SET status='REJECTED' WHERE id IN (".join(',',@{&ARef($f->{pay_id})}).")" );
      $ses->redirect_msg("$c->{site_url}/?op=admin_payments","Selected payments marked as Rejected");
   }

   my $list = $db->SelectARef("SELECT p.*, u.usr_login, u.usr_email, u.usr_pay_email, u.usr_pay_type
                               FROM Payments p, Users u
                               WHERE status='PENDING'
                               AND p.usr_id=u.usr_id
                               ORDER BY created");
#  for(@$list)
#  {
#     $_->{"info_$_->{usr_pay_type}"} = $_->{usr_pay_email};
#  }
   my $amount_sum = $db->SelectOne("SELECT SUM(amount) FROM Payments WHERE status='PENDING'");
   $ses->PrintTemplate("admin_payments.html",
                       'list' => $list,
                       'amount_sum' => $amount_sum,
                       'paypal_email'        => $c->{paypal_email},
                       'alertpay_email'      => $c->{alertpay_email},
                       'webmoney_merchant_id'=> $c->{webmoney_merchant_id},
                       );
}

sub MyAccount
{
   if($f->{twitter1})
   {
      require Net::Twitter::Lite;
      my $nt = Net::Twitter::Lite->new(consumer_key    => $c->{twit_consumer1},
                                       consumer_secret => $c->{twit_consumer2} );
      my $url = $nt->get_authorization_url(callback => "$c->{site_url}/?op=my_account&twitter2=1");
      $ses->setCookie('tw_token',$nt->request_token);
      $ses->setCookie('tw_token_secret',$nt->request_token_secret);
      $ses->redirect($url);
   }
   if($f->{twitter2})
   {
      use Net::Twitter::Lite;
      my $nt = Net::Twitter::Lite->new(consumer_key    => $c->{twit_consumer1},
                                       consumer_secret => $c->{twit_consumer2});

      $nt->request_token( $ses->getCookie('tw_token') );
      $nt->request_token_secret( $ses->getCookie('tw_token') );
      my($access_token, $access_token_secret, $user_id, $screen_name) = $nt->request_access_token(verifier => $f->{oauth_verifier});

      if($access_token && $access_token_secret)
      {
         $db->Exec("INSERT INTO UserData SET usr_id=?, name=?, value=? 
                    ON DUPLICATE KEY UPDATE value=?",$ses->getUserId, 'twitter_login', $access_token, $access_token);
         $db->Exec("INSERT INTO UserData SET usr_id=?, name=?, value=? 
                    ON DUPLICATE KEY UPDATE value=?",$ses->getUserId, 'twitter_password', $access_token_secret, $access_token_secret);
      }
   }
   if($f->{twitter_stop})
   {
      $db->Exec("DELETE FROM UserData WHERE usr_id=? AND name IN ('twitter_login','twitter_password')",$ses->getUserId);
      $ses->redirect('?op=my_account');
   }
   if($f->{settings_save})
   {
      $ses->message("Not allowed in Demo mode!") if $c->{demo_mode} && $ses->getUser->{usr_adm};
      my $user=$db->SelectRow("SELECT usr_login,DECODE(usr_password,?) as usr_password,usr_email FROM Users WHERE usr_id=?",$c->{pasword_salt},$ses->getUserId);
      if($f->{usr_login} && $user->{usr_login}=~/^\d+$/ && $f->{usr_login} ne $user->{usr_login})
      {
         $f->{usr_login}=$ses->SecureStr($f->{usr_login});
         $ses->message("Error: Login should contain letters") if $f->{usr_login}=~/^\d+$/;
         $ses->message("Error: $ses->{lang}->{lang_login_too_short}") if length($f->{usr_login})<4;
         $ses->message("Error: $ses->{lang}->{lang_login_too_long}") if length($f->{usr_login})>32;
         $ses->message("Error: Invalid login: reserved word") if $f->{usr_login}=~/^(admin|images|captchas|files)$/;
         $ses->message("Error: $ses->{lang}->{lang_invalid_login}") unless $f->{usr_login}=~/^[\w\-\_]+$/;
         $ses->message("Error: $ses->{lang}->{lang_login_exist}")  if $db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$f->{usr_login});
         $db->Exec("UPDATE Users SET usr_login=? WHERE usr_id=?",$f->{usr_login},$ses->getUserId);
      }
      if($f->{usr_email} ne $ses->getUser->{usr_email})
      {
         $ses->message("This email already in use") if $db->SelectOne("SELECT usr_id FROM Users WHERE usr_id<>? AND usr_email=?", $ses->getUserId, $f->{usr_email} );
         $ses->message("Error: Invalid e-mail") unless $f->{usr_email}=~/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
         $db->Exec("UPDATE Users SET usr_email=? WHERE usr_id=?",$f->{usr_email},$ses->getUserId);
         $f->{msg}.=$ses->{lang}->{lang_email_changed_ok}.'<br>';
         $user->{usr_email_new} = $f->{usr_email};
      }
      if($f->{password_new} && $f->{password_new2})
      {
         $ses->message("New password is too short") if length($f->{password_new})<4;
         $ses->message("New passwords do not match") unless $f->{password_new} eq $f->{password_new2};
         $db->Exec("UPDATE Users SET usr_password=ENCODE(?,?) WHERE usr_id=?", $f->{password_new}, $c->{pasword_salt}, $ses->getUserId );
         $f->{msg}=$ses->{lang}->{lang_pass_changed_ok}.'<br>';
         $user->{usr_password_new} = $f->{password_new};
      }

      $db->Exec("UPDATE Users 
                 SET usr_pay_email=?, 
                     usr_pay_type=?,
                     usr_direct_downloads=?,
                     usr_rapid_login=?, 
                     usr_rapid_pass=?
                 WHERE usr_id=?",$f->{usr_pay_email}||'',
                                 $f->{usr_pay_type}||'',
                                 $f->{usr_direct_downloads}||0,
                                 $f->{usr_rapid_login}||'',
                                 $f->{usr_rapid_pass}||'',
                                 $ses->getUserId);
      $f->{msg}.=$ses->{lang}->{lang_sett_changed_ok};

      my @custom_fields = qw(
                             twitter_filename
                            );
      for(qw(rs mu nl hf mf fs df ff es sm ug fe))
      {
         push @custom_fields, "$_\_logins";
      }
      for( @custom_fields )
      {
         $db->Exec("INSERT INTO UserData
                    SET usr_id=?, name=?, value=?
                    ON DUPLICATE KEY UPDATE value=?
                   ",$ses->getUserId, $_, $f->{$_}||'', $f->{$_}||'');
      }

      $ses->ApplyPlugins('user_edit',$user);
   }
   &CheckAuth();
   my $user = $ses->getUser;
   my $totals = $db->SelectRow("SELECT COUNT(*) as total_files, SUM(file_size) as total_size FROM Files WHERE usr_id=?",$ses->getUserId);
   $totals->{total_size} = sprintf("%.02f",$totals->{total_size}/1024**3);
   my $disk_space = sprintf("%.0f GB",$c->{disk_space}/1024);
   $user->{premium_expire} = $db->SelectOne("SELECT DATE_FORMAT(usr_premium_expire,'%e %M %Y') FROM Users WHERE usr_id=?",$ses->getUserId);
   if($c->{bw_limit_days} && $c->{bw_limit})
   {
      my $bw = $db->SelectOne("SELECT SUM(size) FROM IP2Files WHERE ip=INET_ATON(?) AND created > NOW()-INTERVAL ? DAY",$ses->getIP,$c->{bw_limit_days});
      $user->{traffic_left} = sprintf("%.0f", $c->{bw_limit}-$bw/1024**2 );
   }
   my $data = $db->SelectARef("SELECT * FROM UserData WHERE usr_id=?",$user->{usr_id});
   $user->{$_->{name}}=$_->{value} for @$data;

   $user->{usr_money}=~s/\.?0+$//;
   $user->{login_change}=1 if $user->{usr_login}=~/^\d+$/;

   my $referrals = $db->SelectOne("SELECT COUNT(*) FROM Users WHERE usr_aff_id=?",$ses->getUserId);

   my @payout_list = map{ {name=>$_,checked=>($_ eq $ses->getUser->{usr_pay_type})} } split(/\s*\,\s*/,$c->{payout_systems});
   
   $ses->PrintTemplate("my_account.html",
                       %{$user},
                       'msg'  => $f->{msg},
                       'remote_url' => $c->{remote_url},
                       %{$totals},
                       'disk_space' => $disk_space,
                       #"pay_type_".$ses->getUser->{usr_pay_type}  => 1,
                       'paypal_email'        => $c->{paypal_email},
                       'payout_list'         => \@payout_list,
                       'alertpay_email'      => $c->{alertpay_email},
                       'webmoney_merchant_id'=> $c->{webmoney_merchant_id},
                       'm_w'  => $c->{m_w},
                       'referrals'           => $referrals,
                      );
}

sub MyReferrals
{
   my $list = $db->SelectARef("SELECT usr_login, usr_created, usr_money, UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as dt
                               FROM Users WHERE usr_aff_id=? ORDER BY usr_created DESC".$ses->makePagingSQLSuffix($f->{page}),$ses->getUserId);
   my $total = $db->SelectOne("SELECT COUNT(*) FROM Users WHERE usr_aff_id=?",$ses->getUserId);
   for(@$list)
   {
      $_->{prem}=1 if $_->{dt}>0;
      $_->{usr_money}=~s/\.?0+$//;
   }
   $ses->PrintTemplate("my_referrals.html",
                       list   => $list,
                       paging => $ses->makePagingLinks($f,$total),
                      );
}

sub MyFiles
{
   if($f->{del_code})
   {
      my $file = $db->SelectRow("SELECT * FROM Files WHERE file_code=? AND usr_id=?",$f->{del_code},$ses->getUserId);
      $ses->message("Security error: not_owner") unless $file;
      $ses->DeleteFile($file);
      $ses->redirect("?op=my_files");
   }
   if($f->{del_selected} && $f->{file_id})
   {
      my $files = $db->SelectARef("SELECT * FROM Files WHERE usr_id=? AND file_id IN (".join(',',@{&ARef($f->{file_id})}).")",$ses->getUserId);
      $|=1;
      print"Content-type:text/html\n\n<html><body>\n\n";
      $ses->DeleteFilesMass($files,'nb');
      print"<script>window.location='$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}';</script>";
      exit;
      #$ses->redirect("$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}");
   }
   if($f->{set_public} && $f->{file_id})
   {
      $f->{set_public} = $f->{set_public} eq 'true' ? 1 : 0;
      $db->Exec("UPDATE Files SET file_public=? WHERE usr_id=? AND file_id=?",$f->{set_public},$ses->getUserId,$f->{file_id});
      my $style = $f->{set_public} ? 'pub' : '';
      print"Content-type:text/html\n\n";
      print"\$\$('td$f->{file_id}').className='$style';";
      exit;
   }
   if($f->{set_public_multi} && $f->{file_id})
   {
      $db->Exec("UPDATE Files SET file_public=1 WHERE usr_id=? AND file_id IN (".join(',',@{&ARef($f->{file_id})}).")",$ses->getUserId);
      $ses->redirect("$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}");
   }
   #if($f->{set_private} && $f->{file_id})
   #{
   #   $db->Exec("UPDATE Files SET file_public=0 WHERE usr_id=? AND file_id IN (".join(',',@{&ARef($f->{file_id})}).")",$ses->getUserId);
   #   $ses->redirect("$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}");
   #}
   if($f->{create_new_folder})
   {
      $f->{create_new_folder} = $ses->SecureStr($f->{create_new_folder});
      $ses->message("Invalid folder name!") unless $f->{create_new_folder};
      $ses->message("Invalid parent folder") if $f->{fld_id} && !$db->SelectOne("SELECT fld_id FROM Folders WHERE usr_id=? AND fld_id=?",$ses->getUserId,$f->{fld_id});
      $ses->message("You have can't have more than 1024 folders") if $db->SelectOne("SELECT COUNT(*) FROM Folders WHERE usr_id=?",$ses->getUserId)>=1024;
      $db->Exec("INSERT INTO Folders SET usr_id=?, fld_parent_id=?, fld_name=?",$ses->getUserId,$f->{fld_id},$f->{create_new_folder});
      $ses->redirect("$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}");
   }
   if($f->{del_folder})
   {
      my $fld = $db->SelectRow("SELECT * FROM Folders WHERE usr_id=? AND fld_id=?",$ses->getUserId,$f->{del_folder});
      $ses->message("Invalid ID") unless $fld;
      sub delFolder
      {
         my ($fld_id)=@_;
         my $subf = $db->SelectARef("SELECT * FROM Folders WHERE usr_id=? AND fld_parent_id=?",$ses->getUserId,$fld_id);
         for(@$subf)
         {
            &delFolder($_->{fld_id});
         }
         my $files = $db->SelectARef("SELECT * FROM Files WHERE usr_id=? AND file_fld_id=?",$ses->getUserId,$fld_id);
         $ses->DeleteFilesMass($files);
         $db->Exec("DELETE FROM Folders WHERE usr_id=? AND fld_id=?",$ses->getUserId,$fld_id);
      }
      &delFolder($f->{del_folder});
      $ses->redirect("$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}");
   }
   if(defined $f->{to_folder} && $f->{file_id})
   {
      my $fld_id = $db->SelectOne("SELECT fld_id FROM Folders WHERE usr_id=? AND fld_id=?",$ses->getUserId,$f->{to_folder})||0;
      $db->Exec("UPDATE Files SET file_fld_id=? WHERE usr_id=? AND file_id IN (".join(',',@{&ARef($f->{file_id})}).")",$fld_id,$ses->getUserId);
      $ses->redirect("$c->{site_url}/?op=my_files&fld_id=$f->{fld_id}");
   }
   if($f->{add_my_acc})
   {
      print"Content-type:text/html\n\n";
      my $file = $db->SelectRow("SELECT * FROM Files WHERE file_code=? AND file_public=1",$f->{add_my_acc});
      print("Invalid file"),exit unless $file;

      my $code = $ses->randchar(12);
      while($db->SelectOne("SELECT file_id FROM Files WHERE file_code=?",$code)){$code = $ses->randchar(12);}

      $db->Exec("INSERT INTO Files 
           SET file_name=?, usr_id=?, srv_id=?, file_descr=?, file_public=?, file_code=?, file_real=?, file_real_id=?, file_del_id=?, file_size=?, 
               file_password=?, file_ip=INET_ATON(?), file_md5=?, file_spec=?, file_created=NOW(), file_last_download=NOW()",
            $file->{file_name},
            $ses->getUserId,
            $file->{srv_id},
            '',
            1,
            $code,
            $file->{file_real},
            $file->{file_real_id}||$file->{file_id},
            $file->{file_del_id},
            $file->{file_size},
            '',
            $ses->getIP,
            $file->{file_md5},
            $file->{file_spec}||'',
          );
      $db->Exec("UPDATE Servers SET srv_files=srv_files+1 WHERE srv_id=?",$file->{srv_id});
      print $ses->{lang}->{lang_added_to_account};
      exit;
   }
   if($f->{del_torrent})
   {
      my $torr = $db->SelectRow("SELECT * FROM Torrents WHERE sid=? AND usr_id=?",$f->{del_torrent},$ses->getUserId);
      $ses->redirect("$c->{site_url}/?op=my_files") unless $torr;
      my $res = $ses->api2($torr->{srv_id},{
                                  op   => 'torrent_delete',
                                  sid  => $f->{del_torrent},
                                 });
      $ses->message("Error1:$res") unless $res eq 'OK';

      $db->Exec("DELETE FROM Torrents WHERE sid=? AND status='WORKING'",$f->{del_torrent});
      $ses->redirect("$c->{site_url}/?op=my_files")
   }

   $f->{sort_field}||='file_created';
   $f->{sort_order}||='down';
   $f->{fld_id}||=0;
   my ($files,$total);
   my $folders=[];
   my $curr_folder = $db->SelectRow("SELECT * FROM Folders WHERE fld_id=?",$f->{fld_id}) if $f->{fld_id};
   $curr_folder ||= {};
   $ses->message("Invalid folder id") if $f->{fld_id} && $curr_folder->{usr_id}!=$ses->getUserId;
   if($f->{key})
   {
      $files = $db->SelectARef(q{SELECT *, DATE(file_created) as created,
                                (SELECT COUNT(*) FROM Comments WHERE cmt_type=1 AND file_id=cmt_ext_id) as comments
                                FROM Files
                                WHERE usr_id=?
                                AND (file_name LIKE CONCAT('%',?,'%') OR file_descr LIKE CONCAT('%',?,'%'))
                                ORDER BY file_created DESC}.$ses->makePagingSQLSuffix($f->{page}),$ses->getUserId,$f->{key},$f->{key});

      $total = $db->SelectOne("SELECT COUNT(*) FROM Files WHERE usr_id=? AND (file_name LIKE CONCAT('%',?,'%') OR file_descr LIKE CONCAT('%',?,'%'))",$ses->getUserId,$f->{key},$f->{key});
   }
   else
   {
      $files = $db->SelectARef("SELECT f.*, DATE(f.file_created) as created, 
                                (SELECT COUNT(*) FROM Comments WHERE cmt_type=1 AND file_id=cmt_ext_id) as comments
                                FROM Files f 
                                WHERE f.usr_id=? 
                                AND f.file_fld_id=? 
                                ".&makeSortSQLcode($f,'file_created').$ses->makePagingSQLSuffix($f->{page}),$ses->getUserId,$f->{fld_id});

      $total = $db->SelectOne("SELECT COUNT(*) FROM Files WHERE usr_id=? AND file_fld_id=?", $ses->getUserId, $f->{fld_id} );

      $folders = $db->SelectARef("SELECT f.*, COUNT(ff.file_id) as files_num
                                  FROM Folders f
                                  LEFT JOIN Files ff ON f.fld_id=ff.file_fld_id
                                  WHERE f.usr_id=? 
                                  AND fld_parent_id=?
                                  GROUP BY fld_id
                                  ORDER BY fld_name",$ses->getUserId,$f->{fld_id});
   }
   unshift @$folders, {fld_id=>$curr_folder->{fld_parent_id},fld_name=>'&nbsp;. .&nbsp;'} if $f->{fld_id};

   my %sort_hash = &makeSortHash($f,['file_name','file_downloads','comments','file_size','file_public','file_created']);

   my $totals = $db->SelectRow("SELECT COUNT(*) as total_files, SUM(file_size) as total_size FROM Files WHERE usr_id=?",$ses->getUserId);
   $totals->{total_size} = $totals->{total_size}<1048576 ? sprintf("%.01f Kb",$totals->{total_size}/1024) : sprintf("%.01f Mb",$totals->{total_size}/1048576);

   for(@$files)
   {
      $_->{site_url} = $c->{site_url};
      $_->{file_size} = $ses->makeFileSize($_->{file_size});
      my $file_descr = $_->{file_descr};
      utf8::decode($file_descr);
      $_->{file_descr} = length($file_descr)>48 ? substr($file_descr,0,48).'&#133;' : $file_descr;
      utf8::encode($_->{file_descr});
      my $file_name = $_->{file_name};
      utf8::decode($file_name);
      $_->{file_name_txt} = length($file_name)>$c->{display_max_filename} ? substr($file_name,0,$c->{display_max_filename}).'&#133;' : $file_name;
      utf8::encode($_->{file_name_txt});
      $_->{download_link} = $ses->makeFileLink($_);
      $_->{file_downloads}||='';
      $_->{comments}||='';
   }

   my $allfld = $db->SelectARef("SELECT * FROM Folders WHERE usr_id=? ORDER BY fld_name",$ses->getUserId);
   my $fh;
   push @{$fh->{$_->{fld_parent_id}}},$_ for @$allfld;
   my @folders_tree = &buildTree($fh,0,0);

   my $torrents=[];
   if($ses->iPlg('t'))
   {
      $torrents = $db->SelectARef("SELECT *, UNIX_TIMESTAMP()-UNIX_TIMESTAMP(created) as working
                                   FROM Torrents
                                   WHERE usr_id=?
                                   AND status='WORKING' ",$ses->getUserId);
      for my $t (@$torrents)
      {
         my @files = split("\n",$t->{files});
         $t->{file_list} = join('<br>',map{/^(.+):(\d+)$/;"$1 (<i>".sprintf("%.1f Mb",$2/1048576)."<\/i>)"}@files );
         $t->{file_list} =~ s/'/\\'/g;
         $t->{title}=$files[0];
         $t->{title}=~s/\/.+$//;
         $t->{title}=~s/:\d+$//;
         ($t->{done},$t->{total},$t->{down_speed},$t->{up_speed})=split(':',$t->{progress});
         $t->{percent}=sprintf("%.01f", 100*$t->{done}/$t->{total} );
         $t->{done} = sprintf("%.1f", $t->{done}/1048576 );
         $t->{total} = sprintf("%.1f", $t->{total}/1048576 );
         $t->{working} = $t->{working}>3600*3 ? sprintf("%.1f hours",$t->{working}/3600) : sprintf("%.0f mins",$t->{working}/60)
      }
   }

   $ses->PrintTemplate("my_files.html",
                       'files'         => $files,
                       'folders'       => $folders,
                       'folders_tree'  => \@folders_tree,
                       'folder_id'     => $f->{fld_id},
                       'folder_name'   => $curr_folder->{fld_name},
                       'fld_descr'     => $curr_folder->{fld_descr},
                       'key'           => $f->{key},
                       'disk_space'    => $c->{disk_space},
                       'paging'        => $ses->makePagingLinks($f,$total),
                       'torrents'      => $torrents,
                       enable_file_comments => $c->{enable_file_comments},
                       %{$totals},
                       %sort_hash,
                      );
}

sub buildTree
{
   my ($fh,$parent,$depth)=@_;
   my @tree;
   for my $x (@{$fh->{$parent}})
   {
      $x->{pre}='&nbsp;&nbsp;'x$depth;
      push @tree, $x;
      push @tree, &buildTree($fh,$x->{fld_id},$depth+1);
   }
   return @tree;
}

sub MyFilesExport
{
   my $filter;
   if($f->{file_id})
   {
      my $ids = join ',', grep{/^\d+$/}@{ARef($f->{file_id})};
      $filter="AND file_id IN ($ids)" if $ids;
   }
   else
   {
      $filter="AND file_fld_id='$f->{fld_id}'" if $f->{fld_id}=~/^\d+$/;
   }
   my $list = $db->SelectARef("SELECT * FROM Files f, Servers s
                               WHERE usr_id=? 
                               AND f.srv_id=s.srv_id
                               $filter 
                               ORDER BY file_name",$ses->getUserId);
   print $ses->{cgi_query}->header( -type    => 'text/html',
                                    -expires => '-1d',
                                    -charset => $c->{charset});
   my (@list,@list_bb,@list_html);
   for my $file (@$list)
   {
      $file->{download_link} = $ses->makeFileLink($file);
      if($c->{image_mod} && $file->{file_name}=~/\.(jpg|jpeg|gif|png|bmp)$/i)
      {
         $ses->getThumbLink($file);
      }
      else
      {
         $file->{fsize} = $ses->makeFileSize($file->{file_size});
      }
      push @list, $file->{download_link};
      push @list_bb, $file->{thumb_url} ? "[URL=$file->{download_link}][IMG]$file->{thumb_url}\[\/IMG]\[\/URL]" : "[URL=$file->{download_link}]$file->{file_name} - $file->{fsize}\[\/URL]";
      push @list_html, $file->{thumb_url} ? qq[<a href="$file->{download_link}" target=_blank><img src="$file->{thumb_url}" border=0><\/a>"] : qq[<a href="$file->{download_link}" target=_blank>$file->{file_name} - $file->{fsize}<\/a>];
   }
   print"<HTML><BODY style='font: 13px Arial;'>";
   print"<b>Download links</b><br><textarea cols=100 rows=10 wrap=off>".join("\n",@list)."<\/textarea><br><br>";
   print"<b>Forum code</b><br><textarea cols=100 rows=10 wrap=off>".join("\n",@list_bb)."<\/textarea><br><br>";
   print"<b>HTML code</b><br><textarea cols=100 rows=10 wrap=off>".join("\n",@list_html)."<\/textarea><br><br>";
   exit;
}

sub UserPublic
{
   my $user = $db->SelectRow("SELECT * FROM Users WHERE usr_login=?",$f->{usr_login});
   $ses->message("No such user exist") unless $user;
   $f->{fld}=~s/\///g;
   my $folder = $db->SelectRow("SELECT * FROM Folders WHERE usr_id=? AND fld_id=?",$user->{usr_id},$f->{fld_id});
   $ses->message("No such folder") if $f->{fld} && !$folder;
   my $files = $db->SelectARef("SELECT *, TO_DAYS(CURDATE())-TO_DAYS(file_created) as created,
                                       s.srv_htdocs_url
                                FROM Files f, Servers s
                                WHERE usr_id=?
                                AND file_public=1
                                AND file_fld_id=?
                                AND f.srv_id=s.srv_id
                                ORDER BY file_created DESC",$user->{usr_id},$folder->{fld_id}||0);
   my $folders = $db->SelectARef("SELECT *
                                  FROM Folders
                                  WHERE usr_id=?
                                  AND fld_parent_id=?
                                  ORDER BY fld_name",$user->{usr_id},$folder->{fld_id}||0);
   my $parent = $db->SelectRow("SELECT fld_id as fld_parent_id, fld_name as parent_name 
                                FROM Folders 
                                WHERE usr_id=? AND fld_id=?",$user->{usr_id},$folder->{fld_parent_id}) if $folder->{fld_parent_id};
   my $cx;
   for(@$files)
   {
      $_->{site_url} = $c->{site_url};

      my $file_name = $_->{file_name};
      utf8::decode($file_name);
      $_->{file_name_txt} = length($file_name)>$c->{display_max_filename} ? substr($file_name,0,$c->{display_max_filename}).'&#133;' : $file_name;
      utf8::encode($_->{file_name_txt});

      $_->{file_size}     = $ses->makeFileSize($_->{file_size});
      $_->{download_link} = $ses->makeFileLink($_);
      my ($ext) = $_->{file_name}=~/\.(\w+)$/i;
      $ext=lc $ext;
#      $_->{img_preview} = $ext=~/^(ai|aiff|asf|avi|bmpbz2|css|doc|eps|gif|gz|html|jpg|jpeg|mid|mov|mp3|mpg|mpeg|ogg|pdf|png|ppt|ps|psd|qt|ra|ram|rm|rpm|rtf|tgz|tif|torrent|txt|wav|xls|xml|zip|exe|flv|swf|qma|wmv|mkv)$/i ? "$c->{site_url}/images/icons/$ext-dist.png" : "$c->{site_url}/images/icons/1.gif";
      $_->{img_preview} = $ext=~/^(ai|aiff|asf|avi|bmpbz2|css|doc|eps|gif|gz|html|jpg|jpeg|mid|mov|mp3|mpg|mpeg|ogg|pdf|png|ppt|ps|psd|qt|ra|ram|rm|rpm|rtf|tgz|tif|torrent|txt|wav|xls|xml|zip|exe|flv|swf|qma|wmv|mkv|rar)$/ ? "$c->{site_url}/images/icons/$ext-dist.png" : "$c->{site_url}/images/icons/default-dist.png";
      $_->{add_to_account}=1 if $ses->getUser && $_->{usr_id}!=$ses->getUserId;
      if( ($c->{m_i} && $_->{file_name}=~/\.(jpg|jpeg|gif|png|bmp)$/i )
          || ($c->{m_v} && $_->{file_name}=~/\.(avi|divx|flv|mp4|wmv|mkv)$/i) )
      {
         my $iurl = $_->{srv_htdocs_url};
         $iurl=~s/^(.+)\/.+$/$1\/i/;
         my $dx = sprintf("%05d",($_->{file_real_id}||$_->{file_id})/$c->{files_per_folder});
         $_->{img_preview2} = "$iurl/$dx/$_->{file_real}_t.jpg";
      }
      $_->{'tr'}=1 if ++$cx%3==0;
   }
   for(@$folders)
   {
      $_->{site_url} = $c->{site_url};
      $_->{usr_login} = $f->{usr_login};
   }
   $ses->{page_title} = $ses->{lang}->{lang_files_of}." ".$user->{usr_login};
   $ses->{page_title} .= ": $folder->{fld_name} folder" if $folder->{fld_name};
   $ses->{meta_descr} = $user->{usr_login}.' '.$ses->{lang}->{lang_files};
   $ses->PrintTemplate("user_public.html", 
                       'login'   => $user->{usr_login},
                       'folders' => $folders,
                       'fld_id'  => $f->{fld_id},
                       %$parent,
                       files => $files );
}

sub FileEdit
{
   my $file = $db->SelectRow("SELECT * FROM Files WHERE file_code=?",$f->{file_code});
   $ses->message("No such file!") unless $file;
   $ses->message("It's not your file!") if !$ses->getUser->{usr_adm} && $file->{usr_id}!=$ses->getUserId;

   if($c->{rar_info} && $f->{rar_pass_remove} && $f->{file_code})
   {
         my $res = $ses->api2($file->{srv_id},
                             {
                                op        => 'rar_password',
                                file_id   => $file->{file_id},
                                file_code => $file->{file_code},
                                rar_pass  => $f->{rar_pass},
                             }
                            );
         unless($res=~/Software error/i)
         {
          $db->Exec("UPDATE Files SET file_spec=? WHERE file_real=?",$res,$f->{file_code});
         }
         $ses->redirect("?op=file_edit&file_code=$file->{file_code}");
   }
   if($c->{rar_info} && $f->{rar_files_delete} && $f->{fname})
   {
         my $files = join ' ', map{qq["$_"]} @{&ARef($f->{fname})};
         my $res = $ses->api2($file->{srv_id},
                             {
                                op        => 'rar_file_del',
                                file_id   => $file->{file_id},
                                file_code => $file->{file_code},
                                rar_pass  => $f->{rar_pass},
                                files     => $files,
                             }
                            );
         unless($res=~/Software error/i)
         {
          $db->Exec("UPDATE Files SET file_spec=? WHERE file_real=?",$res,$f->{file_code});
         }
         else
         {
          $ses->message($res);
         }
         $ses->redirect("?op=file_edit&file_code=$file->{file_code}");
   }
   if($c->{rar_info} && $f->{rar_files_extract} && $f->{fname})
   {
         my $files = join ' ', map{qq["$_"]} @{&ARef($f->{fname})};
         my $res = $ses->api2($file->{srv_id},
                             {
                                op        => 'rar_file_extract',
                                file_id   => $file->{file_id},
                                file_code => $file->{file_code},
                                rar_pass  => $f->{rar_pass},
                                files     => $files,
                                usr_id    => $ses->getUserId,
                             }
                            );
         $ses->message($res) unless $res eq 'OK';
         $ses->redirect("?op=my_files");
   }
   if($f->{save})
   {
      $f->{file_name}=~s/%(\d\d)/chr(hex($1))/egs;
      $f->{file_name}=~s/%/_/gs;
      $f->{file_name}=~s/\s{2,}/ /gs;
      $f->{file_name}=~s/[\#\"]+/_/gs;
      $f->{file_name}=~s/[^\w\d\.-]/_/g if $c->{sanitize_filename};
      $ses->message("Filename have unallowed extension") if ($c->{ext_allowed} && $f->{file_name}!~/\.($c->{ext_allowed})$/i) || ($c->{ext_not_allowed} && $f->{file_name}=~/\.($c->{ext_not_allowed})$/i);
      $f->{file_descr} = $ses->SecureStr($f->{file_descr});
      $f->{file_password} = $ses->SecureStr($f->{file_password});
      $ses->message("Filename too short") if length($f->{file_name})<3;
      $db->Exec("UPDATE Files SET file_name=?, file_descr=?, file_public=?, file_password=? WHERE file_code=?",$f->{file_name},$f->{file_descr},$f->{file_public},$f->{file_password},$f->{file_code});
      $ses->redirect("?op=my_files;fld_id=$file->{file_fld_id}");
   }

   if($file->{file_name}=~/\.rar$/i && $file->{file_spec} && $c->{rar_info})
   {
      $file->{rar_nfo}=$file->{file_spec};
      $file->{rar_nfo}=~s/\r//g;
      $file->{rar_password}=1 if $file->{rar_nfo}=~s/password protected\n//ie;
      $file->{rar_nfo}=~s/\n\n.+$//s;
      #die $file->{rar_nfo};
      my @files;
      my $fld;
      while($file->{file_spec}=~/^(.+?) - (\d+ KB|MB)$/gim)
      {
         my $path=$1;
         my $fname=$1;
         my $fsize = $2;
         
         if($fname=~s/^(.+)\///)
         {
            #push @rf,"<b>$1</b>" if $fld ne $1;
            push @files, {fname=>$1, fname2=>"<b>$1</b>"} if $fld ne $1;;
            $fld = $1;
         }
         else
         {
            $fld='';
         }
         $fname=" &nbsp; &nbsp; $fname" if $fld;
         push @files, {fname=>$path, fname2=>"$fname - $fsize"};
      }
      #$file->{rar_nfo}.=join "\n", @rf;
      $file->{rar_files} = \@files;
   }

   $ses->PrintTemplate("file_form.html", %{$file} );
}

sub FolderEdit
{
   my $folder = $db->SelectRow("SELECT * FROM Folders WHERE fld_id=? AND usr_id=?",$f->{fld_id},$ses->getUserId);
   $ses->message("No such folder!") unless $folder;
   if($f->{save})
   {
      $f->{fld_name}  = $ses->SecureStr($f->{fld_name});
      $f->{fld_descr} = $ses->SecureStr($f->{fld_descr});
      $ses->message("Folder name too short") if length($f->{fld_name})<3;
      $db->Exec("UPDATE Folders SET fld_name=?, fld_descr=? WHERE fld_id=?",$f->{fld_name},$f->{fld_descr},$f->{fld_id});
      $ses->redirect("?op=my_files");
   }
   $ses->PrintTemplate("folder_form.html", %{$folder} );
}



sub Payments
{
   $ses->redirect($c->{site_url}) unless $c->{enabled_prem};
   if($f->{amount})
   {
      $f->{amount}=sprintf("%.02f",$f->{amount});

      my $plans;
      for(split(/,/,$c->{payment_plans}))
      {
         /([\d\.]+)=(\d+)/;
         $plans->{sprintf("%.02f",$1)}=$2;
      }
      $ses->message("Invalid payment amount") unless $plans->{$f->{amount}};

      my $id = int(1+rand 9).join('', map {int(rand 10)} 1..9);

      my $usr_id = $ses->getUser ? $ses->getUserId : 0;
      my $aff_id = $ses->getCookie('aff')||0;
      $aff_id=0 if $aff_id==$usr_id;
      $aff_id = $ses->getUser->{usr_aff_id} if $ses->getUser && $ses->getUser->{usr_aff_id} && !$aff_id;
      $db->Exec("INSERT INTO Transactions SET id=?, usr_id=?, amount=?, ip=INET_ATON(?), created=NOW(), aff_id=?",$id,$usr_id,$f->{amount},$ses->getIP,$aff_id);

      my $url;
      if($f->{type} eq 'paypal') # && $ses->iPlg('s')
      {
         if($c->{paypal_subscription})
         {
            my $days = $plans->{$f->{amount}};
            my $time_code='D' if $days<=90;
            unless($time_code){$time_code='M';$days=sprintf("%.0f",$days/30);}
            print"Content-type:text/html\n\n";
print <<END
<HTML><BODY onLoad="document.F1.submit();">
<form name="F1" action="$c->{paypal_url}" method="post">
<input type="hidden" name="cmd" value="_xclick-subscriptions">
<input type="hidden" name="business" value="$c->{paypal_email}">
<input type="hidden" name="currency_code" value="$c->{currency_code}">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="item_name" value="$c->{item_name}">
<input type="hidden" name="a3" value="$f->{amount}">
<input type="hidden" name="p3" value="$days">
<input type="hidden" name="t3" value="$time_code">
<input type="hidden" name="src" value="1">
<input type="hidden" name="sra" value="1">
<input type="hidden" name="rm" value="2">
<input type="hidden" name="no_note" value="1">
<input type="hidden" name="custom" value="$id">
<input type="hidden" name="return" value="$c->{site_url}/?payment_complete=$id-$usr_id">
<input type="hidden" name="notify_url" value="$c->{site_cgi}/ipn.cgi">
<input type="submit" value="Redirecting...">
</form>
</BODY></HTML>
END
;
            exit;
         }
         else
         {
            print"Content-type:text/html\n\n";
print <<END
<HTML><BODY onLoad="document.F1.submit();">
<form name="F1" action="$c->{paypal_url}" method="post">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="no_note" value="1">
<input type="hidden" name="cbt" value="Start using $c->{site_name}!">
<input type="hidden" name="currency_code" value="$c->{currency_code}">
<input type="hidden" name="item_name" value="$c->{item_name}">
<input type="hidden" name="return" value="$c->{site_url}/?payment_complete=$id-$usr_id">
<input type="hidden" name="cancel_return" value="$c->{site_url}">
<input type="hidden" name="notify_url" value="$c->{site_cgi}/ipn.cgi">
<input type="hidden" name="custom" value="$id">
<input type="hidden" name="amount" value="$f->{amount}">
<input type="hidden" name="business" value="$c->{paypal_email}">
<input type="submit" value="Redirecting...">
</form>
</BODY></HTML>
END
;
         exit;
         }
      }
      elsif($f->{type} eq '2co')
      {
         $url="https://www2.2checkout.com/2co/buyer/purchase?sid=$c->{two_checkout_sid}";
         $url.="&cart_order_id=$id&total=$f->{amount}";
         #$url.="&demo=Y";
      }
      elsif(!$ses->iPlg('m'))
      {
         $url="http://sibsoft.net/?sid=$c->{two_checkout_sid}";
         $url.="&cart_order_id=$id&total=$f->{amount}";
         $ses->redirect($url);
      }

      if($f->{type} eq 'alertpay')
      {
         $url="https://www.alertpay.com/PayProcess.aspx?ap_purchasetype=item&ap_merchant=$c->{alertpay_email}&ap_itemname=$c->{item_name}&ap_currency=$c->{currency_code}&ap_returnurl=$c->{site_url}/?payment_complete=$id-$usr_id&ap_quantity=1";
         $url.="&apc_1=$id&ap_amount=$f->{amount}";
      }
      elsif($f->{type} eq 'daopay')
      {
         my $usr_id = $ses->getUser ? $ses->getUserId : 0;
         $url="http://daopay.com/payment/?appcode=$c->{daopay_app_id}&price=$f->{amount}&currency=$c->{currency_code}&payment_complete=$id-$usr_id";
      }
      elsif($f->{type} eq 'wmz')
      {
         print"Content-type:text/html\n\n";
print <<END
<HTML><BODY onLoad="document.F1.submit();">
<Form method="POST" action="https://merchant.webmoney.ru/lmi/payment.asp" name="F1">
<input type="hidden" name="LMI_PAYEE_PURSE" value="$c->{webmoney_merchant_id}">
<input type="hidden" name="LMI_PAYMENT_AMOUNT" value="$f->{amount}">
<input type="hidden" name="LMI_PAYMENT_DESC" value="$c->{item_name}">
<input type="hidden" name="LMI_PAYMENT_NO" value="$id">
<input type="hidden" name="LMI_RESULT_URL" value="$c->{site_cgi}/ipn.cgi">
<input type="hidden" name="LMI_SUCCESS_URL" value="$c->{site_url}/?payment_complete=$id-$usr_id">
<input type="hidden" name="LMI_FAIL_URL" value="$c->{site_url}">
<input type="submit" value="OK">
</Form>
</BODY></HTML>
END
;
         exit;
      }
      elsif($f->{type} eq 'moneybookers')
      {
         print"Content-type:text/html\n\n";
print <<END
<HTML><BODY onLoad="document.F1.submit();">
<form action="https://www.moneybookers.com/app/payment.pl" method="post" name="F1">
<input type="hidden" name="pay_to_email" value="$c->{moneybookers_email}">
<input type="hidden" name="transaction_id" value="$id">
<input type="hidden" name="return_url" value="$c->{site_url}/?payment_complete=$id-$usr_id">
<input type="hidden" name="cancel_url" value="$c->{site_url}">
<input type="hidden" name="status_url" value="$c->{site_cgi}/ipn.cgi">
<input type="hidden" name="language" value="EN">
<input type="hidden" name="amount" value="$f->{amount}">
<input type="hidden" name="currency" value="$c->{currency_code}">
<input type="hidden" name="detail1_description" value="$c->{item_name}">
<input type="hidden" name="detail1_text" value="$f->{amount} payment">
<input type="submit" value="Redirecting...">
</form>
</BODY></HTML>
END
;
         exit;
      }
      elsif($f->{type} eq 'smscoin')
      {
        require Digest::MD5;
	sub print_smscoin_form
	{
		my ($purse, $order_id, $amount, $clear_amount, $description, $secret_code, $usr_id) = @_;
		local $_ = join("::", ($purse, $order_id, $amount, $clear_amount, $description, $secret_code) );
		my $sign = Digest::MD5::md5_hex($_);
		my $cc = $ses->{cgi_query}->cookie( -name => 'transaction_id', -value => "$order_id-$usr_id", -domain  => ".$ses->{domain}", -expires => '+1h');
		print $ses->{cgi_query}->header( -cookie => [$cc] , -type => 'text/html', -expires => '-1h', -charset => $c->{charset});
		print <<Form
		<HTML><BODY onLoad="document.F1.submit();">
		<form action="http://bank.smscoin.com/bank/" method="post" name="F1">
			<p style="visibility:hidden;">
				<input name="s_purse" type="hidden" value="$purse" />
				<input name="s_order_id" type="hidden" value="$order_id" />
				<input name="s_amount" type="hidden" value="$amount" />
				<input name="s_clear_amount" type="hidden" value="$clear_amount" />
				<input name="s_description" type="hidden" value="$description" />
				<input name="s_sign" type="hidden" value="$sign" />
				<input type="submit" value="Pay" />
			</p>
		</form>
		</BODY></HTML>
Form
	;
	}
        print_smscoin_form($c->{smscoin_id}, $id, $f->{amount}, 0, $c->{site_name}, $c->{dl_key}, $usr_id);
        exit;
      }
      elsif($f->{type} eq 'plimus')
      {
        $ses->setCookie('transaction_id',"$id-$usr_id");
        $url="https://www.plimus.com/jsp/buynow.jsp?contractId=$c->{plimus_contract_id}&currency=$c->{currency_code}&bCur=$c->{currency_code}&overridePrice=$f->{amount}&custom1=$id";
      }
      elsif($f->{type} eq 'cashu')
      {
        use Digest::MD5 qw(md5_hex);
	sub print_cashu_form
	{
		my ($merchant_id, $order_id, $amount, $currency, $secret_code) = @_;
		local $_ = join(":", ($merchant_id, $amount, lc($currency), $secret_code) );
		my $sign = md5_hex($_);
		my $cc = $ses->{cgi_query}->cookie( -name => 'transaction_id', -value => $order_id, -domain  => ".$ses->{domain}", -expires => '+1h');
		print $ses->{cgi_query}->header( -cookie => [$cc] , -type => 'text/html', -expires => '-1h', -charset => $c->{charset});
		print <<Form
		<HTML><BODY onLoad="document.F1.submit();">
		<form action="https://www.cashu.com/cgi-bin/pcashu.cgi" method="POST" name="F1">
			<p style="visibility:hidden;">
				<input name="merchant_id" type="hidden" value="$merchant_id" />
				<input name="amount" type="hidden" value="$amount" />
				<input name="currency" type="hidden" value="$currency" />
				<input name="language" type="hidden" value="en" />
				<input name="token" type="hidden" value="$sign" />
				<input name="display_text" type="hidden" value="$c->{site_name}" />
				<input name="txt1" type="display_text" value="$c->{site_name}" />
				<input name="session_id" type="hidden" value="$order_id" />
				<input name="test_mode" type="hidden" value="0" />
				<input type="submit" value="Pay" />
			</p>
		</form>
		</BODY></HTML>
Form
	;
	}
        print_cashu_form($c->{cashu_merchant_id}, $id, $f->{amount}, $c->{currency_code}, $c->{dl_key});
        exit;
      }
      
      $ses->redirect($url) if $url;
   }

   my @arr = split(/,/,$c->{payment_plans});
   my @plans;
   for(@arr)
   {
      /([\d\.]+)=(\d+)/;
      push @plans, { amount=>$1, days=>$2, site_url=>$c->{site_url} };
   }

   for('max_upload_filesize_prem','max_upload_filesize_reg','max_upload_filesize_anon')
   {
      $c->{$_} = $c->{$_} ? "$c->{$_} Mb" : "No limits";
   }
   #$c->{captcha_reg} = 'yes' if $c->{captcha_reg};
   #$c->{captcha_prem} = 'yes' if $c->{captcha_prem};
   #$c->{download_countdown_reg} = $c->{download_countdown_reg} ? "$c->{download_countdown_reg} seconds" : '';
   #$c->{download_countdown_prem} = $c->{download_countdown_prem} ? "$c->{download_countdown_prem} seconds" : '';
   $c->{max_downloads_number_reg}||='Unlimited';
   $c->{max_downloads_number_prem}||='Unlimited';
   $c->{files_expire_anon} = $c->{files_expire_access_anon} ? "$c->{files_expire_access_anon} $ses->{lang}->{lang_days_after_downl}" : $ses->{lang}->{lang_never};
   $c->{files_expire_reg}  = $c->{files_expire_access_reg}  ? "$c->{files_expire_access_reg} $ses->{lang}->{lang_days_after_downl}" : $ses->{lang}->{lang_never};
   $c->{files_expire_prem} = $c->{files_expire_access_prem} ? "$c->{files_expire_access_prem} $ses->{lang}->{lang_days_after_downl}" : $ses->{lang}->{lang_never};
   $c->{bw_limit_anon}||='Unlimited';
   $c->{bw_limit_reg}||='Unlimited';
   $c->{bw_limit_prem}||='Unlimited';

   require Time::Elapsed;
   my $et = new Time::Elapsed;
   $ses->PrintTemplate("payments.html",
                        %{$c},
                        plans => \@plans, 
                        premium => $ses->getUser && $ses->getUser->{premium},
                        expire_elapsed => $ses->getUser && $et->convert($ses->getUser->{exp_sec}),
                        'rand' => $ses->randchar(6),
                      );
}

sub PaymentComplete
{
   my $str = shift;
   $str = $ses->getCookie('transaction_id') if $ses->getCookie('transaction_id');
   my ($id,$usr_id)=split(/-/,$str);
   my $trans = $db->SelectRow("SELECT *, INET_NTOA(ip) as ip, (UNIX_TIMESTAMP()-UNIX_TIMESTAMP(created)) as dt
                               FROM Transactions 
                               WHERE id=?",$id) if $id;
   $ses->message("No such transaction exist") unless $trans;
   $ses->message("Internal error") unless $trans->{ip} eq $ENV{REMOTE_ADDR};
   $ses->message("Your account created successfully.<br>Please check your e-mail for login details") if $trans->{dt}>3600;
   $ses->message("Your payment have not verified yet.<br>Please refresh this page in 1-3 minutes") unless $trans->{verified};

   my $user = $db->SelectRow("SELECT *, DECODE(usr_password,?) as usr_password, 
                                     UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec 
                              FROM Users 
                              WHERE usr_id=?",$c->{pasword_salt},$trans->{usr_id});
   require Time::Elapsed;
   my $et = new Time::Elapsed;
   my $exp = $et->convert($user->{exp_sec});
   $ses->message("Your payment processed successfully!<br><br>Login: $user->{usr_login}<br>Password: $user->{usr_password}<br><br>Your premium account expires in:<br>$exp");
}

sub AdminUsersAdd
{
   
   my ($list,$result);
   if($f->{generate})
   {
      my @arr;
      $f->{prem_days}||=0;
      for(1..$f->{num})
      {
         my $login = join '', map int rand 10, 1..7;
         while($db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$login)){ $login = join '', map int rand 10, 1..7; }
         my $password = $ses->randchar(10);
         push @arr, "$login:$password:$f->{prem_days}";
      }
      $list = join "\n", @arr;
   }
   if($f->{create} && $f->{list})
   {
      my @arr;
      $f->{list}=~s/\r//gs;
      for( split /\n/, $f->{list} )
      {
         $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
         #my ($login,$password,$days) = /^([\w\-\_]+):(\w+):(\d+)$/;
         my ($login,$password,$days,$email) = split(/:/,$_);
         next unless $login=~/^[\w\-\_]+$/ && $password=~/^[\w\-\_]+$/;
         $days=~s/\D+//g;
         $days||=0;
         push(@arr, "<b>$login:$password:$days - ERROR:login already exist</b>"),next if $db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$login);
         $db->Exec("INSERT INTO Users 
                    SET usr_login=?, 
                        usr_password=ENCODE(?,?), 
                        usr_email=?,
                        usr_created=NOW(), 
                        usr_premium_expire=NOW()+INTERVAL ? DAY",$login,$password,$c->{pasword_salt},$email||'',$days);
         push @arr, "$login:$password:$days";
      }
      $result = join "<br>", @arr;
   }
   $ses->PrintTemplate("admin_users_add.html",
                       'list'   => $list,
                       'result' => $result,
                      );
}

sub AdminNews
{
   
   if($f->{del_id})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      $db->Exec("DELETE FROM News WHERE news_id=?",$f->{del_id});
      $db->Exec("DELETE FROM Comments WHERE cmt_type=2 AND cmt_ext_id=?",$f->{del_id});
      $ses->redirect('?op=admin_news');
   }
   my $news = $db->SelectARef("SELECT n.*, COUNT(c.cmt_id) as comments
                               FROM News n 
                               LEFT JOIN Comments c ON c.cmt_type=2 AND c.cmt_ext_id=n.news_id
                               GROUP BY n.news_id
                               ORDER BY created DESC".$ses->makePagingSQLSuffix($f->{page}));
   my $total = $db->SelectOne("SELECT COUNT(*) FROM News");
   for(@$news)
   {
      $_->{site_url} = $c->{site_url};
   }
   $ses->PrintTemplate("admin_news.html",
                       'news' => $news,
                       'paging' => $ses->makePagingLinks($f,$total),
                      );
}

sub AdminNewsEdit
{
   
   if($f->{save})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      $f->{news_text} = $ses->{cgi_query}->param('news_text');
      $f->{news_title2}=lc $f->{news_title};
      $f->{news_title2}=~s/[^\w\s]//g;
      $f->{news_title2}=~s/\s+/-/g;
      if($f->{news_id})
      {
         $db->Exec("UPDATE News SET news_title=?, news_title2=?, news_text=?, created=? WHERE news_id=?",$f->{news_title},$f->{news_title2},$f->{news_text},$f->{created},$f->{news_id});
      }
      else
      {
         $db->Exec("INSERT INTO News SET news_title=?, news_title2=?, news_text=?, created=?",$f->{news_title},$f->{news_title2},$f->{news_text},$f->{created},$f->{news_id});
      }
      $ses->redirect('?op=admin_news');
   }
   my $news = $db->SelectRow("SELECT * FROM News WHERE news_id=?",$f->{news_id});
   $news->{created}||=sprintf("%d-%02d-%02d %02d:%02d:%02d", $ses->getTime() );
   $ses->PrintTemplate("admin_news_form.html",
                       %{$news},
                      );
}

sub AdminMassEmail
{
   if($f->{'send'})
   {
      $ses->message("Not allowed in Demo mode") if $c->{demo_mode};
      $ses->message("Subject required") unless $f->{subject};
      $ses->message("Message") unless $f->{body};
      my $filter_premium=" WHERE usr_premium_expire>NOW()" if $f->{premium_only};
      my $users = $db->SelectARef("SELECT usr_login,usr_email FROM Users $filter_premium");
      $|++;
      print"Content-type:text/html\n\n<HTML><BODY>";
      $c->{email_text}=1;
      my $cx;
      for my $u (@$users)
      {
         next unless $u->{usr_email};
         my $body = $f->{body};
         $body=~s/%username%/$u->{usr_login}/egis;
         $ses->SendMail($u->{usr_email},$c->{email_from},$f->{subject},$body);
         print"Sent to $u->{usr_email}<br>";
         $cx++;
      }
      print"<b>DONE.</b><br><br>Sent to <b>$cx</b> users.<br><br><a href='?op=admin_users'>Back to User Management</a>";
      exit;
   }
   $ses->PrintTemplate("admin_mass_email.html");
}

sub CheckFiles
{
   sleep 1;
   $f->{list}=~s/\r//gs;
   my ($i,@arr);
   for( split /\n/, $f->{list} )
   {
      $i++;
      my ($code,$fname) = /\/(\w{12})\/?(.*?)$/;
      next unless $code;
      $fname=~s/\.html?$//i;
      $fname=~s/_/ /g;
      #my $filter_fname="AND file_name='$fname'" if $fname=~/^[^'"<>]+$/;
      my $file = $db->SelectRow("SELECT f.file_id,f.file_name,s.srv_status FROM Files f, Servers s WHERE f.file_code=? AND s.srv_id=f.srv_id",$code);
      $file->{file_name}=~s/_/ /g;
      push(@arr,"<font color='red'>$_ not found!</font>"),next unless $file;
      push(@arr,"<font color='red'>$_ filename don't match!</font>"),next unless $file->{file_name} eq $fname;
      push(@arr,"<font color='orange'>$_ exist but not available at the moment!</font>"),next if $file->{srv_status} eq 'OFF';
      push(@arr,"<font color='green'>$_ found</font>");
   }
   $ses->PrintTemplate("checkfiles.html",
                       'result' => join "<br>", @arr,
                      );
}

sub Catalogue
{
   $ses->redirect($c->{site_url}) unless $c->{enable_catalogue};
   $f->{page}||=1;
   $f->{per_page}=30;
   my $exts = {'vid' => 'avi|mpg|mpeg|mkv|wmv|mov|3gp|vob|asf|qt|m2v|divx|mp4|flv|rm',
               'aud' => 'mp3|wma|ogg|flac|wav|aac|m4a|mid|mpa|ra',
               'img' => 'jpg|jpeg|png|gif|bmp|eps|ps|psd|tif',
               'arc' => 'zip|rar|7z|gz|pkg|tar',
               'app' => 'exe|msi|app|com'
              }->{$f->{ftype}};
   my $filter_ext = "AND file_name REGEXP '\.($exts)\$' " if $exts;
   my $fsize_logic = $f->{fsize_logic} eq 'gt' ? '>' : '<';
   my $filter_size = "AND file_size $fsize_logic ".($f->{fsize}*1048576) if $f->{fsize};
   my $filter = "AND (file_name LIKE '%$f->{k}%' OR file_descr LIKE '%$f->{k}%')" if $f->{k}=~/^[^\"\'\;\\]{3,}$/;
   my $list = $db->SelectARef("SELECT SQL_CALC_FOUND_ROWS *, TO_DAYS(CURDATE())-TO_DAYS(file_created) as created,
                                      s.srv_htdocs_url
                               FROM Files f, Servers s
                               WHERE file_public=1
                               AND f.srv_id=s.srv_id
                               $filter
                               $filter_ext
                               $filter_size
                               ORDER BY file_created DESC".$ses->makePagingSQLSuffix($f->{page}) );
   my $total = $db->SelectOne("SELECT FOUND_ROWS()");
   my $paging = $ses->makePagingLinks($f,$total,'reverse');

   my $cx;
   for(@$list)
   {
      $_->{site_url} = $c->{site_url};
      utf8::decode($_->{file_descr});
      $_->{file_descr} = substr($_->{file_descr},0,48).'&#133;' if length($_->{file_descr})>48;
      utf8::encode($_->{file_descr});
      $_->{file_size}     = $ses->makeFileSize($_->{file_size});
      $_->{download_link} = $ses->makeFileLink($_);
      $_->{file_name}=~s/_/ /g;
      my ($ext) = $_->{file_name}=~/\.(\w+)$/i;

      my $file_name = $_->{file_name};
      utf8::decode($file_name);
      $_->{file_name_txt} = length($file_name)>$c->{display_max_filename} ? substr($file_name,0,$c->{display_max_filename}).'&#133;' : $file_name;
      utf8::encode($_->{file_name_txt});

      $ext=lc $ext;
      $_->{img_preview} = $ext=~/^(ai|aiff|asf|avi|bmpbz2|css|doc|eps|gif|gz|html|jpg|jpeg|mid|mov|mp3|mpg|mpeg|ogg|pdf|png|ppt|ps|psd|qt|ra|ram|rm|rpm|rtf|tgz|tif|torrent|txt|wav|xls|xml|zip|exe|flv|swf|qma|wmv|mkv|rar)$/ ? "$c->{site_url}/images/icons/$ext-dist.png" : "$c->{site_url}/images/icons/default-dist.png";
      $_->{add_to_account}=1 if $ses->getUser && $_->{usr_id}!=$ses->getUserId;
      if( ($c->{m_i} && $_->{file_name}=~/\.(jpg|jpeg|gif|png|bmp)$/i )
          || ($c->{m_v} && $_->{file_name}=~/\.(avi|divx|flv|mp4|wmv|mkv)$/i) )
      {
         my $iurl = $_->{srv_htdocs_url};
         $iurl=~s/^(.+)\/.+$/$1\/i/;
         my $dx = sprintf("%05d",($_->{file_real_id}||$_->{file_id})/$c->{files_per_folder});
         $_->{img_preview2} = "$iurl/$dx/$_->{file_real}_t.jpg";
      }
      $_->{'tr'}=1 if ++$cx%3==0;
   }
   $ses->{header_extra} = qq{<link rel="alternate" type="application/rss+xml" title="$c->{site_name} new files" href="$c->{site_url}/catalogue.rss">};
   $ses->{page_title} = "$c->{site_name} File Catalogue: page $f->{page}";
   #die $f->{k};
   $ses->PrintTemplate("catalogue.html",
                       'files'  => $list,
                       'paging' => $paging,
                       'date'   => $f->{date},
                       'k'      => $f->{k},
                       'fsize'  => $f->{fsize},
                      );
}

sub RequestMoney
{
   my $money = $ses->getUser->{usr_money};
   if($f->{convert_ext_acc})
   {
      $ses->message("$ses->{lang}->{lang_need_at_least} \$$c->{convert_money}") if $money<$c->{convert_money};
      if($ses->getUser->{premium})
      {
         $db->Exec("UPDATE Users 
                    SET usr_money=usr_money-?, 
                        usr_premium_expire=usr_premium_expire+INTERVAL ? DAY 
                    WHERE usr_id=?",$c->{convert_money},$c->{convert_days},$ses->getUserId);
      }
      else
      {
         $db->Exec("UPDATE Users 
                    SET usr_money=usr_money-?, 
                        usr_premium_expire=NOW()+INTERVAL ? DAY 
                    WHERE usr_id=?",$c->{convert_money},$c->{convert_days},$ses->getUserId);
      }
      $ses->redirect_msg("$c->{site_url}/?op=my_account","Your premium account extended for $c->{convert_days} days");
   }
   if($f->{convert_new_acc})
   {
      $ses->message("You need at least \$$c->{convert_money}") if $money<$c->{convert_money};
      my $login = join '', map int rand 10, 1..7;
      while($db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$login)){ $login = join '', map int rand 10, 1..7; }
      my $password = $ses->randchar(10);
      $db->Exec("INSERT INTO Users (usr_login,usr_password,usr_created,usr_premium_expire,usr_aff_id) VALUES (?,ENCODE(?,?),NOW(),NOW()+INTERVAL ? DAY,?)",$login,$password,$c->{pasword_salt},$c->{convert_days},$ses->getUserId);
      $db->Exec("UPDATE Users SET usr_money=usr_money-? WHERE usr_id=?",$c->{convert_money},$ses->getUserId);
      $ses->message("$ses->{lang}->{lang_account_generated}<br>$ses->{lang}->{lang_login} / $ses->{lang}->{lang_password}:<br>$login<br>$password");
   }
   if($f->{convert_profit})
   {
      $ses->message("You need at least \$$c->{min_payout}") if $money<$c->{min_payout};
      $ses->message("Profit system is disabled") unless $c->{min_payout};
      $ses->message("Enter Payment Info in you account settings") unless $ses->getUser->{usr_pay_email};

      $db->Exec("UPDATE Users SET usr_money=0 WHERE usr_id=?",$ses->getUserId);
      my $exist_id = $db->SelectOne("SELECT id FROM Payments WHERE usr_id=? AND status='PENDING'",$ses->getUserId);
      if($exist_id)
      {
         $db->Exec("UPDATE Payments SET amount=amount+? WHERE id=?",$money,$exist_id);
      }
      else
      {
         $db->Exec("INSERT INTO Payments SET usr_id=?,amount=?,status='PENDING',created=NOW()",$ses->getUserId,$money);
      }
      $ses->redirect_msg("$c->{site_url}/?op=request_money",$ses->{lang}->{lang_payout_requested});
   }

   my $pay_req = $db->SelectOne("SELECT SUM(amount) FROM Payments WHERE usr_id=? AND status='PENDING'",$ses->getUserId);

   my $convert_enough = 1 if $money >= $c->{convert_money};
   my $payout_enough = 1 if $money >= $c->{min_payout};
   $money = sprintf("%.02f",$money);

   $ses->PrintTemplate("request_money.html",
                       'usr_money'           => $money,
                       'convert_days'        => $c->{convert_days},
                       'convert_money'       => $c->{convert_money},
                       'payment_request'     => $pay_req,
                       'payout_enough'       => $payout_enough,
                       'convert_enough'      => $convert_enough,
                       'enabled_prem'        => $c->{enabled_prem},
                       'min_payout'          => $c->{min_payout},
                       'msg'                 => $f->{msg},
                      );
}

sub ReportFile
{
   my $file = $db->SelectRow("SELECT * FROM Files WHERE file_code=?",$f->{id});
   $ses->message("No such file") unless $file;
   $c->{captcha}=1;
   my %secure = $ses->SecSave( 2, 5 );
   $f->{$_}=$ses->SecureStr($f->{$_}) for keys %$f;
   $f->{email}||=$ses->getUser->{usr_email} if $ses->getUser;
   $ses->PrintTemplate("report_file.html",
                       %{$f},
                       %secure,
                       'file_name' => $file->{file_name},
                       'ip'   => $ses->getIP(),
                      );
}

sub ReportFileSend
{
   &ReportFile unless $ENV{REQUEST_METHOD} eq 'POST';
   $c->{captcha}=1;
   &ReportFile unless $ses->SecCheck( $f->{'rand'}, 2, $f->{code} );
   my $file = $db->SelectRow("SELECT * FROM Files WHERE file_code=?",$f->{id});
   $ses->message("No such file") unless $file;

   $f->{msg}.="Email is not valid. " unless $f->{email} =~ /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
   $f->{msg}.="Name required. " unless $f->{name};
   $f->{msg}.="Message required. " unless $f->{message};
   
   &ReportFile if $f->{msg};

   #$f->{message}="Reason: $f->{reason}\n\n$f->{message}";
   $f->{$_}=$ses->SecureStr($f->{$_}) for keys %$f;

   $db->Exec("INSERT INTO Reports SET file_id=?, usr_id=?, filename=?, name=?, email=?, reason=?, info=?, ip=INET_ATON(?), status='PENDING', created=NOW()",
             $file->{file_id}, $file->{usr_id}, $file->{file_name}, $f->{name}, $f->{email}, $f->{reason}, $f->{message}, $ses->getIP() );
   $f->{subject} = "$c->{site_name}: File reported";
   $f->{message} = "File was reported on $c->{site_name}.\n\nFilename: $file->{file_name}\n\nName: $f->{name}\nE-mail: $f->{email}\nReason: $f->{reason}\nIP: $ENV{REMOTE_ADDR}\n\n$f->{message}";
   $c->{email_text}=1;
   $ses->SendMail($c->{contact_email}, $c->{email_from}, $f->{subject}, $f->{message});
   $ses->redirect("$c->{site_url}/?msg=Report sent successfully");
}

sub AdminReports
{
   $ses->message("Access denied") if !$ses->getUser->{usr_adm} && !($c->{m_d} && $ses->getUser->{usr_mod} && $c->{m_d_a});
   if($f->{report_hide})
   {
      $db->Exec("UPDATE Reports SET status='DECLINED' WHERE id=?",$f->{report_hide});
      $ses->redirect("$c->{site_url}/?op=admin_reports");
   }
   if($f->{report_delete})
   {
      $db->Exec("DELETE FROM Reports WHERE id=?",$f->{report_delete});
      $ses->redirect("$c->{site_url}/?op=admin_reports&history=$f->{history}");
   }
   if($f->{nuke_file_id})
   {
      my $file = $db->SelectRow("SELECT * FROM Files WHERE file_id=?",$f->{nuke_file_id});
      my $ban=",ban_size='$file->{file_size}', ban_md5='$file->{file_md5}' " if $f->{ban};
      $db->Exec("UPDATE Reports SET status='APPROVED'$ban WHERE file_id=?",$f->{nuke_file_id});
      $ses->DeleteFile($file);
      $ses->redirect("$c->{site_url}/?op=admin_reports");
   }
   my $filter_status = $f->{history} ? "WHERE status<>'PENDING'" : "WHERE status='PENDING'";
   my $list = $db->SelectARef("SELECT r.*, f.*, INET_NTOA(ip) as ip,
                               (SELECT u.usr_login FROM Users u WHERE r.usr_id=u.usr_id) as usr_login
                               FROM Reports r 
                               LEFT JOIN Files f ON r.file_id = f.file_id
                               $filter_status
                               ORDER BY r.created DESC".$ses->makePagingSQLSuffix($f->{page}));
   my $total = $db->SelectOne("SELECT COUNT(*)
                               FROM Reports r
                               $filter_status");
   for(@$list)
   {
      $_->{site_url} = $c->{site_url};
      $_->{file_size2} = sprintf("%.02f Mb",$_->{file_size}/1048576);
      $_->{info} =~ s/\n/<br>/gs;
      $_->{"status_$_->{status}"}=1;
      $_->{status}.=', BANNED' if $_->{ban_size};
   }
   $ses->PrintTemplate("admin_reports.html",
                       'list'    => $list,
                       'paging'  => $ses->makePagingLinks($f,$total),
                       'history' => $f->{history},
                      );
}

sub AdminAntiHack
{
   my $gen_ip = $db->SelectARef("SELECT INET_NTOA(ip) as ip_txt, SUM(money) as money, COUNT(*) as downloads
                                 FROM IP2Files 
                                 WHERE created>NOW()-INTERVAL 48 HOUR
                                 GROUP BY ip
                                 ORDER BY money DESC
                                 LIMIT 20");

   my $gen_user = $db->SelectARef("SELECT u.usr_login, u.usr_id, SUM(money) as money, COUNT(*) as downloads
                                 FROM IP2Files i, Users u
                                 WHERE created>NOW()-INTERVAL 48 HOUR
                                 AND i.usr_id=u.usr_id
                                 GROUP BY i.usr_id
                                 ORDER BY money DESC
                                 LIMIT 20");

   my $rec_user = $db->SelectARef("SELECT u.usr_login, u.usr_id, SUM(money) as money, COUNT(*) as downloads
                                 FROM IP2Files i, Users u
                                 WHERE created>NOW()-INTERVAL 48 HOUR
                                 AND i.owner_id=u.usr_id
                                 GROUP BY i.owner_id
                                 ORDER BY money DESC
                                 LIMIT 20");

   $ses->PrintTemplate("admin_anti_hack.html",
                       'gen_ip'     => $gen_ip,
                       'gen_user'   => $gen_user,
                       'rec_user'   => $rec_user,
                      );
}

sub APIGetLimits
{
   if($f->{login} && $f->{password})
   {
      &Login('no_redirect');
      $f->{error}="auth_error" unless $ses->getUser;
   }
   elsif($f->{session_id})
   {
      $ses->{cookies}->{$ses->{auth_cook}} = $f->{session_id};
      &CheckAuth();
   }
   my $utype = $ses->getUser ? ($ses->getUser->{premium} ? 'prem' : 'reg') : 'anon';
   $c->{$_}=$c->{"$_\_$utype"} for qw(max_upload_files max_upload_filesize download_countdown captcha ads bw_limit remote_url direct_links down_speed);

   my $type_filter = $utype eq 'prem' ? "AND srv_allow_premium=1" : "AND srv_allow_regular=1";
   my $server = $db->SelectRow("SELECT * FROM Servers 
                                WHERE srv_status='ON' 
                                AND srv_disk+? <= srv_disk_max
                                $type_filter
                                ORDER BY srv_last_upload 
                                LIMIT 1",$c->{max_upload_filesize}||100);
   my $ext_allowed     = join '|', map{uc($_)." Files|*.$_"} split(/\|/,$c->{ext_allowed});
   my $ext_not_allowed = join '|', map{uc($_)." Files|*.$_"} split(/\|/,$c->{ext_not_allowed});
   my $login_logic = 1 if !$c->{enabled_anon} && ($c->{enabled_reg} || $c->{enabled_prem});
      $login_logic = 2 if $c->{enabled_anon} && !$c->{enabled_reg} && !$c->{enabled_prem};
   print"Content-type:text/xml\n\n";
   print"<Data>\n";
   print"<ExtAllowed>$ext_allowed</ExtAllowed>\n";
   print"<ExtNotAllowed>$ext_not_allowed</ExtNotAllowed>\n";
   print"<MaxUploadFilesize>$c->{max_upload_filesize}</MaxUploadFilesize>\n";
   print"<ServerURL>$server->{srv_cgi_url}</ServerURL>\n";
   print"<SessionID>".$ses->{cookies_send}->{$ses->{auth_cook}}."</SessionID>\n";
   print"<Error>$f->{error}</Error>\n";
   print"<SiteName>$c->{site_name}</SiteName>\n";
   print"<LoginLogic>$login_logic</LoginLogic>\n";
   print"</Data>";
   exit;
}

sub CommentAdd
{
   &CheckAuth;
   $ses->message("File comments are not allowed") if $f->{cmt_type}==1 && !$c->{enable_file_comments};
   $ses->message("Invalid object ID") unless $f->{cmt_ext_id}=~/^\d+$/;
   #my $redirect = &CommentRedirect($f->{cmt_type},$f->{cmt_ext_id});
   if($f->{name} || $f->{email} || $f->{text})
   {
      sleep 10;
      $ses->message("bot!");
   }
   if($ses->getUser)
   {
      $f->{cmt_name} = $ses->getUser->{usr_login};
      $f->{cmt_email} = $ses->getUser->{usr_email};
   }
   $f->{usr_id} = $ses->getUser ? $ses->getUserId : 0;
   $f->{cmt_name}=~s/(http:\/\/|www\.|\.com|\.net)//gis;
   $f->{cmt_name}    = $ses->SecureStr($f->{cmt_name});
   $f->{cmt_email}   = $ses->SecureStr($f->{cmt_email});
   $f->{cmt_text}    = $ses->SecureStr($f->{cmt_text});
   $f->{cmt_text} =~ s/(\_n\_|\n)/<br>/g;
   $f->{cmt_text} =~ s/\r//g;
   $f->{cmt_text} = substr($f->{cmt_text},0,800);
   my $err;
   $err.="Name is required field<br>" unless $f->{cmt_name};
   $err.="E-mail is not valid<br>" if $f->{cmt_email} && $f->{cmt_email}!~/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
   $err.="Too short comment text<br>" if length($f->{cmt_text})<5;
   my $txt=$f->{cmt_text};
   $txt=~s/[\s._-]+//gs;
   $err.="Comment text contain restricted word" if $c->{bad_comment_words} && $txt=~/$c->{bad_comment_words}/i;
   print(qq{Content-type:text/html\n\n\$\$('cnew').innerHTML+="<b class='err'>$err</b><br><br>"}),exit if $err;

   $db->Exec("INSERT INTO Comments
              SET usr_id=?,
                  cmt_type=?,
                  cmt_ext_id=?,
                  cmt_ip=INET_ATON(?),
                  cmt_name=?,
                  cmt_email=?,
                  cmt_text=?
             ",$f->{usr_id},$f->{cmt_type},$f->{cmt_ext_id},$ses->getIP,$f->{cmt_name},$f->{cmt_email},$f->{cmt_text});
   $ses->setCookie('cmt_name',$f->{cmt_name});
   $ses->setCookie('cmt_email',$f->{cmt_email});
   #$ses->redirect($redirect,'+1m');
   print"Content-type:text/html\n\n";
   print qq{\$\$('cmt_txt').value='';\$\$('cnew').innerHTML+="<div class='cmt'><div class='cmt_hdr'><b>$f->{cmt_name}</b></div><p>$f->{cmt_text}</p></div>"};
   exit;
}

sub CommentDel
{
   $ses->message("Access denied") unless $ses->getUser && $ses->getUser->{usr_adm};
   $db->Exec("DELETE FROM Comments WHERE cmt_id=?",$f->{i});
   print"Content-type:text/html\n\n \$\$('cm$f->{i}').style.display='none';";
   exit;
}

sub CommentRedirect
{
   my ($cmt_type,$cmt_ext_id) = @_;
   if($cmt_type==1) # Files
   {
      my $file = $db->SelectRow("SELECT * FROM Files WHERE file_id=?",$cmt_ext_id);
      $ses->message("Object doesn't exist") unless $file;
      $ses->setCookie("skip$file->{file_id}",1);
      return $ses->makeFileLink($file).'#comments';
   }
   elsif($cmt_type==2) # News
   {
      my $news = $db->SelectRow("SELECT * FROM News WHERE news_id=?",$cmt_ext_id);
      $ses->message("Object doesn't exist") unless $news;
      return "$c->{site_url}/n$news->{news_id}-$news->{news_title2}.html#comments";
   }
   $ses->message("Invalid object type");
}

sub Links
{
   my @links;
   for(split(/~/,$c->{external_links}))
   {
      my ($url,$name)=split(/\|/,$_);
      $name||=$url;
      $url="http://$url" unless $url=~/^https?:\/\//i;
      push @links, {url=>$url,name=>$name};
   }
   $ses->PrintTemplate('links.html',links => \@links);
}

###
sub ARef
{
  my $data=shift;
  $data=[] unless $data;
  $data=[$data] unless ref($data) eq 'ARRAY';
  return $data;
}

sub getTime
{
    my ($t) = @_;
    my @t = $t ? localtime($t) : localtime();
    return ( sprintf("%04d",$t[5]+1900),
             sprintf("%02d",$t[4]+1), 
             sprintf("%02d",$t[3]), 
             sprintf("%02d",$t[2]), 
             sprintf("%02d",$t[1]), 
             sprintf("%02d",$t[0]) 
           );
}

sub makeSortSQLcode
{
  my ($f,$default_field) = @_;
  
  my $sort_field = $f->{sort_field} || $default_field;
  my $sort_order = $f->{sort_order} eq 'down' ? 'DESC' : '';

  return " ORDER BY $sort_field $sort_order ";
}

sub makeSortHash
{
   my ($f,$fields) = @_;
   my @par;
   foreach my $key (keys %{$f})
   {
    next if $key=~/^(sort_field|sort_order)$/i;
    my $val = $f->{$key};
    push @par, (ref($val) eq 'ARRAY' ? map({"$key=$_"}@$val) : "$key=$val");
   }
   my $params = join('&amp;',@par);
   my $sort_field = $f->{sort_field};
   my $sort_order = $f->{sort_order};
   $sort_field ||= $fields->[0];
   my $sort_order2 = $sort_order eq 'down' ? 'up' : 'down';   
   my %hash = ('sort_'.$sort_field         => 1,
               'sort_order_'.$sort_order2  => 1,
               'params'                    => $params,
              );
   for my $fld (@$fields)
   {
      if($fld eq $sort_field)
      {
         $hash{"s_$fld"}  = "<a href='?$params&amp;sort_field=$fld&amp;sort_order=$sort_order2'>";
         $hash{"s2_$fld"} = "<img border=0 src='$c->{site_url}/images/$sort_order.gif'>"
      }
      else
      {
         $hash{"s_$fld"}  = "<a href='?$params&amp;sort_field=$fld&amp;sort_order=down'>";
      }
      $hash{"s2_$fld"}.= "</a>";
   }

   return %hash;
}

