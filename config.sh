#! /bin/sh

LOGFILE="/app/logs/config.log"

echo "USB inserted" > $LOGFILE

if [ -f /media/CONFIG/wpa_supplicant.conf ]
then
	echo "Config file found, copying..." >> $LOGFILE
	sudo cp /media/CONFIG/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
	sudo chmod 755 /etc/wpa_supplicant/wpa_supplicant.conf
	echo "Copy complete." >> $LOGFILE
else
	echo "config file did not exist" >> $LOGFILE
fi