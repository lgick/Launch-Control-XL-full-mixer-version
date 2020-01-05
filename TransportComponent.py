# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/MixerComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip_longest
from _Framework.Control import control_list, ButtonControl
from _Framework.TransportComponent import TransportComponent as TransportComponentBase

import functools, logging, traceback
logger = logging.getLogger(__name__)
#logger.error('#### !!!!!!!!!!! #########')

class TransportComponent(TransportComponentBase):
    delete_clip_button = ButtonControl()
    stop_clip_button = ButtonControl()
    play_clip_button = ButtonControl()
    arm_button = ButtonControl()

    @delete_clip_button.pressed
    def delete_clip_button(self, button):
        clip = self.song().view.detail_clip

        if clip:
            self.song().view.selected_track.delete_clip(clip)
            self.update_colors()

    @stop_clip_button.pressed
    def stop_clip_button(self, button):
        tracks = self.song().tracks
        track = self.song().view.selected_track

        if track in tracks:
            self.song().view.selected_track.stop_all_clips(False)
            self.update_colors()

    @play_clip_button.pressed
    def play_clip_button(self, button):
        tracks = self.song().tracks
        track = self.song().view.selected_track
        clip = self.song().view.detail_clip
        current_slot = self.song().view.highlighted_clip_slot

        if track in tracks and current_slot:
            if not clip:
                self.song().view.selected_track.arm = True
            current_slot.fire()
            self.update_colors()

    @arm_button.pressed
    def arm_button(self, button):
        tracks = self.song().tracks
        track = self.song().view.selected_track

        if track in tracks:
            track.arm = not track.arm
            self.update_colors()

    def on_selected_track_changed(self):
        self.update_colors()

    def update_colors(self):
        track = self.song().view.selected_track
        tracks = self.song().tracks

        if track in tracks:
            self.delete_clip_button.color = 'Color.ClipDelete'
            self.stop_clip_button.color = 'Color.ClipStop'
            self.play_clip_button.color = 'Color.ClipPlay'

            if track.arm == True:
                self.arm_button.color = 'Color.RecOn'
            else:
                self.arm_button.color = 'Color.RecOff'
        else:
            self.arm_button.color = 'Color.Off'
            self.delete_clip_button.color = 'Color.Off'
            self.stop_clip_button.color = 'Color.Off'
            self.play_clip_button.color = 'Color.Off'

    def clear_buttons(self):
        self.delete_clip_button.color = 'Color.Off'
        self.delete_clip_button.set_control_element(None)
        self.stop_clip_button.color = 'Color.Off'
        self.stop_clip_button.set_control_element(None)
        self.play_clip_button.color = 'Color.Off'
        self.play_clip_button.set_control_element(None)
        self.arm_button.color = 'Color.Off'
        self.arm_button.set_control_element(None)

    def set_metronome_button(self, button):
        if self._metronome_toggle._on_button_value.subject:
            self._metronome_toggle._on_button_value.subject.reset()

        if button:
            button.set_on_off_values('Color.MetronomeOn', 'Color.MetronomeOff')
        self._metronome_toggle.set_toggle_button(button)

    def set_overdub_button(self, button):
        if self._overdub_toggle._on_button_value.subject:
            self._overdub_toggle._on_button_value.subject.reset()

        if button:
            button.set_on_off_values('Color.RecOn', 'Color.RecOff')
        self._overdub_toggle.set_toggle_button(button)

    def set_delete_clip_button(self, button):
        if button:
            self.delete_clip_button.set_control_element(button)
            self.update_colors()

    def set_arm_button(self, button):
        if button:
            self.arm_button.set_control_element(button)
            self.update_colors()

    def set_stop_clip_button(self, button):
        if button:
            self.stop_clip_button.set_control_element(button)
            self.update_colors()

    def set_play_clip_button(self, button):
        if button:
            self.play_clip_button.set_control_element(button)
            self.update_colors()
