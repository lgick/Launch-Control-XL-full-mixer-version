# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/MixerComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip_longest
from _Framework.Control import control_list, ButtonControl
from _Framework.SessionComponent import SessionComponent as SessionComponentBase
from _Framework.ScrollComponent import ScrollComponent

import functools, logging, traceback
logger = logging.getLogger(__name__)
#logger.error('#### !!!!!!!!!!! #########')

class SessionComponent(SessionComponentBase):

    def __init__(self, *a, **k):
        super(SessionComponent, self).__init__(*a, **k)

        self._clip_vertical_button, self._clip_horisontal_button = self.register_components(ScrollComponent(), ScrollComponent())
        self._clip_vertical_button.scroll_up_button.color = 'Color.NavButtonOn'
        self._clip_vertical_button.scroll_down_button.color = 'Color.NavButtonOn'
        self._clip_vertical_button.scroll_up_button.pressed_color = 'Color.NavButtonOn'
        self._clip_vertical_button.scroll_down_button.pressed_color = 'Color.NavButtonOn'
        self._clip_horisontal_button.scroll_up_button.color = 'Color.NavButtonOn'
        self._clip_horisontal_button.scroll_down_button.color = 'Color.NavButtonOn'
        self._clip_horisontal_button.scroll_up_button.pressed_color = 'Color.NavButtonOn'
        self._clip_horisontal_button.scroll_down_button.pressed_color = 'Color.NavButtonOn'

        def can_clip():
            return True

        self._clip_vertical_button.can_scroll_up = can_clip
        self._clip_vertical_button.can_scroll_down = can_clip
        self._clip_vertical_button.scroll_up = self.clip_up
        self._clip_vertical_button.scroll_down = self.clip_down

        self._clip_horisontal_button.can_scroll_up = can_clip
        self._clip_horisontal_button.can_scroll_down = can_clip
        self._clip_horisontal_button.scroll_up = self.clip_left
        self._clip_horisontal_button.scroll_down = self.clip_right

    def clip_up(self):
        selected_track = self.song().view.selected_track
        selected_scene = self.song().view.selected_scene
        tracks = self.song().tracks
        scenes = self.song().scenes

        if selected_track not in tracks:
            self.song().view.selected_track = tracks[self.track_offset()]
            self.song().view.selected_scene = scenes[0]
        else:
            if selected_scene != scenes[0]:
                index = list(scenes).index(selected_scene)
                self.song().view.selected_scene = scenes[(index - 1)]
            else:
                self.song().view.selected_scene = scenes[(-1)]

    def clip_down(self):
        selected_track = self.song().view.selected_track
        selected_scene = self.song().view.selected_scene
        tracks = self.song().tracks
        scenes = self.song().scenes

        if selected_track not in tracks:
            self.song().view.selected_track = tracks[self.track_offset()]
            self.song().view.selected_scene = scenes[0]
        else:
            if selected_scene != scenes[(-1)]:
                index = list(scenes).index(selected_scene)
                self.song().view.selected_scene = scenes[(index + 1)]
            else:
                self.song().view.selected_scene = scenes[0]

    def clip_left(self):
        selected_track = self.song().view.selected_track
        tracks = self.song().tracks

        if selected_track in tracks:
            index = list(tracks).index(selected_track) - 1
        else:
            index = self.track_offset()

        if index < 0:
            index = len(tracks) - 1

        for track in tracks:
            track.arm = False

        self.song().view.selected_track = tracks[index]
        self.song().view.selected_track.arm = True

    def clip_right(self):
        selected_track = self.song().view.selected_track
        tracks = self.song().tracks

        if selected_track in tracks:
            index = list(tracks).index(selected_track) + 1
        else:
            index = self.track_offset()

        if index == len(tracks):
            index = 0

        for track in tracks:
            track.arm = False

        self.song().view.selected_track = tracks[index]
        self.song().view.selected_track.arm = True

    def clear_buttons(self):
        return

    def set_clip_left_button(self, button):
        self._clip_horisontal_button.set_scroll_up_button(button)

    def set_clip_right_button(self, button):
        self._clip_horisontal_button.set_scroll_down_button(button)

    def set_clip_up_button(self, button):
        self._clip_vertical_button.set_scroll_up_button(button)

    def set_clip_down_button(self, button):
        self._clip_vertical_button.set_scroll_down_button(button)

    def set_page_left_button(self, button):
        if button:
            button.set_on_off_values('Color.NavButtonOn', 'Color.NavButtonOff')

        self._page_left_button = button
        self._horizontal_paginator.set_scroll_up_button(button)

    def set_page_right_button(self, button):
        if button:
            button.set_on_off_values('Color.NavButtonOn', 'Color.NavButtonOff')

        self._page_right_button = button
        self._horizontal_paginator.set_scroll_down_button(button)

    def set_track_bank_left_button(self, button):
        if button:
            button.set_on_off_values('Color.NavButtonOn', 'Color.NavButtonOff')

        self._bank_left_button = button
        self._horizontal_banking.set_scroll_up_button(button)

    def set_track_bank_right_button(self, button):
        if button:
            button.set_on_off_values('Color.NavButtonOn', 'Color.NavButtonOff')

        self._bank_right_button = button
        self._horizontal_banking.set_scroll_down_button(button)
