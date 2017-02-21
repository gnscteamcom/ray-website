#!/usr/bin/perl
use strict;
use XFSConfig;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use XUpload;

my $q = new CGI;
my $f;
$f->{$_}=$q->param($_) for $q->param();


my $file;
$file->{file_tmp} = $q->tmpFileName($f->{Filedata});
$file->{file_name_orig} = $f->{Filename};
$file->{file_public} = 1;

$file = &XUpload::ProcessFile($file,$f);

print"Content-type:text/html\n\n";
print $file->{file_status} ? "$file->{file_status}" : "$file->{file_code}:$file->{file_real}:$file->{dx}:$file->{file_name_orig}:$file->{type}";

