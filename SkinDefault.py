# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10) 
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/SkinDefault.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from _Framework.Skin import Skin
from _Framework.ButtonElement import Color

class Defaults:

    class DefaultButton:
        On = Color(127)
        Off = Color(0)
        Disabled = Color(0)


class BiLedColors:

    class Mixer:
        SoloOn = Color(60)
        SoloOff = Color(12)
        MuteOn = Color(12)
        MuteOff = Color(63)
        ArmSelected = Color(15)
        ArmUnselected = Color(13)
        TrackSelected = Color(62)
        TrackUnselected = Color(29)
        Pans = Color(60)

        Up = Color(60)
        Down = Color(60)
        Stop = Color(60)
        Play = Color(60)

        ResetDevice = Color(15)
        SwitchDevice = Color(15)
        PrevDevice = Color(15)
        NextDevice = Color(15)

        TrackSelectButtonOff = Color(29)
        TrackSelectButtonOn = Color(63)
        SendSelectButtonOff = Color(29)
        SendSelectButtonOn = Color(63)
        SendSwitchOff = Color(13)
        SendSwitchOn = Color(15)
        CrossOff = Color(13)
        CrossOn = Color(15)

        NoTrack = Color(0)
        Sends = Color(62)
        VolumeSends = Color(60)

    class Device:
        Parameters = Color(13)
        NoDevice = Color(0)
        BankSelected = Color(15)
        BankUnselected = Color(0)


def make_default_skin():
    return Skin(Defaults)


def make_biled_skin():
    return Skin(BiLedColors)
