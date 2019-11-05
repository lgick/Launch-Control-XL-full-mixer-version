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

class ChannelStripComponent(ChannelStripComponentBase):
    def set_crossfade_toggle(self, button):
        if button != self._crossfade_toggle:
            self.reset_button_on_exchange(self._crossfade_toggle)
            self._crossfade_toggle = button
            self._crossfade_toggle_slot.subject = button
            self.update()

    def _on_cf_assign_changed(self):
        if self.is_enabled() and self._crossfade_toggle:
            state = self._track.mixer_device.crossfade_assign if self._track else 1
            value_to_send = None
            if state == 0: #A
                value_to_send = 'Mixer.CrossA'
            elif state == 1: #Off
                value_to_send = 'Mixer.CrossOff'
            elif state == 2: #B
                value_to_send = 'Mixer.CrossB'
            self._crossfade_toggle.set_light(value_to_send)
        return

    send_lights = control_list(ButtonControl, control_count=2, color='Mixer.Sends', disabled_color='Mixer.NoTrack')

    def set_track(self, track):
        super(ChannelStripComponent, self).set_track(track)
        for light in self.send_lights:
            light.enabled = bool(track)


class MixerComponent(MixerComponentBase):
    next_sends_button = ButtonControl()
    prev_sends_button = ButtonControl()

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)
        self._update_send_buttons()

    def _create_strip(self):
        return ChannelStripComponent()

    def set_send_controls(self, controls):
        self._send_controls = controls
        for index, channel_strip in enumerate(self._channel_strips):
            if self.send_index is None:
                channel_strip.set_send_controls([None])
            else:
                send_controls = [ controls.get_button(index, i) for i in xrange(2) ] if controls else [None]
                skipped_sends = [ None for _ in xrange(self.send_index) ]
                channel_strip.set_send_controls(skipped_sends + send_controls)

        return

    def set_send_lights(self, lights):
        for index, channel_strip in enumerate(self._channel_strips):
            elements = None
            if lights is not None:
                lights.reset()
                elements = None if self.send_index is None else [ lights.get_button(index, i) for i in xrange(2) ]
            channel_strip.send_lights.set_control_element(elements)

        return

    def _get_send_index(self):
        return super(MixerComponent, self)._get_send_index()

    def _set_send_index(self, index):
        if index is not None and index % 2 > 0:
            index -= 1
        super(MixerComponent, self)._set_send_index(index)
        self._update_send_buttons()
        return

    send_index = property(_get_send_index, _set_send_index)

    def _update_send_buttons(self):
        self.next_sends_button.enabled = self.send_index is not None and self.send_index < self.num_sends - 2
        self.prev_sends_button.enabled = self.send_index is not None and self.send_index > 0
        return

    @next_sends_button.pressed
    def next_sends_button(self, button):
        self.send_index = min(self.send_index + 2, self.num_sends - 1)

    @prev_sends_button.pressed
    def prev_sends_button(self, button):
        self.send_index = max(self.send_index - 2, 0)

    def set_track_select_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.TrackSelected', 'Mixer.TrackUnselected')
            strip.set_select_button(button)

    def set_solo_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.SoloOn', 'Mixer.SoloOff')
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.MuteOn', 'Mixer.MuteOff')
            strip.set_mute_button(button)

    def set_crossfader_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.CrossOn', 'Mixer.CrossOff')
            strip.set_crossfade_toggle(button)


    def set_send_select_buttons(self, buttons):
        return True

    def set_master_button(self, button):
        return True

    def set_track_activate_send_buttons(self, buttons):
        return True

    def set_send_mute_buttons(self, buttons):
        return True




    def set_send_controls(self, controls):
        return True

    def set_send_controls_lights(self, controls):
        return True

    def set_send_volumes(self, controls):
        return True

    def set_send_volumes_lights(self, controls):
        return True
