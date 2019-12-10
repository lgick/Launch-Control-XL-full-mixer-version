# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/DeviceComponent.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.Control import control_list, ButtonControl
from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase

class DeviceComponent(DeviceComponentBase):
    parameter_lights = control_list(ButtonControl, control_count=8, enabled=False, color='Color.DeviceControlOn', disabled_color='Color.DeviceControlOff')
    prev_device_button = ButtonControl(color='Color.PrevDevice')
    next_device_button = ButtonControl(color='Color.NextDevice')

    @prev_device_button.pressed
    def prev_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.left)

    @next_device_button.pressed
    def next_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.right)

    def set_on_off_button(self, button):
        if button:
            button.set_on_off_values('Color.DeviceOn', 'Color.DeviceOff')
            self._on_off_button = button
            self._on_off_button_slot.subject = button
            self._update_on_off_button()

    def set_lock_button(self, button):
        if button:
            button.set_on_off_values('Color.LockOn', 'Color.LockOff')
            self._lock_button = button
            self._lock_button_slot.subject = button
            self._update_lock_button()
            return

    def _scroll_device_view(self, direction):
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def set_device(self, device):
        super(DeviceComponent, self).set_device(device)
        for light in self.parameter_lights:
            light.enabled = bool(device)

    def set_bank_buttons(self, buttons):
        for button in buttons or []:
            if button:
                button.set_on_off_values('Color.NavDown', 'Color.Off')

        super(DeviceComponent, self).set_bank_buttons(buttons)

    def _is_banking_enabled(self):
        return True
