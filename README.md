# AdventurePhotoFrame
This is the set of scripts and configuration steps for creating a PhotoFrame client for the Adventure project.

# Setup Instructions

1) Download Raspbian
	https://www.raspberrypi.org/downloads/raspbian/
	
2) Flash Rasbian to SD card
	https://www.raspberrypi.org/documentation/installation/installing-images/windows.md

3) Put all the hardware together and boot with keyboard and mouse hooked up

4) Boot, connect to WiFi

5) Change pi password
	passwd
	[enter unique password]

## Clean up the Pi software

6) Update everything
	sudo apt-get update
	sudo apt-get upgrade
	sudo apt-get dist-upgrade

7) Remove unused software:
	sudo apt-get remove --purge libreoffice*
	sudo apt-get remove --purge wolfram-engine
	sudo apt-get remove --purge bluej
	sudo apt-get remove --purge claws-mail
	sudo apt-get remove --purge greenfoot
	sudo apt-get remove --purge geany
	sudo apt-get remove --purge minecraft-pi
	sudo apt-get remove --purge nodered
	sudo apt-get remove --purge sonic-pi
	sudo apt-get remove --purge scratch
	
	sudo apt-get autoremove
	sudo apt-get clean
	
## Begin configuring the Pi
	
8) Disable screen blanking
	If you want to disable the blank screen at every startup, just update the `/etc/lightdm/lightdm.conf` file and add in the `[SeatDefaults]` section the following command:

	[SeatDefaults]
	xserver-command=X -s 0 -dpms
	You need root rights to update the lightdm.conf file. You can use the nano editor:
	sudo nano /etc/lightdm/lightdm.conf

9) Disable WiFi power saving

	sudo iw dev wlan0 set power_save off

10) Configure wlan0
(http://weworkweplay.com/play/automatically-connect-a-raspberry-pi-to-a-wifi-network/)

	sudo nano /etc/network/interfaces
	

Add this line to the top of the file:

	auto wlan0

Ensure the wlan0 section of the file looks like this:

	allow-hotplug wlan0
	iface wlan0 inet dhcp
	wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
	iface default inet dhcp

11) Setup the app fileshare

	sudo apt-get install samba samba-common-bin
	sudo nano /etc/samba/smb.conf

Edit these params:

	workgroup = BROWNTOWN
	wins support = yes
	
Add this new section:

	[app]
		comment= App
		path=/app
		browseable=Yes
		read only=no
		only guest=no
		create mask=0755
		directory mask=0755
		public=yes

Configure the user:

	 smbpasswd -a pi
	 #User the pis logon password

12) Hide boot logs

	sudo nano /boot/cmdline.txt
	
Change:

	console=tty1
To:

	console=tty9 loglevel=3 logo.nologo
Now you can use Ctrl+Alt+F9 to see the logs, and `logo.nologo` removes the RaspberryPi images
	
13) Splash Screen

	sudo apt-get install fbi
	sudo nano /etc/init.d/asplashscreen
	
Paste contents of asplashscreen into asplashscreen
	
Copy `splash.png` into `/app` directory

	sudo mv /app/splash.png /etc
	
	sudo chmod a+x /etc/init.d/asplashscreen
	sudo insserv /etc/init.d/asplashscreen
	
## Install the App

14) Configure USB config udev rules

Copy `11-media-by-label-auto-mount.rules` and `app_config.rules` into `/app`
	
	sudo mv 11-media-by-label-auto-mount.rules /etc/udev/rules.d
	sudo mv app_config.rules /etc/udev/rules.d
	
(*lsusb - find the usb info if needed*)

15) Setup crontab

	sudo crontab -e
	
Copy these contents into the root crontab:

	@reboot     /app/start_app.sh 2> /app/logs/app_errors.log
	00 00 * * * /app/update.sh > /app/logs/update.log 2>&1
	00 12 * * * /app/health.sh > /app/logs/health.log 2>&1
	00 00 1 * * /app/clean_up.sh

16) Install Python dependencies

	sudo apt-get install libjpeg-dev
	sudo apt-get install libpython-all-dev
	
	sudo pip install python-resize-image
	sudo pip install Pillow --upgrade
	
17) Copy latest zip into `/app` and extract

18) Copy `GOOGLE_MAPS_API_KEY` into `/app/config`

19) Create `PHOTO_FRAME_ID`

	sudo nano /app/config/PHOTO_FRAME_ID
	
Set to the next unique ID
	
20) Make all of the shell scripts executable

	sudo chmod +x /app/*.sh
	
21) Format USB drive with label: `CONFIG`
