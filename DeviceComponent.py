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
    prev_device_button = ButtonControl()
    next_device_button = ButtonControl()
    reset_device_button = ButtonControl()

    def clear_buttons(self):
        self.prev_device_button.color = 'Color.Off'
        self.next_device_button.color = 'Color.Off'
        self.reset_device_button.color = 'Color.Off'
        self.prev_device_button.set_control_element(None)
        self.next_device_button.set_control_element(None)
        self.reset_device_button.set_control_element(None)

    def set_prev_device_button(self, button):
        if button:
            self.prev_device_button.set_control_element(button)
            self.prev_device_button.color = 'Color.PrevDevice'

    def set_next_device_button(self, button):
        if button:
            self.next_device_button.set_control_element(button)
            self.next_device_button.color = 'Color.NextDevice'

    def set_reset_device_button(self, button):
        if button:
            self.reset_device_button.set_control_element(button)
            self.reset_device_button.color = 'Color.On'

    @reset_device_button.pressed
    def reset_device_button(self, button):
        pass

    @prev_device_button.pressed
    def prev_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.left)

    @next_device_button.pressed
    def next_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.right)

    def set_on_off_button(self, button):
        if button:
            button.set_on_off_values('Color.DeviceOn', 'Color.DeviceOff')

        super(DeviceComponent, self).set_on_off_button(button)

    def set_lock_button(self, button):
        if button:
            button.set_on_off_values('Color.LockOn', 'Color.LockOff')

        super(DeviceComponent, self).set_lock_button(button)

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
