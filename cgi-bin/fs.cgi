#!/usr/bin/perl
use strict;
use lib '.';
use XFileConfig;
use CGI::Simple;
use DataBase;
use Session;
use CGI::Carp qw(fatalsToBrowser);
#open STDERR, ">>logs.txt";

die"111" unless $ENV{REQUEST_METHOD} eq 'POST';
die"222" unless $ENV{HTTP_USER_AGENT} eq 'XFS-FSAgent';

my $q = new CGI::Simple;
my $f;
$f->{$_}=$q->param($_) for $q->param;

if($f->{op} eq 'test')
{
   print"Content-type:text/html\n\nOK:".$ENV{REMOTE_ADDR};
   exit;
}

my $db = DataBase->new();

my $server = $db->SelectRow("SELECT * FROM Servers WHERE srv_key=?", $f->{fs_key} );
die"333" unless $server;
#die"444" unless $server->{srv_ip} eq $ENV{REMOTE_ADDR};


$f->{usr_id} = $db->SelectOne("SELECT usr_id
                               FROM Sessions
                               WHERE session_id=?",$f->{sess_id}) if $f->{sess_id} && !$f->{usr_id};

if($f->{torrent} && $f->{sid})
{
   $f->{usr_id} = $db->SelectOne("SELECT usr_id FROM Torrents WHERE sid=?",$f->{sid});
   $db->Exec("UPDATE Torrents SET status='DONE' WHERE sid=?",$f->{sid});
}

my $user = $db->SelectRow("SELECT *, UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec,
                           (SELECT SUM(f.file_size) FROM Files f WHERE f.usr_id=u.usr_id) as total_size
                           FROM Users u 
                           WHERE u.usr_id=?",$f->{usr_id}) if $f->{usr_id};

$user = $db->SelectRow("SELECT *, UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec,
                        (SELECT SUM(f.file_size) FROM Files f WHERE f.usr_id=u.usr_id) as total_size
                        FROM Users u 
                        WHERE u.usr_login=?",$f->{usr_login}) if !$user && $f->{usr_login};

my $utype = $user ? ($user->{exp_sec}>0 ? 'prem' : 'reg') : 'anon';
$c->{$_}=$c->{"$_\_$utype"} for qw(disk_space max_upload_filesize max_rs_leech torrent_dl torrent_dl_slots);


my $sub={
         check_codes    => \&CheckCodes,
         update_srv     => \&UpdateServer,
         del_torrent    => \&TorrentDel,
         add_torrent    => \&TorrentAdd,
         torrent_stats  => \&TorrentStats,
         file_new_size  => \&FileNewSize,
         file_new_spec  => \&FileNewSpec,
	     }->{ $f->{op} };
if($sub)
{
   &$sub;
}
else
{
   &SaveFile if $f->{file_name};
}

sub CheckCodes
{
   my @codes = split(/\,/,$f->{codes});
   print("Content-type:text/html\n\nOK:"),exit unless @codes;
   my $ok = $db->SelectARef("SELECT file_real FROM Files WHERE file_real IN (".join(',', map{"'$_'"}@codes ).")");
   my %h;
   $h{$_->{file_real}}=1 for @$ok;
   my @bad;
   for(@codes)
   {
      push @bad,$_ unless $h{$_};
   }
   print"Content-type:text/html\n\nOK:".join(',',@bad);
}

sub TorrentDel
{
   $db->Exec("DELETE FROM Torrents WHERE sid=?",$f->{sid});
   print"Content-type:text/html\n\nOK";
}

sub UpdateServer
{
   my $info = $db->SelectRow("SELECT srv_id, file_size, count(*) as num
                              FROM Files 
                              WHERE file_real=?
                              GROUP BY file_real",$f->{file_real});
   $db->Exec("UPDATE Files SET srv_id=? WHERE file_real=?",$f->{srv_id},$f->{file_real});
   $db->Exec("UPDATE Servers SET srv_files=srv_files-?, srv_disk=srv_disk-? WHERE srv_id=?",$info->{num},$info->{file_size},$info->{srv_id});
   $db->Exec("UPDATE Servers SET srv_files=srv_files+?, srv_disk=srv_disk+? WHERE srv_id=?",$info->{num},$info->{file_size},$f->{srv_id});
   print"Content-type:text/html\n\nOK";
}

sub TorrentAdd
{
   print"Content-type:text/html\n\n";
   print("ERROR:This torrent already working"),exit if $db->SelectOne("SELECT sid FROM Torrents WHERE sid=?",$f->{sid});
   print("ERROR:This type of users is not allowed to upload torrents"),exit unless $c->{torrent_dl};
   print("ERROR:You're already using $c->{torrent_dl_slots} torrent slots"),exit 
      if $c->{torrent_dl_slots} && $db->SelectOne("SELECT COUNT(*) FROM Torrents WHERE usr_id=? AND status='WORKING'",$user->{usr_id})>=$c->{torrent_dl_slots};

   $db->Exec("INSERT INTO Torrents SET sid=?, usr_id=?, srv_id=?, files=?, progress='0:$f->{total_size}:0:0', created=NOW()",
              $f->{sid}, $user->{usr_id}, $server->{srv_id}, $f->{files} 
            );
   print"OK";
}

sub TorrentStats
{
   for(split(/\|/,$f->{data}))
   {
      next unless $_;
      my ($sid,$done,$total,$down_speed,$up_speed) = split(/:/,$_);
      $db->Exec("UPDATE Torrents SET progress=? WHERE sid=? AND status='WORKING'","$done:$total:$down_speed:$up_speed",$sid) if $sid;
   }
   print"Content-type:text/html\n\nOK";
}

sub SaveFile
{
   my $size  = $f->{file_size}||0;
   my $filename = $f->{file_name};
   my $descr = $f->{file_descr}||'';
   
   unless($f->{no_limits})
   {
      if( $c->{max_upload_filesize} && $size>$c->{max_upload_filesize}*1024*1024 )
      {
         print"Content-type:text/html\n\n";
         print"0:0:0:file is too big";
         exit;
      }
      $c->{disk_space} = $user->{usr_disk_space} if $user && $user->{usr_disk_space};
      if($c->{disk_space} && $user->{total_size}+$size > $c->{disk_space}*1048576)
      {
         print"Content-type:text/html\n\n";
         print"0:0:0:not enough disk space on your account";
         exit;
      }
      if($c->{fnames_not_allowed})
      {
          $filename=~s/$c->{fnames_not_allowed}/_/gi;
      }
      if($f->{rslee})
      {
         print("Content-type:text/html\n\n0:0:0:RS leech not allowed for you"),exit 
            unless $c->{"\x6d\x5f\x72"} && $user;

         if($c->{max_rs_leech})
         {
            my $leech_left_mb = $c->{max_rs_leech} - $db->SelectOne("SELECT ROUND(SUM(size)/1048576) FROM IP2RS WHERE created>NOW()-INTERVAL 24 HOUR AND (usr_id=? OR ip=INET_ATON(?))",$user->{usr_id},$f->{file_ip});
            print("Content-type:text/html\n\n0:0:0:You've used all Free Leech traffic today"),exit 
               if $leech_left_mb <= 0;
         }
         $db->Exec("INSERT INTO IP2RS SET usr_id=?, ip=INET_ATON(?), size=?",$user->{usr_id},$f->{file_ip},$size);
      }
      if( ($c->{ext_allowed} && $filename!~/\.($c->{ext_allowed})$/i) || ($c->{ext_not_allowed} && $filename=~/\.($c->{ext_not_allowed})$/i) )
      {
         print"Content-type:text/html\n\n";
         print"0:0:0:unallowed extension";
         exit;
      }
   }
   
   
   $filename=~s/%(\d\d)/chr(hex($1))/egs;
   $filename=~s/%/_/gs;
   $filename=~s/\s{2,}/ /gs;
   $filename=~s/[\#\"]+/_/gs;
   $filename=~s/[^\w\d\.-]/_/g if $c->{sanitize_filename};
   $filename=~s/\.(\w+)$/"$c->{add_filename_postfix}\.$1"/e if $c->{add_filename_postfix};
   $descr=~s/</&lt;/gs;
   $descr=~s/>/&gt;/gs;
   $descr=~s/"/&quote;/gs;
   $descr=~s/\(/&#40;/gs;
   $descr=~s/\)/&#41;/gs;

   my $usr_id = $user ? $user->{usr_id} : 0;

   if($f->{fld_name} && $usr_id)
   {
      $f->{fld_id} = $db->SelectOne("SELECT fld_id FROM Folders WHERE usr_id=? AND fld_parent_id=0 AND fld_name=?",$usr_id,$f->{fld_name});
      unless($f->{fld_id})
      {
         $db->Exec("INSERT INTO Folders SET usr_id=?, fld_parent_id=0, fld_name=?",$usr_id,$f->{fld_name});
         $f->{fld_id} = $db->getLastInsertId;
      }
   }
   
   my $md5 = $f->{file_md5}||'';
   my $code = &randchar(12);
   while($db->SelectOne("SELECT file_id FROM Files WHERE file_code=?",$code)){$code = &randchar(12);}
   my $del_id = &randchar(10);
   
   if($db->SelectOne("SELECT id FROM Reports WHERE ban_size=? AND ban_md5=? LIMIT 1",$size,$md5))
   {
      print"Content-type:text/html\n\n";
      print"0:0:0:this file is banned by administrator";
      exit;
   }
   
   my $ex = $db->SelectRow("SELECT * FROM Files WHERE file_size=? AND srv_id=? AND file_md5=? LIMIT 1",$size,$server->{srv_id},$md5)
            if $c->{anti_dupe_system};
   my $real = $ex->{file_real} if $ex;
   my $real_id = $ex->{file_id} if $ex;
   $f->{file_spec}=$ex->{file_spec} if $ex;
   #$server->{srv_id} = $ex->{srv_id} if $ex;
   $real ||= $code;
   
   $db->Exec("INSERT INTO Files 
              SET file_name=?, usr_id=?, srv_id=?, file_descr=?, file_fld_id=?, file_public=?, file_code=?, file_real=?, file_real_id=?, file_del_id=?, file_size=?, 
                  file_password=?, file_ip=INET_ATON(?), file_md5=?, file_spec=?, file_created=NOW(), file_last_download=NOW()",
               $filename,
               $usr_id,
               $server->{srv_id},
               $descr,
               $f->{fld_id}||0,
               $f->{file_public}||0,
               $code,
               $real,
               $real_id||0,
               $del_id,
               $size,
               $f->{file_password}||'',
               $f->{file_ip}||'1.1.1.1',
               $md5,
               $f->{file_spec}||'',
             );
   
   my $file_id = $db->getLastInsertId;
   $size=0 unless $code eq $real;
   $db->Exec("UPDATE Servers 
              SET srv_files=srv_files+1, 
                  srv_disk=srv_disk+?, 
                  srv_last_upload=NOW() 
              WHERE srv_id=?", $size, $server->{srv_id} );
   
   $db->Exec("INSERT INTO Stats SET day=CURDATE(), uploads=1 ON DUPLICATE KEY UPDATE uploads=uploads+1");
   
   if($f->{compile})
   {
      my $ses = Session->new();
      my $link = $ses->makeFileLink({ file_code=>$code, file_name=>$filename });
      my $del_link="$link?killcode=$del_id";
      print"Content-type:text/html\n\n";
      print"$file_id:$code:$real:OK=$link|$del_link";
      exit;
   }
   
   print"Content-type:text/html\n\n";
   print"$file_id:$code:$real:OK";
}

sub FileNewSize
{
   my $file = $db->SelectRow("SELECT * FROM Files WHERE file_code=?",$f->{file_code});
   $db->Exec("UPDATE Files SET file_size=?, file_name=? WHERE file_code=?",$f->{file_size},$f->{file_name},$f->{file_code});
   $db->Exec("UPDATE Servers SET srv_disk=srv_disk+? WHERE srv_id=?",($f->{file_size}-$file->{file_size}),$file->{srv_id});
   print"Content-type:text/html\n\nOK";
}

sub FileNewSpec
{
   if($f->{file_code} && $f->{file_size} && $f->{encoded})
   {
      $db->Exec("UPDATE Files 
                 SET file_name=CONCAT(file_name,'.mp4'), file_spec=?, file_size=? 
                 WHERE file_real=?",$f->{file_spec},$f->{file_size},$f->{file_code});
   }
   elsif($f->{file_code} && $f->{file_size})
   {
      $db->Exec("UPDATE Files 
                 SET file_spec=?, file_size=? 
                 WHERE file_real=?",$f->{file_spec},$f->{file_size},$f->{file_code});
   }
   elsif($f->{file_code})
   {
      $db->Exec("UPDATE Files 
                 SET file_spec=?
                 WHERE file_real=?",$f->{file_spec},$f->{file_code});
   }
   print"Content-type:text/html\n\nOK";
}

#################
sub randchar
{ 
   my @range = ('0'..'9','a'..'z');
   my $x = int scalar @range;
   join '', map $range[rand $x], 1..shift||1;
}
