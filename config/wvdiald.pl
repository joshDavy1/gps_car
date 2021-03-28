#!/usr/bin/perl -l
# wvdiald.pl - Auto connect USB modems on Linux
# Author: naveenk <dndkumarasnghe@gmail.com>
# License: MIT
# Make sure you have wvdial and usb-modeswitch installed. Fill the connection parameters below.
# Run this as root. Add "perl /path/to/wvdiald.pl" to /etc/rc.local to make this a service

######################### CHANGE AS NEEDED ################################

# connection parameters
my $MODEM = '/dev/ttyUSB2';     # can be ttyUSB0, ttyUSB1 or ttyUSB2
my $APN = 'mobile.o2.co.uk';          		# ask your Internet service provider
my $USERNAME = 'o2web';          # ignore if you're not given one
my $PASSWORD = 'password';          # ignore if you're not given one
my $PHONE = '*99#';             # usually *99# or *99***1#
my $BAUD_RATE = 460800;         # modem's communication speed. usually 9600, 57600, 115200 460800 or 760000
my $NOTIFICATION_EMAIL = '';      	  			                    # email to notify when connection is up
my $DEFAULT_INTERNET_INTERFACE = 'ppp0';                        # route Internet through this interface

###########################################################################

# AT commands
my $AT_CMD_1='ATZ';
my $AT_CMD_2='ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0';
my $AT_CMD_3='AT+CGDCONT=1,"IP","' . $APN . '"';
my $AT_CMD_4='AT+CNMP=2';
my $AT_CMD_5='AT+CGPS=0';
my $AT_CMD_6='AT+CGPS=1,2';
my $AT_CMD_7='AT+CGPSXE=1';
#my $AT_CMD_7='AT+CGNSSMODE=15,1';
#my $AT_CMD_W='WAIT=2';

###########################################################################

use threads;
use Sys::Hostname;
use autodie;
my $thr;
$|=1;   # enable immediate STDOUT flushing

sub setDefaultInternetInterface{
	$SIG{'KILL'} = sub { threads->exit(); };
	print "Waiting to default $DEFAULT_INTERNET_INTERFACE...";
	while(system("route add default $DEFAULT_INTERNET_INTERFACE") != 0){ sleep(1);}
	print "$DEFAULT_INTERNET_INTERFACE is now the default Internet interface.";
	system('printf "Subject: $USER@' . hostname . '\nwvdiald.pl: USB modem connected to Internet." | sendmail ' . $EMAIL);
}

# write config
open CONFIGFILE, ">/tmp/wvdial.conf";
print CONFIGFILE "[Dialer Defaults]";
print CONFIGFILE "Modem=$MODEM";
print CONFIGFILE "Phone=$PHONE";
print CONFIGFILE "Username=$USERNAME";
print CONFIGFILE "Password=$PASSWORD";
print CONFIGFILE "Init1=$AT_CMD_1";
print CONFIGFILE "Init2=$AT_CMD_4";
print CONFIGFILE "Init3=$AT_CMD_2";
print CONFIGFILE "Init4=$AT_CMD_3";
print CONFIGFILE "Baud=$BAUD_RATE";
print CONFIGFILE "Modem Type=Analog Modem";
print CONFIGFILE "Stupid mode=1";
print CONFIGFILE "Dial Command=ATDT";
print CONFIGFILE "Abort on Busy=yes";
print CONFIGFILE "Dial Attempts=1";
print CONFIGFILE "ISDN=0";
print CONFIGFILE "Init5=$AT_CMD_5";
#print CONFIGFILE "Init6=$AT_CMD_W";
print CONFIGFILE "Init7=$AT_CMD_6";
print CONFIGFILE "Init8=$AT_CMD_7";
#print CONFIGFILE "Init9=$AT_CMD_8";
close CONFIGFILE; 

# start wvdial loop
while(1){
        # if modem exists
        if (-e $MODEM){
                # set modem as the default internet when ready
                $thr = threads->create(\&setDefaultInternetInterface);
                print "Dialing modem on $MODEM...";
                system("wvdial --config=/tmp/wvdial.conf");
                $thr->kill('KILL')->join();
                print "Connection failed on $MODEM.";
        }
        sleep(5);
}
