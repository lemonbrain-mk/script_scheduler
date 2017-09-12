# Script Scheduler
Runs scripts on timely bases
Create a script wich will be running on a timley base. In default it will be a zrep sync script which runs every hour. you will get feedback on your Ubuntu status bar. When the script was runned the last time and if it is currently running. You can also add the Script Scheduler to your autostart programms, start the script manualy, read the current log file or quit it, all through the status bar. 
Just follow this instructions or run the script_scheduler.pyt script in a terminal and try on yourself ;)
Please also read the small LICENSE and have fun with the Script Scheduler. I'm always open for some contributions, comments and helps and if it is just cause of my english ;)

![Script Scheduler](https://lemonbrain.ch/application/files/6215/0515/2249/ScriptScheduler.png)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

You need to install python 3

```
sudo apt-get update
sudo apt-get install python3
```

### Installing
#### Downloading

Now download the project to your favorite folder, my one would be /opt
```
cd /opt
sudo git clone https://github.com/lemonbrain-mk/script_scheduler.git
```

#### Configure your bash script
Open the bash script and add your lines in it
```
cd scirpt_scheduler
sudo vi backup.sh
```

Remove this lines and add yours
```
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
    ZREP_PATH=/opt/local/bin/zrep /usr/local/sbin/zrep -S all
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
```

Now save and quit it, press esc, :wq and enter

While we have to run this shell script as sudo we need to add it to the visudo file
```
sudo chown root:root /opt/script_scheduler/backup.sh
sudo chmod 700 /opt/script_scheduler/backup.sh
sudo visudo
Scroll down to %sudo   ALL=(ALL:ALL) ALL
and add under it: username  ALL=(ALL) NOPASSWD: /opt/script_scheduler/backup.sh
Now save and quit it, press esc, :wq and enter
```

#### Configure the Script Scheduler
open the config file
```
sudo vi script_scheduler.conf
```

Edit the configs
```
[SCRIPT_SCHEDULER]
scipt_scheduler_old_log_name = script_scheduler_old.log 		#Name of the old log file
shell_script_name = backup.sh 						#Name of the shell script file
autostart_path = $HOME/.config/autostart				#Path to your autostart directory
idle_icon_path = icons/apps/24/script-scheduler-idle.svg 		#Path to the idle Icon
error_icon_path = icons/apps/24/script-scheduler-x.svg 			#Path to the error Icon
start_script_all_minutes = 60 						#Timebase for the shell script. Will be running every xx minutes
last_sync = Backuped 11.09.17 17:07 					#last run
busy_icons_path = icons/apps/24/script-scheduler-busy.svg 		#Path to the busy Icon
autostart_enabled = True 						#Autostart of Script Scheduler
autostart_script_name = script_scheduler.desktop 			#Name of the autostart file
scipt_scheduler_log_name = script_scheduler.log 			#Name of the current log file
busy_icons_path2 = icons/apps/24/script-scheduler-busy2.svg 		#Path to the second busy Icon
last_sync_text = Backuped 						#Text in front of the last run date
max_log_size = 20480							#Max Log file size
app_name = script_scheduler						#App name
last_sync_time_format = %d.%m.%y %H:%M					#Format of the last run date
```

Now save and quit it, press esc, :wq and enter

#### Run the Script Scheduler
```
./scipt_scheduler.pyt
```

Now you can see a new icon in your status bar and your shell script will be running the first time. Click on the icon to manually run the script, to add Script Scheduler to your autostart programs, to see the log file or to just quit the Script Scheduler.

![Script Scheduler](https://lemonbrain.ch/application/files/6215/0515/2249/ScriptScheduler.png)

## Tests
I tested and developed the Script Scheduler on my [ZFS Ubuntu 16.04](https://github.com/zfsonlinux/zfs/wiki/Ubuntu-16.04-Root-on-ZFS).

## Contributing

Please read [CONTRIBUTING.md](https://github.com/lemonbrain-mk/script_scheduler/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/lemonbrain-mk/script_scheduler/tags). 

## Authors

* **Marco Kuoni** - *Initial work* - [Script Scheduler](https://github.com/lemonbrain-mk/script_scheduler)

See also the list of [contributors](https://github.com/lemonbrain-mk/script_scheduler/contributors) who participated in this project.

## License

This project is licensed under a small License - see the [LICENSE](LICENSE) file for details

## Acknowledgments
* I use this scheduler to run a [zrep sync](http://www.bolthole.com/solaris/zrep/) all hours from my [ZFS Ubuntu 16.04](https://github.com/zfsonlinux/zfs/wiki/Ubuntu-16.04-Root-on-ZFS) to my backup server (based on a [SmartOS](https://www.joyent.com/smartos)) as long as the computer is running and the server is reachable.
* It is not possible to run your script two times parallel, it just will ignore your second call
* It always try to shutdown savely and waits until your script is finish. As long as the OS does not force the shotdown
* if you delete the *.conf or the *.desktop file, it will create a new one with just all default settings in it. If you edit the files, it will always read the settings from the files.
