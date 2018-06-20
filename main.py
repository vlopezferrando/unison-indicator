#!/usr/bin/python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
import subprocess

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject, GLib


UNISON_PROFILE = 'victor'


class Indicator(object):
    SYNC_COMMAND = ['unison', UNISON_PROFILE, '-ui', 'text', '-repeat', 'watch', '-batch']
    SYNC_COMMAND = ['counter']
    GUI_COMMAND = "unison-gtk"

    ICON_GOOD  = "icons/color.svg"
    ICON_WAIT  = "icons/gray.svg"
    ICON_SYNC  = "icons/sync.svg"
    ICON_ERROR = "icons/error.svg"

    def __init__(self):
        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            'unison-indicator',
            os.path.abspath(self.ICON_WAIT),
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())

        self.sync_icon = 1

        # Launch unison in the background
        #self.run_unison()

        self.is_syncing = True
        self.start_syncing()

        # Gtk event loop
        Gtk.main()

    def build_menu(self):
        """Build indicator menu"""
        menu = Gtk.Menu()

        # Open root directory
        item_open_root = Gtk.MenuItem('Open Unison root folder')
        item_open_root.connect('activate', self.open_root)
        menu.append(item_open_root)

        # Launch GUI
        item_launch_gui = Gtk.MenuItem('Launch Unison GUI')
        item_launch_gui.connect('activate', self.launch_gui)
        menu.append(item_launch_gui)

        # Recently changed files
        menu_file_list = Gtk.Menu()
        menu_file_list.append(Gtk.MenuItem('--'))
        item_file_list = Gtk.MenuItem('Recently changed files')
        item_file_list.set_submenu(menu_file_list)
        menu.append(item_file_list)

        menu.append(Gtk.SeparatorMenuItem())

        # Stop / Start
        item_stop_start = Gtk.MenuItem('Pause syncing')
        item_stop_start.connect('activate', self.stop_start)
        menu.append(item_stop_start)

        menu.append(Gtk.SeparatorMenuItem())

        # Quit
        item_quit = Gtk.MenuItem('Stop Unison')
        item_quit.connect('activate', quit)
        menu.append(item_quit)

        menu.append(Gtk.SeparatorMenuItem())

        # Show menu
        menu.show_all()
        return menu

    def run_unison(self):
        self.pid, _, idout, iderr = GLib.spawn_async(
            self.SYNC_COMMAND,
            flags=GLib.SPAWN_DO_NOT_REAP_CHILD | GLib.SPAWN_SEARCH_PATH,
            standard_output=True,
            standard_error=True)

        fout = os.fdopen(idout, 'r')
        ferr = os.fdopen(iderr, 'r')

        GLib.child_watch_add(self.pid, self._on_done)
        GLib.io_add_watch(fout, GLib.IO_IN, self._on_stdout)
        GLib.io_add_watch(ferr, GLib.IO_IN, self._on_stderr)
        
        return self.pid

    # Parse Unison output

    def _on_stdout(self, fobj, cond):
        print("stdout", fobj.readline(), end='')
        return True

    def _on_stderr(self, fobj, cond):
        print("stderr", fobj.readline(), end='')
        return True

    def start_syncing(self):
        if not self.is_syncing:
            GLib.idle_add(
                self.indicator.set_icon,
                os.path.abspath(self.ICON_GOOD))
            return

        self.sync_icon = 2 if self.sync_icon == 1 else 1
        GLib.idle_add(
            self.indicator.set_icon,
            os.path.abspath(self.ICON_SYNC.replace('sync', 'sync%d' % self.sync_icon)))
        GLib.timeout_add_seconds(1, self.start_syncing)

    def done_syncing(self):
        self.is_syncing = False


    # Stop / start Unison

    def _on_done(self, pid, retval, *argv):
        print('Process done')

    def stop_start(self):
        print('Stop-start')

    # Open root folder

    def open_root(self, item):
        subprocess.run('xdg-open ', shell=True, check=True)


    # Launch GUI

    def launch_gui(self, item):
        """Launch Unison GUI. Useful to resolve conflicts or edit profile"""
        subprocess.run(self.GUI_COMMAND, shell=True, check=True)

    # Quit

    def quit(self):
        Gtk.main_quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Indicator()