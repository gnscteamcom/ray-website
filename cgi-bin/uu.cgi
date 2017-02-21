#!/usr/bin/perl
use strict;
use XFSConfig;
use CGI::Simple;
$CGI::Simple::DISABLE_UPLOADS = 0;
$CGI::Simple::POST_MAX = -1;
use CGI::Carp qw(fatalsToBrowser);
use File::Copy;

my $q = new CGI::Simple;

my $dx = $q->param('dx');
my $file1 = $q->param('file1');
my $file2 = $q->param('file2');

my $dir=$c->{upload_dir};
my $idir = $c->{htdocs_dir};
   $idir=~s/^(.+)\/.+$/$1\/i/;

unless(-d "$dir/$dx")
{
    my $mode = 0777;
    mkdir("$dir/$dx",$mode);
    chmod $mode,"$dir/$dx";
}
unless(-d "$idir/$dx")
{
    my $mode = 0777;
    mkdir("$idir/$dx",$mode);
    chmod $mode,"$idir/$dx";
}

$q->upload($file1, "$dir/$dx/$file1")  || die("Can't move file $file1:$!") if $file1;

if($file2)
{
   $q->upload($file2, "$idir/$dx/$file2") || die("Can't move file $file2:$!");
   symlink("$dir/$dx/$file1","$idir/$dx/$file1.".$q->param('ext')) if $q->param('ext');
}


my $mode = 0666;
chmod $mode, "$dir/$dx/$file1"   if $file1;
chmod $mode, "$idir/$dx/$file2"  if $file2;

print"Content-type:text/html\n\n";
print"OK";