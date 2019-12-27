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
    def clear_buttons(self):
        pass

    def set_metronome_button(self, button):
        if button:
            button.set_on_off_values('Color.MetronomeOn', 'Color.MetronomeOff')
        self._metronome_toggle.set_toggle_button(button)

    def set_tap_tempo_button(self, button):
        if self._tap_tempo_button != button:
            self._tap_tempo_button = button
            self._tap_tempo_value.subject = button
            self._update_tap_tempo_button()

    def set_stop_clip_button(self, button):
        if button:
            button.color = 'Color.StopClip'
        #self._song().view.selected_track.stop_all_clips(False)
