#!/usr/bin/perl
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib '.';
use index_dl;

&index_dl::run();
