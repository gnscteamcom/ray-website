#!/usr/bin/perl
# SQL Upgrade script from XFS Pro
use strict;
use XFileConfig;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
use DataBase;

my $db = DataBase->new();
die"Can't connect to DB" unless $db;

my $kk = $c->{profit_amount}/$c->{profit_points} if $c->{profit_amount} && $c->{profit_points};
$kk||=0;

$db->Exec("ALTER TABLE Users ADD COLUMN usr_money decimal(11,5) unsigned NOT NULL default '0.00000'");

$db->Exec("UPDATE Users SET usr_money = usr_points*$kk WHERE usr_points>0");
$db->Exec("UPDATE Stats2 SET profit_dl=profit_dl*$kk, 
                             profit_sales=profit_sales*$kk, 
                             profit_refs=profit_refs*$kk");


open(FILE,"upgrade_17_18.sql")||die("Can't open sql");
my $sql;
$sql.=$_ while <FILE>;
$sql=~s/CREATE TABLE/CREATE TABLE IF NOT EXISTS/gis;
$db->Exec($_) for grep{length($_)>3} split(';',$sql);

my $mode = 0777;
chmod $mode,'index_dl.cgi';

print"Content-type:text/html\n\nDONE.";