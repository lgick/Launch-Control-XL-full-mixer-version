# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/MixerComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip_longest
from ableton.v2.base import listens, liveobj_valid
from _Framework.Control import control_list, ButtonControl, EncoderControl
from _Framework.ChannelStripComponent import ChannelStripComponent as ChannelStripComponentBase
from _Framework.MixerComponent import MixerComponent as MixerComponentBase
import Live

import functools, logging, traceback
logger = logging.getLogger(__name__)
#logger.error('#### !!!!!!!!!!! #########')

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
    master_select_button = ButtonControl()
    tracks_activate_send_button = ButtonControl()
    crossfader_control_light = ButtonControl()
    tempo_control_light = ButtonControl()
    prehear_volume_light = ButtonControl()
    master_volume_light = ButtonControl()
    switch_sends = 'A'
    switch_sends_button = ButtonControl()
    send_buttons_mode = 'select'
    send_buttons = control_list(ButtonControl, control_count=6)
    send_volumes_lights = control_list(ButtonControl, control_count=6)
    send_controls_lights = control_list(ButtonControl, control_count=6)

    def __init__(self, send_volumes=None, send_controls=None, *a, **k):
        self.send_volumes = send_volumes
        self.send_controls = send_controls
        super(MixerComponent, self).__init__(*a, **k)

    def _create_strip(self):
        return ChannelStripComponent()

    def clear_buttons(self):
        for button in self.send_buttons:
            button.color = 'Color.Off'
            button.set_control_element(None)

        self.switch_sends_button.color = 'Color.Off'
        self.switch_sends_button.set_control_element(None)
        self.master_select_button.color = 'Color.Off'
        self.master_select_button.set_control_element(None)
        self.tracks_activate_send_button.color = 'Color.Off'
        self.tracks_activate_send_button.set_control_element(None)

    @send_buttons.pressed
    def send_buttons(self, button):
        if self.switch_sends == 'A':
            index = button.index
        elif self.switch_sends == 'B':
            index = 6 + button.index

        if index < len(self.song().return_tracks):
            if self.send_buttons_mode == 'select':
                self.song().view.selected_track = self.song().return_tracks[index]
            elif self.send_buttons_mode == 'mute':
                self.song().return_tracks[index].mute = not self.song().return_tracks[index].mute

            self.on_return_tracks_changed()

    @switch_sends_button.pressed
    def switch_sends_button(self, button):
        length = len(self.song().return_tracks)

        if length > 6:
            if self.switch_sends == 'A':
                self.switch_sends = 'B'
            elif self.switch_sends == 'B':
                self.switch_sends = 'A'

            self.on_return_tracks_changed()

    @master_select_button.pressed
    def master_select_button(self, button):
        if self.song().view.selected_track != self.song().master_track:
            self.song().view.selected_track = self.song().master_track

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

    def on_selected_track_changed(self):
        MixerComponentBase.on_selected_track_changed(self)
        self.on_master_selected_track_changed()
        self.on_return_tracks_changed()
        return

    def on_master_selected_track_changed(self):
        if self.song().view.selected_track != self.song().master_track:
            self.master_select_button.color = 'Color.MasterUnselected'
        else:
            self.master_select_button.color = 'Color.MasterSelected'

    def on_track_list_changed(self):
        MixerComponentBase.on_track_list_changed(self)
        self.on_return_tracks_changed()
        return

    def on_return_tracks_changed(self):
        length = len(self.song().return_tracks)
        return_tracks = self.song().return_tracks

        if length > 6:
            if self.switch_sends == 'A':
                side_len = 6
                i_plus = 0
                send_color = 'Color.SendsA'
                volume_color = 'Color.VolumeSendsA'
            elif self.switch_sends == 'B':
                side_len = length - 6
                i_plus = 6
                send_color = 'Color.SendsB'
                volume_color = 'Color.VolumeSendsB'

            self.switch_sends_button.color = send_color

            for i in xrange(6):
                if i < side_len:
                    self.send_controls_lights[i].color = send_color
                    self.send_volumes_lights[i].color = volume_color
                    self.set_send_button_light(return_tracks[i + i_plus], i)
                    self.send_volumes[i].connect_to(return_tracks[i + i_plus].mixer_device.volume)
                else:
                    self.send_volumes_lights[i].color = 'Color.Off'
                    self.send_controls_lights[i].color = 'Color.Off'
                    self.send_buttons[i].color = 'Color.Off'
                    self.send_volumes[i].release_parameter()
        else:
            self.switch_sends = 'A'
            self.switch_sends_button.color = 'Color.Off'

            for i in xrange(6):
                if i < length:
                    self.send_controls_lights[i].color = 'Color.SendsA'
                    self.send_volumes_lights[i].color = 'Color.VolumeSendsA'
                    self.set_send_button_light(return_tracks[i], i)
                    self.send_volumes[i].connect_to(return_tracks[i].mixer_device.volume)
                else:
                    self.send_volumes_lights[i].color = 'Color.Off'
                    self.send_controls_lights[i].color = 'Color.Off'
                    self.send_buttons[i].color = 'Color.Off'
                    self.send_volumes[i].release_parameter()

    def set_send_button_light(self, track, index):
        if self.send_buttons_mode == 'select':
            if self.song().view.selected_track == track:
                self.send_buttons[index].color = 'Color.TrackSelected'
            else:
                self.send_buttons[index].color = 'Color.TrackUnselected'

        elif self.send_buttons_mode == 'mute':
            if track.mute:
                self.send_buttons[index].color = 'Color.SendMuteOn'
            else:
                self.send_buttons[index].color = 'Color.SendMuteOff'















    def set_send_controls(self, controls):
        #self.send_controls.set_control_element(controls)

        #[]for strip, control in izip_longest(self._channel_strips, controls or []):


        #[]num_sends = self._mixer.num_sends
        #[]for index in xrange(6):
        #[]    self._encoder_modes.set_mode_enabled('send_%d_mode' % (index,), True if index < num_sends else False)
        #return True

        #controls[0].connect_to(self.song().tracks[0].mixer_device.sends[0])
        #controls[1].connect_to(self.song().tracks[1].mixer_device.sends[0])
        return


        #self._send_index = 0
#       # self._send_controls = controls


        self._send_index = 0
        for strip, control in izip_longest(self._channel_strips, controls or []):
            if self._send_index is None:
                strip.set_send_controls(None)
            else:
                strip.set_send_controls((None, ) * self._send_index + (control,))
        return
























    def set_send_select_buttons(self, buttons):
        self.send_buttons_mode = 'select'
        self.send_buttons.set_control_element(buttons)
        self.on_return_tracks_changed()

    def set_send_mute_buttons(self, buttons):
        self.send_buttons_mode = 'mute'
        self.send_buttons.set_control_element(buttons)
        self.on_return_tracks_changed()

    def set_switch_sends_button(self, button):
        self.switch_sends_button.set_control_element(button)
        self.on_return_tracks_changed()

    def set_send_controls_lights(self, controls):
        self.send_controls_lights.set_control_element(controls)
        self.on_return_tracks_changed()

    def set_send_volumes_lights(self, controls):
        self.send_volumes_lights.set_control_element(controls)
        self.on_return_tracks_changed()

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

    def set_master_select_button(self, button):
        if button:
            self.master_select_button.set_control_element(button)
            self.on_master_selected_track_changed();

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
