# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/MixerComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip_longest
from ableton.v2.base import listens, liveobj_valid
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Control import control_list, ButtonControl, EncoderControl
from _Framework.ChannelStripComponent import ChannelStripComponent as ChannelStripComponentBase
from _Framework.MixerComponent import MixerComponent as MixerComponentBase
import Live

import functools, logging, traceback
logger = logging.getLogger(__name__)
#logger.error('#### !!!!!!!!!!! #########')

class ChannelStripComponent(ChannelStripComponentBase):
    def __init__(self, *a, **k):
        super(ChannelStripComponent, self).__init__(*a, **k)
        self._crossfade_toggle_A = None
        self._crossfade_toggle_B = None
        self._controls = None
        self._sends_mode = 'A'
        self._sends_active = False

        def make_button_slot(name):
            return self.register_slot(None, getattr(self, '_%s_value' % name), 'value')

        self._crossfade_toggle_slot_A = make_button_slot('crossfade_toggle_A')
        self._crossfade_toggle_slot_B = make_button_slot('crossfade_toggle_B')

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

    def clear_buttons(self):
        for button in [self._crossfade_toggle_A, self._crossfade_toggle_B]:
            if button != None:
                button.reset()

        self._crossfade_toggle_A = None
        self._crossfade_toggle_B = None

        if self._controls != None:
            for control in self._controls:
                if control != None:
                    control.release_parameter()

            self._controls = None

    def disconnect(self):
        super(ChannelStripComponent, self).disconnect()
        self.clear_buttons()

    def _disconnect_parameters(self):
        super(ChannelStripComponent, self)._disconnect_parameters()
        self.clear_buttons()

    def set_track(self, track):
        super(ChannelStripComponent, self).set_track(track)

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

    def set_send_controls(self, controls):
        self._controls = [
                EncoderElement(MIDI_CC_TYPE, 8, controls[0], Live.MidiMap.MapMode.absolute),
                EncoderElement(MIDI_CC_TYPE, 8, controls[1], Live.MidiMap.MapMode.absolute),
                EncoderElement(MIDI_CC_TYPE, 8, controls[2], Live.MidiMap.MapMode.absolute),
                EncoderElement(MIDI_CC_TYPE, 8, controls[3], Live.MidiMap.MapMode.absolute),
                EncoderElement(MIDI_CC_TYPE, 8, controls[4], Live.MidiMap.MapMode.absolute),
                EncoderElement(MIDI_CC_TYPE, 8, controls[5], Live.MidiMap.MapMode.absolute)
                ]

    def sends_off(self):
        if self._controls != None:
            self._sends_active = False
            for control in self._controls:
                control.release_parameter()

    def sends_on(self, mode):
        if liveobj_valid(self._track) and self._controls != None:
            self._sends_active = True
            self._sends_mode = mode

            if mode == 'A':
                count = 0
                for control in self._controls:
                    if count < len(self._track.mixer_device.sends):
                        control.connect_to(self._track.mixer_device.sends[count])
                    else:
                        control.release_parameter()
                    count += 1
            elif mode == 'B':
                count = 6
                for control in self._controls:
                    if count < len(self._track.mixer_device.sends):
                        control.connect_to(self._track.mixer_device.sends[count])
                    else:
                        control.release_parameter()
                    count += 1

    def get_sends_status(self):
        return self._sends_active

    def update(self):
        super(ChannelStripComponent, self).update()

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
    sends_mode = 'A'
    switch_sends_button = ButtonControl()
    send_buttons_mode = 'select'
    send_buttons = control_list(ButtonControl, control_count=6)
    send_volumes_lights = control_list(ButtonControl, control_count=6)
    send_controls_lights = control_list(ButtonControl, control_count=6)
    track_activate_send_buttons = control_list(ButtonControl, control_count=8)
    track_activators = {}
    all_track_activators = False
    track_activators_list = []

    def __init__(self, send_volumes=None, send_controls=None, *a, **k):
        self.send_volumes = send_volumes
        super(MixerComponent, self).__init__(*a, **k)

        for strip in self._channel_strips:
           strip.set_send_controls(send_controls)

        self.update_sends()

    def _create_strip(self):
        return ChannelStripComponent()

    def clear_buttons(self):
        for button in self.send_buttons:
            button.color = 'Color.Off'
            button.set_control_element(None)

        for button in self.track_activate_send_buttons:
            button.color = 'Color.Off'
            button.set_control_element(None)

        self.switch_sends_button.color = 'Color.Off'
        self.switch_sends_button.set_control_element(None)
        self.master_select_button.color = 'Color.Off'
        self.master_select_button.set_control_element(None)
        self.tracks_activate_send_button.color = 'Color.Off'
        self.tracks_activate_send_button.set_control_element(None)

    def update_sends(self):
        tracks = self.song().tracks
        self.all_track_activators = True

        for strip, button in izip_longest(self._channel_strips, self.track_activate_send_buttons):
            if strip._track in tracks:
                index = list(tracks).index(strip._track)

                if index in self.track_activators:
                    if self.track_activators[index] == True:
                        strip.sends_on(self.sends_mode)
                        button.color = 'Color.TrackActivatedSend'
                    else:
                        strip.sends_off()
                        button.color = 'Color.TrackUnactivatedSend'
                        self.all_track_activators = False
                else:
                    self.track_activators[index] = False
                    strip.sends_off()
                    button.color = 'Color.TrackUnactivatedSend'
                    self.all_track_activators = False
            else:
                button.color = 'Color.Off'

        if self.all_track_activators == True:
            self.tracks_activate_send_button.color = 'Color.TracksActivatedSend'
        else:
            self.tracks_activate_send_button.color = 'Color.TracksUnactivatedSend'

    @track_activate_send_buttons.pressed
    def track_activate_send_buttons(self, button):
        button_index = button.index
        tracks = self.song().tracks
        strip = self._channel_strips[button_index]

        if strip._track in tracks:
            index = list(tracks).index(strip._track)

        if self.track_activators[index] != True or self.track_activators[index] == True and len(self.track_activators) > 1:
            self.track_activators[index] = True
            self.track_activators_list.append(index)

        for index in self.track_activators:
            if index not in self.track_activators_list:
                self.track_activators[index] = False

        self.update_sends()

    @track_activate_send_buttons.released
    def track_activate_send_buttons(self, button):
        button_index = button.index
        tracks = self.song().tracks
        strip = self._channel_strips[button_index]

        if strip._track in tracks:
            index = list(tracks).index(strip._track)

        self.track_activators_list.remove(index)

    @tracks_activate_send_button.pressed
    def tracks_activate_send_button(self, button):
        self.all_track_activators = not self.all_track_activators

        for track in self.track_activators:
            self.track_activators[track] = self.all_track_activators

        self.update_sends()

    @send_buttons.pressed
    def send_buttons(self, button):
        if self.sends_mode == 'A':
            index = button.index
        elif self.sends_mode == 'B':
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
            if self.sends_mode == 'A':
                self.sends_mode = 'B'
            elif self.sends_mode == 'B':
                self.sends_mode = 'A'

            self.on_return_tracks_changed()
            self.update_sends()

    @master_select_button.pressed
    def master_select_button(self, button):
        if self.song().view.selected_track != self.song().master_track:
            self.song().view.selected_track = self.song().master_track

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
        self.update_sends()

    def on_return_tracks_changed(self):
        length = len(self.song().return_tracks)
        return_tracks = self.song().return_tracks

        if length > 6:
            if self.sends_mode == 'A':
                side_len = 6
                i_plus = 0
                send_color = 'Color.SendsA'
                volume_color = 'Color.VolumeSendsA'
            elif self.sends_mode == 'B':
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
            self.sends_mode = 'A'
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
        if buttons:
            tracks = self.song().tracks
            self.track_activators = {}

            for strip, track, button in izip_longest(self._channel_strips, self.track_activate_send_buttons, buttons):
                track.set_control_element(button)

                if strip._track in tracks:
                    index = list(tracks).index(strip._track)
                    self.track_activators[index] = strip.get_sends_status()

            self.update_sends()

    def set_tracks_activate_send_button(self, button):
        self.tracks_activate_send_button.set_control_element(None)

        if button:
            tracks = self.song().tracks
            self.all_track_activators = True

            for strip in self._channel_strips:
                if strip._track in tracks:
                    index = list(tracks).index(strip._track)
                    if index in self.track_activators and self.track_activators[index] == False:
                        self.all_track_activators = False

            self.tracks_activate_send_button.set_control_element(button)
            self.update_sends()

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
