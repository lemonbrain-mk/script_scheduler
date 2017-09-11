#!/bin/bash 

#Run this as sudo and to do so do this in advanced
#sudo chown root:root /path/to/file/backup.sh
#sudo chmod 700 /path/to/file/backup.sh
#sudo visudo
#Scroll down to %sudo   ALL=(ALL:ALL) ALL
#and add under it: username  ALL=(ALL) NOPASSWD: /path/to/file/backup.sh
#save and exit

if [ "$1" == "run_script" ]; then
	echo "*************************************************"
	echo "-------------------------------------------------"
	echo "create_backup has started at $(date)"
	echo "-------------------------------------------------"

	PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

	if ping -c 1 193.168.200.200
	then
		echo ""
		echo "Start backup"
		echo ""
		#ZREP_PATH=/opt/local/bin/zrep /usr/local/sbin/zrep -S all
		echo ""
		echo "Backup finished at $(date)"
		echo ""
	else
		echo ""
		echo "Backupserver not found"
		echo ""
	fi
	echo ""
	echo "-------------------------------------------------"
	echo ""
elif [ "$1" == "copy_autostart" ] && [ "x$2" != "x"  ] && [ "x$3" != "x" ]; then
	shopt -s nullglob dotglob	
	if [ ! -f "$3" ]; then
		echo "*************************************************"
		echo "-------------------------------------------------"
		echo "copy_autostart has started at $(date)"
		echo "-------------------------------------------------"
		sudo cp $2 $3
		sudo chown marcokuoni:marcokuoni $3
		sudo chmod 664 $3
		echo ""
		echo "-------------------------------------------------"
		echo ""
	fi
	shopt -u nullglob dotglob
elif [ "$1" == "remove_autostart" ] && [ "x$2" != "x" ]; then
        shopt -s nullglob dotglob
	if [ -f "$2" ]; then
		echo "*************************************************"
		echo "-------------------------------------------------"
		echo "remove_autostart has started at $(date)"
		echo "-------------------------------------------------"
		sudo rm $2
		echo ""
		echo "-------------------------------------------------"
		echo ""
	fi
	shopt -u nullglob dotglob
fi
