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
    SYNC_COMMAND = ['unison', UNISON_PROFILE,
                    '-ui', 'text',
                    '-repeat', 'watch',
                    '-batch']
    SYNC_COMMAND = ['counter']
    GUI_COMMAND = "unison-gtk"

    ICON_GOOD  = "icons/color.svg"
    ICON_WAIT  = "icons/gray.svg"
    ICON_SYNC  = "icons/sync.svg"
    ICON_ERROR = "icons/error.svg"

    RE_IDLE     = 'Nothing to do: replicas have not changed since last sync.'
    RE_START    = r'started propagating.* (\d+[^)]*)'
    RE_COMPLETE = r'Synchronization complete.* \((\d+[^)]*)\)'
    RE_COPIED   = r'\[END\]\s+Copying\s+(.*/)*([^/]+)'
    RE_DELETED  = r'\[END\]\s+Deleting\s+(.*/)*([^/]+)'
    RE_UPDATING = r'\[END\]\s+Updating file\s+(.*/)*([^/]+)'

    def __init__(self):
        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            'unison-indicator',
            os.path.abspath(self.ICON_WAIT),
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())

        # Unison is not paused at the beggining
        self.paused = False

        # Launch unison in the background
        self.unison_pid = self.start_unison()

        # Gtk event loop
        Gtk.main()

    def set_icon(self, icon):
        GLib.idle_add(self.indicator.set_icon, os.path.abspath(icon))

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

        # Pause Unison
        self.item_pause_resume = Gtk.MenuItem('Pause Unison')
        self.item_pause_resume.connect('activate', self.pause_resume_unison)
        menu.append(self.item_pause_resume)

        menu.append(Gtk.SeparatorMenuItem())

        # Quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.append(Gtk.SeparatorMenuItem())

        # Show menu
        menu.show_all()
        return menu

    # Start unison

    def start_unison(self):
        pid, _, idout, iderr = GLib.spawn_async(
            self.SYNC_COMMAND,
            flags=GLib.SPAWN_DO_NOT_REAP_CHILD
                | GLib.SPAWN_SEARCH_PATH,
            standard_output=None,
            standard_error=True)

        ferr = os.fdopen(iderr, 'r')

        GLib.child_watch_add(pid, self._on_done)
        GLib.io_add_watch(ferr, GLib.IO_IN, self._on_stderr)

        return pid

    # Stop Unison

    def stop_unison(self):
        os.kill(self.unison_pid, signal.SIGTERM)

    # Pause / Resume Unison

    def pause_resume_unison(self, item):
        os.kill(self.unison_pid,
                signal.SIGCONT if self.paused else signal.SIGTSTP)
        self.paused = not self.paused
        GLib.idle_add(self.set_start_unison_label)

    def set_start_unison_label(self):
        self.item_pause_resume.get_child().set_text(
            '%s Unison' % 'Resume' if self.paused else 'Pause')

    # Parse Unison output

    def _on_stderr(self, fobj, cond):
        print("stderr", fobj.readline(), end='')
        return True

    def _on_done(self, pid, retval, *argv):
        print('Process done')

    # Animated syncing icon

    def start_syncing_icon(self):
        self.sync_icon = True
        self.is_syncing = True
        self.flip_syncing_icon()

    def stop_syncing_icon(self):
        self.is_syncing = False

    def flip_syncing_icon(self):
        if self.is_syncing:
            self.sync_icon = not self.sync_icon
            self.set_icon(self.ICON_SYNC.replace(
                'sync', 'sync%d' % 1 + self.sync_icon))
            GLib.timeout_add_seconds(1, self.flip_syncing_icon)

    # Open root folder

    def open_root(self, item):
        # TODO: get unison root
        subprocess.call('xdg-open .', shell=True)

    # Launch GUI

    def launch_gui(self, item):
        """Launch Unison GUI. Useful to resolve conflicts or edit profile"""
        subprocess.run(self.GUI_COMMAND, shell=True, check=True)

    # Quit

    def quit(self, item):
        self.stop_unison()
        Gtk.main_quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Indicator()
