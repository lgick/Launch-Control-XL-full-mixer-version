# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/SkinDefault.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from _Framework.Skin import Skin
from _Framework.ButtonElement import Color

class BiLedColors:
    class Color:
        Off = Color(0)


        #controls
        SendsA = Color(63)
        SendsB = Color(15)

        VolumeSendsA = Color(62)
        VolumeSendsB = Color(62)

        DeviceControlOn = Color(15)
        DeviceControlOff = Color(13)

        CrossControl = Color(60)
        TempoControl = Color(12)
        PrehearVolume = Color(60)
        MasterVolume = Color(60)


        # nav buttons
        NavUp = Color(60)
        NavDown = Color(60)
        NavLeft = Color(60)
        NavRight = Color(60)


        # Device mode
        TrackSelected = Color(58)
        TrackUnselected = Color(29)

        SendSelected = Color(58)
        SendUnselected = Color(29)

        MasterSelected = Color(15)
        MasterUnselected = Color(13)


        # Mute mode
        SoloOn = Color(60)
        SoloOff = Color(29)

        MuteOn = Color(29)
        MuteOff = Color(60)


        # Send mode
        TrackActivatedSend = Color(60)
        TrackUnactivatedSend = Color(29)

        SendMuteOn = Color(60)
        SendMuteOff = Color(28)

        SendSideA = Color(15)
        SendSideB = Color(60)

        TracksActivatedSend = Color(60)
        TracksUnactivatedSend = Color(29)


        # Cross mode
        CrossOn = Color(13)
        CrossOff = Color(12)


def make_biled_skin():
    return Skin(BiLedColors)
