# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/DeviceComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
import Live
from itertools import izip_longest
from _Framework.Control import control_list, ButtonControl
from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase
from _Framework.SubjectSlot import subject_slot, subject_slot_group, Subject

import functools, logging, traceback
logger = logging.getLogger(__name__)
#logger.error('#### !!!!!!!!!!! #########')

class DeviceComponent(DeviceComponentBase):
    parameter_lights = control_list(ButtonControl, control_count=8, enabled=False, color='Color.DeviceControlOn', disabled_color='Color.DeviceControlOff')
    prev_device_button = ButtonControl()
    next_device_button = ButtonControl()
    device_buttons = control_list(ButtonControl, control_count=8)

    def clear_buttons(self):
        for button in self.device_buttons:
            if button != None:
                button.color = 'Color.Off'
                button.set_control_element(None)

        self.prev_device_button.color = 'Color.Off'
        self.next_device_button.color = 'Color.Off'
        self.prev_device_button.set_control_element(None)
        self.next_device_button.set_control_element(None)

    @prev_device_button.pressed
    def prev_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.left)

    @next_device_button.pressed
    def next_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.right)

    @device_buttons.pressed
    def device_buttons(self, button):
        index = button.index
        track = self.song().view.selected_track

        if len(track.devices) > index:
            device_to_select = track.devices[index]
            self.song().view.select_device(device_to_select)
            self.set_device(device_to_select)

    @subject_slot('selected_device')
    def __on_selected_device_changed(self):
        super(DeviceComponent, self).__on_selected_device_changed()
        self.update_device_buttons()

    def update_device_selection(self):
        super(DeviceComponent, self).update_device_selection()
        self.update_device_buttons()

    def update_device_buttons(self):
        track = self.song().view.selected_track
        device_to_select = track.view.selected_device

        for button, device in izip_longest(self.device_buttons, track.devices):
            if button:
                if device == None:
                    button.color = 'Color.Off'
                else:
                    if device == device_to_select:
                        button.color = 'Color.DeviceOn'
                    else:
                        button.color = 'Color.DeviceOff'

    def set_prev_device_button(self, button):
        if button:
            self.prev_device_button.set_control_element(button)
            self.prev_device_button.color = 'Color.PrevDevice'

    def set_next_device_button(self, button):
        if button:
            self.next_device_button.set_control_element(button)
            self.next_device_button.color = 'Color.NextDevice'

    def set_bank_prev_button(self, button):
        if self._bank_down_button != None:
            self._bank_down_button.reset()

        if button != self._bank_down_button:
            if button:
                button.set_on_off_values('Color.BankOn', 'Color.BankOff')

            self._bank_down_button = button
            self._bank_down_button_slot.subject = button
            self.update()

    def set_bank_next_button(self, button):
        if self._bank_up_button != None:
            self._bank_up_button.reset()

        if button != self._bank_up_button:
            if button:
                button.set_on_off_values('Color.BankOn', 'Color.BankOff')

            self._bank_up_button = button
            self._bank_up_button_slot.subject = button
            self.update()

    def set_on_off_button(self, button):
        if self._on_off_button != None:
            self._on_off_button.reset()

        if button:
            button.set_on_off_values('Color.DeviceOn', 'Color.DeviceOff')

        self._on_off_button = button
        self._on_off_button_slot.subject = button
        self._update_on_off_button()

    def set_device_buttons(self, buttons):
        if buttons:
            for device_button, button in izip_longest(self.device_buttons, buttons):
                device_button.set_control_element(button)

            self.update_device_buttons()

    def _scroll_device_view(self, direction):
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def set_device(self, device):
        super(DeviceComponent, self).set_device(device)
        for light in self.parameter_lights:
            light.enabled = bool(device)
