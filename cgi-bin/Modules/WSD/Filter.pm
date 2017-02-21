package WSD::Filter;

use 5.006000;
#use strict;
#use warnings;

our $VERSION = '1.0';

require DynaLoader;
@ISA = qw(DynaLoader);
my $perlver = '508';
$perlver = '510' if($] >= 5.01);
#print $];
my @v = ('32', '32_3', '32_2', '32_4', '64', '64_3', '64_4', '64_2');
my $libref = undef;
my $file_version;
while(@v && !$libref) {
	my $bit = shift @v;
	$file_version = $perlver.$bit;
	$libref = DynaLoader::dl_load_file("Modules/WSD/Filter$file_version.so");
}
#print "$libref\n";
my $symref = DynaLoader::dl_find_symbol($libref, 'boot_WSD__Filter');
#print "$symref\n";
my $xs = DynaLoader::dl_install_xsub('WSD::Filter::bootstrap', $symref);
#print "$xs\n";
&$xs('WSD::Filter');
1;
