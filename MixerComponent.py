# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/MixerComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip_longest
from _Framework.Control import control_list, ButtonControl
from _Framework.ChannelStripComponent import ChannelStripComponent as ChannelStripComponentBase
from _Framework.MixerComponent import MixerComponent as MixerComponentBase
from ableton.v2.base import listens, liveobj_valid
import Live

TRACK_ACTIVATORS = {}
ALL_TRACK_ACTIVATORS = False

class ChannelStripComponent(ChannelStripComponentBase):
    def __init__(self, *a, **k):
        super(ChannelStripComponent, self).__init__(*a, **k)
        self._crossfade_toggle_A = None
        self._crossfade_toggle_B = None
        self._track_activate_send_button = None

        def make_button_slot(name):
            return self.register_slot(None, getattr(self, '_%s_value' % name), 'value')

        self._crossfade_toggle_slot_A = make_button_slot('crossfade_toggle_A')
        self._crossfade_toggle_slot_B = make_button_slot('crossfade_toggle_B')
        self._track_activate_send_button_slot = make_button_slot('track_activate')

    def _track_activate_value(self, value):
        if self.is_enabled():
            if liveobj_valid(self._track):
                if value != 0:
                    if self.get_track_activate() == 1:
                        self.set_track_activate(0)
                    else:
                        self.set_track_activate(1)

                    self._on_track_activate_changed()

    def _crossfade_toggle_A_value(self, value):
        if self.is_enabled():
            if liveobj_valid(self._track):
                current = self._track.mixer_device.crossfade_assign
                if value != 0:
                    if current == 0:
                        self._track.mixer_device.crossfade_assign = 1
                    elif current == 1 or current == 2:
                        self._track.mixer_device.crossfade_assign = 0

    def _crossfade_toggle_B_value(self, value):
        if self.is_enabled():
            if liveobj_valid(self._track):
                current = self._track.mixer_device.crossfade_assign
                if value != 0:
                    if current == 2:
                        self._track.mixer_device.crossfade_assign = 1
                    elif current == 1 or current == 0:
                        self._track.mixer_device.crossfade_assign = 2

    def disconnect(self):
        super(ChannelStripComponent, self).disconnect()

        for button in [self._crossfade_toggle_A, self._crossfade_toggle_B, self._track_activate_send_button]:
            if button != None:
                button.reset()

        self._crossfade_toggle_A = None
        self._crossfade_toggle_B = None
        self._track_activate_send_button = None

    def set_track(self, track):
        super(ChannelStripComponent, self).set_track(track)

    def get_track_activate(self):
        if liveobj_valid(self._track):
            track_index = list(self.song().tracks).index(self._track)
            if track_index not in TRACK_ACTIVATORS:
                if ALL_TRACK_ACTIVATORS == True:
                    TRACK_ACTIVATORS[track_index] = 1
                else:
                    TRACK_ACTIVATORS[track_index] = 0

            return TRACK_ACTIVATORS[track_index]

    def set_track_activate(self, value):
        value = value or 0
        if liveobj_valid(self._track) and self._track in self.song().tracks:
            track_index = list(self.song().tracks).index(self._track)
            TRACK_ACTIVATORS[track_index] = value

    def set_crossfade_toggle_A(self, button):
        if button != self._crossfade_toggle_A:
            self.reset_button_on_exchange(self._crossfade_toggle_A)
            self._crossfade_toggle_A = button
            self._crossfade_toggle_slot_A.subject = button
            self.update()

    def set_crossfade_toggle_B(self, button):
        if button != self._crossfade_toggle_B:
            self.reset_button_on_exchange(self._crossfade_toggle_B)
            self._crossfade_toggle_B = button
            self._crossfade_toggle_slot_B.subject = button
            self.update()

    def set_track_activate_send(self, button):
        if button != self._track_activate_send_button:
            self.reset_button_on_exchange(self._track_activate_send_button)
            self._track_activate_send_button = button
            self._track_activate_send_button_slot.subject = button
            self.update()

    def update(self):
        super(ChannelStripComponent, self).update()

        if self.is_enabled():
            self._on_track_activate_changed()

    def _on_track_activate_changed(self):
        if self.is_enabled() and self._track_activate_send_button:
            if liveobj_valid(self._track):
                if self.get_track_activate() == 1:
                    self._track_activate_send_button.set_light(True)
                else:
                    self._track_activate_send_button.set_light(False)
            else:
                self._track_activate_send_button.set_light('Color.Off')
        return

    def _on_cf_assign_changed(self):
        if self.is_enabled() and self._crossfade_toggle_A and self._crossfade_toggle_B:
            if self._track:
                state = self._track.mixer_device.crossfade_assign
                if state == 0:
                    self._crossfade_toggle_A.set_light(True)
                    self._crossfade_toggle_B.set_light(False)
                elif state == 1:
                    self._crossfade_toggle_A.set_light(False)
                    self._crossfade_toggle_B.set_light(False)
                elif state == 2:
                    self._crossfade_toggle_A.set_light(False)
                    self._crossfade_toggle_B.set_light(True)
            else:
                self._crossfade_toggle_A.set_light('Color.Off')
                self._crossfade_toggle_B.set_light('Color.Off')
        return


class MixerComponent(MixerComponentBase):
    tracks_activate_send_button = ButtonControl()
    crossfader_control_light = ButtonControl()
    tempo_control_light = ButtonControl()
    prehear_volume_light = ButtonControl()
    master_volume_light = ButtonControl()

    @tracks_activate_send_button.pressed
    def tracks_activate_send_button(self, button):
        global ALL_TRACK_ACTIVATORS
        global TRACK_ACTIVATORS

        if ALL_TRACK_ACTIVATORS == True:
            ALL_TRACK_ACTIVATORS = False
            self.tracks_activate_send_button.color = "Color.TracksUnactivatedSend"

            for track_index in TRACK_ACTIVATORS:
                TRACK_ACTIVATORS[track_index] = 0

            for strip in self._channel_strips:
                strip._on_track_activate_changed()
        else:
            ALL_TRACK_ACTIVATORS = True
            self.tracks_activate_send_button.color = "Color.TracksActivatedSend"

            for track_index in TRACK_ACTIVATORS:
                TRACK_ACTIVATORS[track_index] = 1

            for strip in self._channel_strips:
                strip._on_track_activate_changed()

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)

    def _create_strip(self):
        return ChannelStripComponent()

    def set_track_select_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Color.TrackSelected', 'Color.TrackUnselected')
            strip.set_select_button(button)

    def set_solo_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Color.SoloOn', 'Color.SoloOff')
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Color.MuteOn', 'Color.MuteOff')
            strip.set_mute_button(button)

    def set_crossfader_buttons_A(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Color.CrossOn', 'Color.CrossOff')
            strip.set_crossfade_toggle_A(button)

    def set_crossfader_buttons_B(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Color.CrossOn', 'Color.CrossOff')
            strip.set_crossfade_toggle_B(button)

    def set_send_select_buttons(self, buttons):
        return True

    def set_master_select_button(self, button):
        return True

    def set_track_activate_send_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Color.TrackActivatedSend', 'Color.TrackUnactivatedSend')
            strip.set_track_activate_send(button)

    def set_tracks_activate_send_button(self, button):
        self.tracks_activate_send_button.set_control_element(None)
        global ALL_TRACK_ACTIVATORS

        if button:
            self.tracks_activate_send_button.set_control_element(button)
            if ALL_TRACK_ACTIVATORS == False:
                self.tracks_activate_send_button.color = "Color.TracksUnactivatedSend"
            else:
                self.tracks_activate_send_button.color = "Color.TracksActivatedSend"
            self.tracks_activate_send_button.enabled = True

    def set_switch_sends_button(self, button):
        return

    def set_send_mute_buttons(self, buttons):
        return True

    def set_send_controls(self, controls):
        return

    def set_send_controls_lights(self, controls):
        #return_tracks = self.song().return_tracks
        #for control, track in izip_longest(controls, return_tracks or []):
        return

    def set_send_volumes(self, controls):
        return True

    def set_send_volumes_lights(self, controls):
        return True

    def set_crossfader_control_light(self, button):
        if button:
            self.crossfader_control_light.set_control_element(button)
            self.crossfader_control_light.color = "Color.CrossControl"
            self.crossfader_control_light.enabled = True

    def set_tempo_control_light(self, button):
        if button:
            self.tempo_control_light.set_control_element(button)
            self.tempo_control_light.color = "Color.TempoControl"
            self.tempo_control_light.enabled = True

    def set_prehear_volume_light(self, button):
        if button:
            self.prehear_volume_light.set_control_element(button)
            self.prehear_volume_light.color = "Color.PrehearVolume"
            self.prehear_volume_light.enabled = True

    def set_master_volume_light(self, button):
        if button:
            self.master_volume_light.set_control_element(button)
            self.master_volume_light.color = "Color.MasterVolume"
            self.master_volume_light.enabled = True
