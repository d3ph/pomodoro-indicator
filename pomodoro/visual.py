#!/usr/bin/env python
#-*- coding:utf-8 -*-

#
# Copyright 2011 malev.com.ar
#
# Author: Marcos Vanetta <marcosvanetta@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of either or both of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the
# Free Software Foundation; and/or
# 2) the GNU Lesser General Public License version 2.1, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the applicable version of the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of both the GNU Lesser General Public
# License version 3 and version 2.1 along with this program.  If not, see
# <http://www.gnu.org/licenses/>

import gobject
import gtk
import appindicator
import pynotify
import sys
import pomodoro_state
import gettext
import pygame
import os

from gettext import gettext as _
from configuration import Configuration

PROJECTNAME = 'pomodoro-indicator'
gettext.bindtextdomain(PROJECTNAME)
gettext.textdomain(PROJECTNAME)

"""
Pomodoro's indicator
"""
# ICONS
# http://www.softicons.com/free-icons/food-drinks-icons/veggies-icons-by-icon-icon/tomato-icon


class PomodoroNotificator:
    def notify_change(self):
        pass

    def notify_start(self):
        pass


class PomodoroSoundNotificator(PomodoroNotificator):
    def __init__(self, configuration):
        self.configuration = configuration
        pygame.init()

    def notify_change(self, status):
        if status == pomodoro_state.WORKING_STATE:
            self.break_soung()
        elif status == pomodoro_state.RESTING_STATE:
            self.ring_sound()

    def notify_start(self):
        self.tictac_sound()

    def break_soung(self):
        pygame.mixer.music.load(self.configuration['break_sound'])
        pygame.mixer.music.play()

    def ring_sound(self):
        pygame.mixer.music.load(self.configuration['ring_sound'])
        pygame.mixer.music.play()

    def tictac_sound(self):
        pygame.mixer.music.load(self.configuration['ticking_sound'])
        pygame.mixer.music.play()


class PomodoroOSDNotificator(PomodoroNotificator):
    def __init__(self, configuration):
        self.icon_directory = configuration.icon_directory()

    def notify_change(self, state):
        pynotify.init("pomodoro-indicator")
        message = self.generate_message(state)
        if message:
            osd_box = pynotify.Notification(
                    _("Pomodoro"),
                    message,
                    self.big_icon()
                    )
            osd_box.show()
        else:
            osd_box = pynotify.Notification(
                    _("Pomodoro"),
                    "Unknown message for state '%s'" % state,
                    self.big_icon()
                    )
            osd_box.show()

    def notify_start(self):
        pynotify.init("pomodoro-indicator")
        osd_box = pynotify.Notification(
                _("Pomodoro"),
                "Ready, set, GO!",
                self.big_icon()
                )
        osd_box.show()

    def big_icon(self):
        return os.path.join(self.icon_directory, "tomato_32.png")

    def generate_message(self, status):
        message = None
        if status == pomodoro_state.WORKING_STATE:
            message = _("You should start working")
        elif status == pomodoro_state.WAITING_STATE:
            message = _("Now you can start working.")
        elif status == pomodoro_state.RESTING_STATE:
            message = _("You can take a break now.")
        return message


class PomodoroFiller:
    def __init__(self, pomodoro):
        self.pomodoro = pomodoro

    def update_icon(self):
        if self.pomodoro.is_working():
            rest = int(self.pomodoro.working_percentage() * 0.12)
            return "pomodoro_%i.png" % rest
        return "tomato_grey.png"


class PomodoroIndicator:
    status_labels = {pomodoro_state.WAITING_STATE: _('Waiting'),
                     pomodoro_state.WORKING_STATE: _('Working'),
                     pomodoro_state.RESTING_STATE: _('Resting'),
                     pomodoro_state.PAUSED_STATE: _('Paused')}

    def __init__(self):
        self.configuration = Configuration()
        self.pomodoro = pomodoro_state.PomodoroMachine(self.configuration)
        self.pomodoro_filler = PomodoroFiller(self.pomodoro)
        self.icon_directory = self.configuration.icon_directory()
        self.listeners = [PomodoroOSDNotificator(self.configuration),
                          PomodoroSoundNotificator(self.configuration)]

        self.ind = appindicator.Indicator("pomodoro-indicator",
                                           self.idle_icon(),
                                           appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon(self.active_icon())

        self.menu_setup()
        self.ind.set_menu(self.menu)
        self.ind.set_label("00:00")
        self.timer_id = None

    def idle_icon(self):
        return os.path.join(self.icon_directory, "tomato_grey.png")

    def active_icon(self):
        return os.path.join(self.icon_directory, "tomato_24.png")

    def menu_setup(self):
        self.menu = gtk.Menu()
        self.separator1 = gtk.SeparatorMenuItem()
        self.separator2 = gtk.SeparatorMenuItem()
        self.current_state_item = gtk.MenuItem(_("Waiting"))
        self.timer_item = gtk.MenuItem("00:00")

        # Drawing buttons
        self.start_item = gtk.MenuItem(_("Start"))
        self.pause_item = gtk.MenuItem(_("Pause"))
        self.resume_item = gtk.MenuItem(_("Resume"))
        self.stop_item = gtk.MenuItem(_("Stop"))
        self.quit_item = gtk.MenuItem(_("Quit"))

        if self.configuration['can_pause']:
            self.state_visible_menu_items = {
                pomodoro_state.WAITING_STATE: [self.start_item],
                pomodoro_state.WORKING_STATE: [self.pause_item, self.stop_item],
                pomodoro_state.RESTING_STATE: [],
                pomodoro_state.PAUSED_STATE: [self.resume_item, self.stop_item]
            }
        else:
            self.state_visible_menu_items = {
                pomodoro_state.WAITING_STATE: [self.start_item],
                pomodoro_state.WORKING_STATE: [self.stop_item],
                pomodoro_state.RESTING_STATE: [],
                pomodoro_state.PAUSED_STATE: [self.stop_item]
            }

        self.available_states = pomodoro_state.AVAILABLE_STATES

        self.hidable_menu_items = [self.start_item, self.pause_item,
                                   self.resume_item, self.stop_item]
        self.start_item.connect("activate", self.start)
        self.pause_item.connect("activate", self.pause)
        self.resume_item.connect("activate", self.resume)
        self.stop_item.connect("activate", self.stop)
        self.quit_item.connect("activate", self.quit)

        self.menu_items = [
            self.current_state_item,
            self.timer_item,
            self.separator1,
            self.start_item,
            self.pause_item,
            self.resume_item,
            self.stop_item,
            self.separator2,
            self.quit_item
        ]

        for item in self.menu_items:
            item.show()
            self.menu.append(item)
        self.redraw_menu()

    def button_pushed(self, widget, data=None):
        method = getattr(self, data.get_child().get_text().lower())
        method()

    def hide_hidable_menu_items(self):
        for item in self.hidable_menu_items:
            item.hide()

    def redraw_menu(self):
        self.hide_hidable_menu_items()
        self.change_status_menu_item_label()
        for state, items in self.state_visible_menu_items.iteritems():
            if self.current_state() == state:
                for item in items:
                    item.show()

    def change_status_menu_item_label(self):
        label = self.current_state_item.child
        label.set_text(self.status_labels[self.pomodoro.current_state()])

    def change_timer_menu_item_label(self, next_label):
        label = self.timer_item.child
        label.set_text(next_label)
        self.ind.set_label(next_label)

    def generate_notification(self):
        if self.configuration['continue_working_after_rest'] and self.current_state() == pomodoro_state.WORKING_STATE:
            self.ind.set_status(appindicator.STATUS_ACTIVE)
        elif not self.configuration['continue_working_after_rest'] and self.current_state() == pomodoro_state.WAITING_STATE:
            self.ind.set_status(appindicator.STATUS_ACTIVE)
        elif self.current_state() == pomodoro_state.RESTING_STATE:
            self.ind.set_status(appindicator.STATUS_ATTENTION)
        [listener.notify_change(self.current_state()) for listener in self.listeners]

    # Methods that interacts with the PomodoroState collaborator.
    def start_timer(self):
        self.timer_id = gobject.timeout_add(1000, self.update_timer)

    def update_timer(self):
        self.start_timer()
        changed = self.pomodoro.next_second()
        self.change_timer_menu_item_label(self.pomodoro.elapsed_time())
        if changed:
            if self.pomodoro.is_waiting():
                self.stop_timer()
                self.ind.set_status(appindicator.STATUS_ACTIVE)
                self.ind.set_icon(os.path.join(self.icon_directory, self.pomodoro_filler.update_icon()))
            self.generate_notification()
            self.redraw_menu()
        elif self.pomodoro.is_working():
            self.ind.set_icon(os.path.join(self.icon_directory, self.pomodoro_filler.update_icon()))

    def current_state(self):
        for state in self.available_states:
            if self.pomodoro.in_this_state(state):
                return state

    def start(self, widget, data=None):
        [listener.notify_start() for listener in self.listeners]
        self.start_timer()
        self.pomodoro.start()
        self.redraw_menu()

    def pause(self, widget, data=None):
        self.stop_timer()
        self.pomodoro.pause()
        self.redraw_menu()

    def resume(self, widget, data=None):
        [listener.notify_start() for listener in self.listeners]
        self.start_timer()
        self.pomodoro.resume()
        self.redraw_menu()

    def stop(self, widget, data=None):
        self.stop_timer()
        self.pomodoro.stop()
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_icon(os.path.join(self.icon_directory, self.pomodoro_filler.update_icon()))
        self.change_timer_menu_item_label(self.pomodoro.elapsed_time())
        self.redraw_menu()

    def stop_timer(self):
        if self.timer_id != None:
            gobject.source_remove(self.timer_id)
        self.timer_id = None

    def main(self):
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

if __name__ == "__main__":
    print __doc__
