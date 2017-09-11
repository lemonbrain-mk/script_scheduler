#!/usr/bin/env python3
"""Runs scripts on timely bases
Create a script wich will be running on a timley base. In default it will be a zrep sync 
script which runs every hour. you will get feedback on your Ubuntu status bar. When the script was 
runned the last time and if it is currently running. You can also add the Script Scheduler
to your autostart programms, start the script manualy, read the current log file or quit it, 
all through the status bar. 
Just follow the instructions on https://github.com/lemonbrain-mk/script_scheduler or run 
this script in a terminal and try on yourself ;)
Please also read the small LICENSE and have fun with the Script Scheduler
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GLib, GObject
import time, os, subprocess, webbrowser, sys, configparser, signal
from datetime import datetime, timedelta
from threading import Thread
from threading import Event
from shutil import copyfile

__author__ = "Marco Kuoni"
__copyright__ = "Copyright 2017, lemonbrain GmbH"
__credits__ = ["Marco Kuoni"]
__license__ = "Own"
__version__ = "1.0.0"
__maintainer__ = "Marco Kuoni"
__email__ = "marco@lemonbrain.ch"
__status__ = "Production"

def InitSignal(gui):
    def signal_action(signal):
        #if signal is 1:
            #print("Caught signal SIGHUP(1)")
        #elif signal is 2:
            #print("Caught signal SIGINT(2)")
        #elif signal is 15:
            #print("Caught signal SIGTERM(15)")
        gui.stop()

    def idle_handler(*args):
        #print("Python signal handler activated.")
        GLib.idle_add(signal_action, priority=GLib.PRIORITY_HIGH)

    def handler(*args):
        #print("GLib signal handler activated.")
        signal_action(args[0])

    def install_glib_handler(sig):
        unix_signal_add = None

        if hasattr(GLib, "unix_signal_add"):
            unix_signal_add = GLib.unix_signal_add
        elif hasattr(GLib, "unix_signal_add_full"):
            unix_signal_add = GLib.unix_signal_add_full

        if unix_signal_add:
            #print("Register GLib signal handler: %r" % sig)
            unix_signal_add(GLib.PRIORITY_HIGH, sig, handler, sig)
        #else:
            #print("Can't install GLib signal handler, too old gi.")

    SIGS = [getattr(signal, s, None) for s in "SIGINT SIGTERM SIGHUP SIGUSR1 SIGUSR2".split()]
    for sig in filter(None, SIGS):
        #print("Register Python signal handler: %r" % sig)
        signal.signal(sig, idle_handler)
        GLib.idle_add(install_glib_handler, sig, priority=GLib.PRIORITY_HIGH)



class ConfigHelper:
    config_file_name = "script_scheduler.conf"
    main_config_name = "SCRIPT_SCHEDULER"
    config = configparser.ConfigParser(interpolation = None)

    def __init__(self):
        if(not os.path.isfile(self.config_file_name)):
            self.config[self.main_config_name] = { 
                                "app_name": "script_scheduler",
                                "busy_icons_path": "icons/apps/24/script-scheduler-busy.svg",
                                "busy_icons_path2": "icons/apps/24/script-scheduler-busy2.svg",
                                "idle_icon_path": "icons/apps/24/script-scheduler-idle.svg",
                                "error_icon_path": "icons/apps/24/script-scheduler-x.svg",
                                "autostart_path": "$HOME/.config/autostart",
                                "max_log_size": 1024 * 20,
                                "start_script_all_minutes": 1 * 60,
                                "last_sync": "",
                                "autostart_enabled": False,
                                "last_sync_text": "Backuped ",
                                "last_sync_time_format": "%d.%m.%y %H:%M",
                                "scipt_scheduler_log_name": "script_scheduler.log",
                                "scipt_scheduler_old_log_name": "script_scheduler_old.log",
                                "shell_script_name": "backup.sh",
                                "autostart_script_name": "script_scheduler.desktop" }
            with open(self.config_file_name, 'w') as configfile:
                self.config.write(configfile)
        self.config.read(self.config_file_name)


    def read_config(self, name):
        return self.config.get(self.main_config_name, name)

    def write_config(self, name, value):
        self.config[self.main_config_name][name] = value
        with open(self.config_file_name, 'w') as configfile:
            self.config.write(configfile)

class AutostartHelper:
    configHelper = None
    current_project_path = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, configHelper):
        self.configHelper = configHelper
        if(not os.path.isfile(configHelper.read_config("autostart_script_name"))):
            autostart_file = open(configHelper.read_config("autostart_script_name"), "a")
            autostart_file.write("[Desktop Entry]" + "\n")
            autostart_file.write("Type=Application" + "\n")
            autostart_file.write("Name=Script Scheduler" + "\n")
            autostart_file.write("Exec=" + os.path.realpath(__file__) + "\n")
            autostart_file.write("Icon=" + self.current_project_path + '/' + self.configHelper.read_config("idle_icon_path") + "\n")
            autostart_file.write("Comment=Starts a script on a timely base" + "\n")
            autostart_file.write("X-GNOME-Autostart-enabled=true")

class LogfileHelper:
    configHelper = None

    def __init__(self, configHelper):
        self.configHelper = configHelper

    def getLogFile(self):       
        if(os.path.isfile(self.configHelper.read_config("scipt_scheduler_log_name"))):
            if(os.path.getsize(self.configHelper.read_config("scipt_scheduler_log_name")) > int(self.configHelper.read_config("max_log_size"))):
                if(os.path.isfile(self.configHelper.read_config("scipt_scheduler_old_log_name"))):
                   os.remove(self.configHelper.read_config("scipt_scheduler_old_log_name"))
                os.rename(self.configHelper.read_config("scipt_scheduler_log_name"), self.configHelper.read_config("scipt_scheduler_old_log_name"))

        return open(self.configHelper.read_config("scipt_scheduler_log_name"), "a")

    def write_tool_started(self):
        log_file = self.getLogFile()
        log_file.write("\n")
        log_file.write("*************************************************\n")
        log_file.write("Started Script Scheduler at " + datetime.now().strftime(self.configHelper.read_config("last_sync_time_format")) + "\n")
        log_file.write("*************************************************\n")
        log_file.write("\n")
        log_file.close()

    def write_tool_ended(self):        
        log_file = self.getLogFile()
        log_file.write("\n")
        log_file.write("*************************************************\n")
        log_file.write("Stopped Script Scheduler at " + datetime.now().strftime(self.configHelper.read_config("last_sync_time_format")) + "\n")
        log_file.write("*************************************************\n")
        log_file.write("\n")
        log_file.close()

class ScriptScheduler:
    stop_event = Event()
    start_at_system = None
    remove_start_at_system = None
    log_i = 0
    configHelper = None
    autostartHelper = None
    logfileHelper = None
    busy_icons_path = []
    current_project_path = os.path.dirname(os.path.abspath(__file__))
    killer = None

    def __init__(self):
        self.configHelper = ConfigHelper()
        self.autostartHelper = AutostartHelper(self.configHelper)
        self.logfileHelper = LogfileHelper(self.configHelper)
        self.busy_icons_path = [ self.current_project_path + '/' + self.configHelper.read_config("busy_icons_path"),
                                    self.current_project_path + '/' + self.configHelper.read_config("busy_icons_path2") ]

        self.app = self.configHelper.read_config("app_name")
        iconpath = self.current_project_path + '/' + self.configHelper.read_config("idle_icon_path")
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())

        self.indicator.set_label(self.configHelper.read_config("last_sync"), self.app)

        self.show_is_busy_thread = Thread(target=self.show_is_busy)
        self.script_scheduler_thread = Thread(target=self.run_script)

        self.run_script_hourly_thread = Thread(target=self.run_script_hourly)
        self.run_script_hourly_thread.setDaemon(True)
        self.run_script_hourly_thread.start()

        if(self.configHelper.read_config("autostart_enabled") == "True"):
            self.start_at_system_start(None)

        self.logfileHelper.write_tool_started()

    def create_menu(self):
        menu = Gtk.Menu()
        # menu item 1
        start_now = Gtk.MenuItem('Start script now')
        start_now.connect('activate', self.start_run_script)
        menu.append(start_now)
        # menu item 2
        show_log = Gtk.MenuItem('Show log file')
        show_log.connect('activate', self.show_log_file)
        menu.append(show_log)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)

        if(self.configHelper.read_config("autostart_enabled") != "True"):
            # menu item 1
            start_at_system = Gtk.MenuItem('Start Script Scheduler at system start')
            start_at_system.connect('activate', self.start_at_system_start)
            menu.append(start_at_system)
        else:
            # menu item 2
            remove_start_at_system = Gtk.MenuItem('Remove Script Scheduler at system start')
            remove_start_at_system.connect('activate', self.remove_start_at_system_start)
            menu.append(remove_start_at_system)

        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.call_stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def show_is_busy(self):
        t = 0
        while (not self.stop_event.is_set()):
            time.sleep(0.5)
            GObject.idle_add(
                self.indicator.set_icon,
                self.busy_icons_path[t % 2]
                )
            t += 1

    def show_is_idle(self):
        GObject.idle_add(
            self.indicator.set_icon,
            self.current_project_path + '/' + self.configHelper.read_config("idle_icon_path")
            )

    def show_is_error(self):
        GObject.idle_add(
            self.indicator.set_icon,
            self.current_project_path + '/' + self.configHelper.read_config("error_icon_path")
            )

    def show_last_sync(self):
        last_sync_text = self.configHelper.read_config("last_sync_text") + " " + datetime.now().strftime(self.configHelper.read_config("last_sync_time_format"))
        self.configHelper.write_config("last_sync", last_sync_text)
        GObject.idle_add(
                self.indicator.set_label,
                last_sync_text , self.app,
                priority=GObject.PRIORITY_DEFAULT
                )

    def start_at_system_start(self, source):
        log_file = self.logfileHelper.getLogFile()
        proc = subprocess.Popen(["sudo " + self.current_project_path + '/' + self.configHelper.read_config("shell_script_name") + " copy_autostart " + self.current_project_path + '/' + self.configHelper.read_config("autostart_script_name") + " " + self.configHelper.read_config("autostart_path") + '/' + self.configHelper.read_config("autostart_script_name")], shell=True, stderr=log_file, stdout=log_file)
        proc.wait()
        log_file.flush()
        log_file.close()
        self.configHelper.write_config("autostart_enabled", "True")
        GObject.idle_add(
                self.indicator.set_menu,
                self.create_menu()
                )


    def remove_start_at_system_start(self, source):   
        log_file = self.logfileHelper.getLogFile()
        proc = subprocess.Popen(["sudo " + self.current_project_path + '/' + self.configHelper.read_config("shell_script_name") + " remove_autostart " + self.configHelper.read_config("autostart_path") + '/' + self.configHelper.read_config("autostart_script_name")], shell=True, stderr=log_file, stdout=log_file)
        proc.wait()
        log_file.flush()
        log_file.close()
        self.configHelper.write_config("autostart_enabled", "False")
        GObject.idle_add(
                self.indicator.set_menu,
                self.create_menu()
                )

    def run_script_hourly(self):
        while 1:
            self.start_run_script(self)
            dt = datetime.now() + timedelta(minutes=int(self.configHelper.read_config("start_script_all_minutes")))
            #dt = dt.replace(second=10)
            while datetime.now() < dt:
                time.sleep(60)

    def run_script(self):
        log_file = self.logfileHelper.getLogFile()
        proc = subprocess.Popen(["sudo " + self.current_project_path + '/' + self.configHelper.read_config("shell_script_name") + " run_script"], shell=True, stderr=log_file, stdout=log_file)
        proc.wait()
        log_file.flush()
        log_file.close()
        self.stop_event.set()
        self.show_is_busy_thread.join()
        self.show_is_idle_thread = Thread(target=self.show_is_idle)
        self.show_is_idle_thread.setDaemon(True) 
        self.show_is_idle_thread.start()
        self.show_last_sync_thread = Thread(target=self.show_last_sync)
        self.show_last_sync_thread.setDaemon(True)
        self.show_last_sync_thread.start()

    def call_stop(self, source):
        self.stop()

    def stop(self):
        while(self.show_is_busy_thread.isAlive() or 
            self.script_scheduler_thread.isAlive()):
            time.sleep(1)
        self.logfileHelper.write_tool_ended()
        Gtk.main_quit()
        sys.exit(0)

    def start_run_script(self, source):    
        if(not self.show_is_busy_thread.isAlive() and 
            not self.script_scheduler_thread.isAlive()):
            self.stop_event.clear()
            self.show_is_busy_thread = Thread(target=self.show_is_busy)
            self.show_is_busy_thread.start()
            self.script_scheduler_thread = Thread(target=self.run_script)
            self.script_scheduler_thread.start()

    def show_log_file(self, source):
        webbrowser.open(self.configHelper.read_config("scipt_scheduler_log_name"))


scriptScheduler = ScriptScheduler()
InitSignal(scriptScheduler)

# this is where we call GObject.threads_init()
GObject.threads_init()
Gtk.main()
