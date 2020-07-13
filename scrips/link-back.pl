#!/usr/bin/perl
@a=glob('*.svg');
foreach $b (@a)
   {
    $b=~s/\.svg/\.back\.svg/;
    $cmd="ln -s ../dummy/dummy.svg $b\n";
    print($cmd);
    `$cmd`;
   }
