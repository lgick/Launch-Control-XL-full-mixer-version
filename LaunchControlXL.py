# uncompyle6 version 3.4.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10)
# [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/LaunchControlXL.py
# Compiled at: 2019-04-09 19:23:44
from __future__ import absolute_import, print_function, unicode_literals
from functools import partial
from itertools import chain
import Live
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.IdentifiableControlSurface import IdentifiableControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import ModeButtonBehaviour, ModesComponent, AddLayerMode
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import nop
from _Framework import Task
from .ButtonElement import ButtonElement
from .DeviceComponent import DeviceComponent, DeviceModeComponent
from .MixerComponent import MixerComponent
from .SkinDefault import make_biled_skin, make_default_skin

MIXER_NUM_TRACKS = 6
NUM_TRACKS = 8
NUM_SCENES = 1
LIVE_CHANNEL = 8
PREFIX_TEMPLATE_SYSEX = (240, 0, 32, 41, 2, 17, 119)
LIVE_TEMPLATE_SYSEX = PREFIX_TEMPLATE_SYSEX + (LIVE_CHANNEL, 247)

class LaunchControlXL(IdentifiableControlSurface):
    def __init__(self, c_instance, *a, **k):
        super(LaunchControlXL, self).__init__(c_instance=c_instance, product_id_bytes=(0, 32, 41, 97), *a, **k)
        self._biled_skin = make_biled_skin()
        self._default_skin = make_default_skin()

        with self.component_guard():
            self._create_controls()
        self._initialize_task = self._tasks.add(Task.sequence(Task.wait(1), Task.run(self._create_components)))
        self._initialize_task.kill()

    def on_identified(self):
        self._send_live_template()

    def _create_components(self):
        self._initialize_task.kill()
        self._disconnect_and_unregister_all_components()
        with self.component_guard():
            mixer = self._create_mixer()
            session = self._create_session()
            device = self._create_device()
            session.set_mixer(mixer)
            self.set_device_component(device)
        self.set_highlighting_session_component(session)

    def _create_controls(self):

        def make_button(identifier, name, midi_type=MIDI_CC_TYPE, skin=self._default_skin):
            #self.log_message(name)
            return ButtonElement(True, midi_type, LIVE_CHANNEL, identifier, name=name, skin=skin)

        def make_button_list(identifiers, name):
            return [ make_button(identifier, name % (i + 1), MIDI_NOTE_TYPE, self._biled_skin) for i, identifier in enumerate(identifiers)
                   ]

        def make_encoder(identifier, name):
            return EncoderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, Live.MidiMap.MapMode.absolute, name=name)

        def make_slider(identifier, name):
            return SliderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, name=name)

        # 13 29 45 61 77 93 109 125
        # 14 30 46 62 78 94 110 126
        # 15 31 47 63 79 95 111 127

        # 41 42 43 44 57 58 59 60
        # 73 74 75 76 89 90 91 92

        self._device_controls = ButtonMatrixElement(rows=[[
            make_encoder(17, 'Device_Control_1'),
            make_encoder(18, 'Device_Control_2'),
            make_encoder(19, 'Device_Control_3'),
            make_encoder(20, 'Device_Control_4'),
            make_encoder(33, 'Device_Control_5'),
            make_encoder(34, 'Device_Control_6'),
            make_encoder(35, 'Device_Control_7'),
            make_encoder(36, 'Device_Control_8')
            ]])

        self._device_controls_lights = ButtonMatrixElement(rows=[make_button_list([77, 93, 109, 125, 78, 94, 110, 126], 'Device_Control_Light_%d')])

        # device mode
        self._device_mode_button = make_button(105, 'Device_Mode', MIDI_NOTE_TYPE)
        # solo/mute mode
        self._mute_mode_button = make_button(106, 'Mute_Mode', MIDI_NOTE_TYPE)
        # send mode
        self._send_mode_button = make_button(107, 'Send_Mode', MIDI_NOTE_TYPE)
        # crossfader mode
        self._crossfader_mode_button = make_button(108, 'Crossfader_Mode', MIDI_NOTE_TYPE)

        self._up_button = make_button(104, 'Up')
        self._down_button = make_button(105, 'Down')
        self._left_button = make_button(106, 'Left')
        self._right_button = make_button(107, 'Right')

        self._crossfader_control = make_encoder(53, 'Crossfader_Control')
        self._tempo_control = make_encoder(54, 'Tempo_Control')
        self._prehear_volume_control = make_encoder(55, 'Prehear_Volume_Control')
        self._master_volume_control = make_encoder(56, 'Master_Volume_Control')

        #self._crossfader_control_light = make_button(95, 'Crossfader_Control_Light')
        #self._prehear_volume_light = make_button(111, 'Prehear_Volume_Light')
        #self._master_volume_light = make_button(127, 'Master_Volume_Light')

        self._volume_faders = ButtonMatrixElement(rows=[[ make_slider(77 + i, 'Volume_%d' % (i + 1)) for i in xrange(8) ]])

        #self._send_encoders = ButtonMatrixElement(rows=[[ make_encoder(13 + i, 'Top_Send_%d' % (i + 1)) for i in xrange(8) ], [ make_encoder(29 + i, 'Bottom_Send_%d' % (i + 1)) for i in xrange(8) ]])
        #self._send_encoders = ButtonMatrixElement(rows=[[ make_encoder(13 + i, 'Send_%d' % (i + 1)) for i in xrange(6) ]])

        self._send_controls = ButtonMatrixElement(rows=[[
            make_encoder(13, 'Send_Control_1'),
            make_encoder(14, 'Send_Control_2'),
            make_encoder(29, 'Send_Control_3'),
            make_encoder(30, 'Send_Control_4'),
            make_encoder(49, 'Send_Control_5'),
            make_encoder(50, 'Send_Control_6')
            ]])

        self._send_controls_lights = ButtonMatrixElement(rows=[
         make_button_list([
          13, 29, 14, 30, 15, 31], 'Send_Control_Light_%d')])

        self._send_volumes = ButtonMatrixElement(rows=[[
            make_encoder(15, 'Send_Volume_1'),
            make_encoder(16, 'Send_Volume_2'),
            make_encoder(31, 'Send_Volume_3'),
            make_encoder(32, 'Send_Volume_4'),
            make_encoder(51, 'Send_Volume_5'),
            make_encoder(52, 'Send_Volume_6')
            ]])

        self._send_volumes_lights = ButtonMatrixElement(rows=[
         make_button_list([
          45, 61, 46, 62, 47, 63], 'Send_Volume_Light_%d')])

        self._state_buttons1 = ButtonMatrixElement(rows=[
         make_button_list(chain(xrange(41, 45), xrange(57, 61)), 'Track_Select_%d')])
        self._state_buttons2 = ButtonMatrixElement(rows=[
         make_button_list(chain(xrange(73, 77), xrange(89, 93)), 'Track_State_%d')])
        self._state_buttons3 = ButtonMatrixElement(rows=[
         make_button_list(chain(xrange(73, 77), xrange(89, 91)), 'Track_State_%d')])
        self._state_buttons4 = ButtonMatrixElement(rows=[
         make_button_list(xrange(91, 93), 'Track_State_%d')])
        self._state_buttons5 = ButtonMatrixElement(rows=[
         make_button_list(xrange(92, 93), 'Track_State_%d')])

    def _create_device(self):
        device = DeviceComponent(name='Device_Component', is_enabled=True, device_selection_follows_track_selection=True)
        device.layer = Layer(parameter_controls=self._device_controls, parameter_lights=self._device_controls_lights, priority=1)

        #device_settings_layer = Layer()
        #mode = DeviceModeComponent(component=device, device_settings_mode=[
        # AddLayerMode(device, device_settings_layer)], is_enabled=True)
        #mode.layer = Layer(device_mode_button=self._device_mode_button)

        #parameter_controls=self._device_controls,
        #bank_buttons=self._device_bank_buttons,
        #bank_prev_button=self._device_prev_bank_button,
        #bank_next_button=self._device_next_bank_button,
        #prev_device_button=self._left_button,
        #next_device_button=self._right_button,
        #on_off_button=self._down_button,
        #lock_button=self._up_button

        return device

    def _create_mixer(self):
        mixer = MixerComponent(NUM_TRACKS, is_enabled=True, auto_name=True)
        mixer.layer = Layer(
                volume_controls=self._volume_faders,
                send_controls=self._send_controls,
                send_controls_lights=self._send_controls_lights,
                send_volumes=self._send_volumes,
                send_volumes_lights=self._send_volumes_lights
                )

        mixer.set_crossfader_control(self._crossfader_control)
        mixer.set_prehear_volume_control(self._prehear_volume_control)
        mixer.master_strip().set_volume_control(self._master_volume_control)

        for channel_strip in map(mixer.channel_strip, xrange(NUM_TRACKS)):
            channel_strip.empty_color = 'Mixer.NoTrack'

        mixer_modes = ModesComponent()
        mixer_modes.add_mode('device', [
         AddLayerMode(mixer, Layer(
             track_select_buttons=self._state_buttons1,
             send_select_buttons=self._state_buttons3,
             master_button=self._state_buttons5
             ))])
        mixer_modes.add_mode('mute', [
         AddLayerMode(mixer, Layer(mute_buttons=self._state_buttons1, solo_buttons=self._state_buttons2))])
        mixer_modes.add_mode('send', [
         AddLayerMode(mixer, Layer(track_activate_send_buttons=self._state_buttons1, send_mute_buttons=self._state_buttons3))])
        mixer_modes.add_mode('crossfader', [
         AddLayerMode(mixer, Layer(crossfader_buttons_A=self._state_buttons1, crossfader_buttons_B=self._state_buttons2))])
        mixer_modes.layer = Layer(device_button=self._device_mode_button, mute_button=self._mute_mode_button, send_button=self._send_mode_button, crossfader_button=self._crossfader_mode_button)
        mixer_modes.selected_mode = 'send'
        return mixer

    def _create_session(self):
        session = SessionComponent(num_tracks=NUM_TRACKS, num_scenes=NUM_SCENES, is_enabled=True, auto_name=True, enable_skinning=True)
        #stop_all_clips_button=self._left_button
        #track_bank_left_button=when_bank_off(self._left_button)
        #track_bank_right_button=when_bank_off(self._right_button)
        #scene_bank_up_button=when_bank_off(self._up_button)
        #scene_bank_down_button=when_bank_off(self._down_button)
        #page_left_button=when_bank_on(self._left_button)
        #page_right_button=when_bank_on(self._right_button)
        #page_up_button=when_bank_on(self._up_button)
        #page_down_button=when_bank_on(self._down_button)
        #stop_track_clip_buttons=self._stop_buttons
        #stop_all_clips_button=self._stop_all_button
        #scene_launch_buttons=self._scene_launch_buttons
        #clip_launch_buttons=self._session_matrix

        #session.layer = Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button, scene_bank_up_button=self._up_button, scene_bank_down_button=self._down_button)
        session.layer = Layer(stop_all_clips_button=self._left_button, scene_launch_buttons=ButtonMatrixElement(rows=[[self._right_button]]), scene_bank_up_button=self._up_button, scene_bank_down_button=self._down_button)
        self._on_session_offset_changed.subject = session
        return session

    @subject_slot('offset')
    def _on_session_offset_changed(self):
        session = self._on_session_offset_changed.subject
        self._show_controlled_tracks_message(session)

    def _show_controlled_tracks_message(self, session):
        start = session.track_offset() + 1
        end = min(start + 8, len(session.tracks_to_use()))
        if start < end:
            self.show_message('Controlling Track %d to %d' % (start, end))
        else:
            self.show_message('Controlling Track %d' % start)

    def _send_live_template(self):
        self._send_midi(LIVE_TEMPLATE_SYSEX)
        self._initialize_task.restart()

    def handle_sysex(self, midi_bytes):
        if midi_bytes[:7] == PREFIX_TEMPLATE_SYSEX:
            if midi_bytes[7] == LIVE_CHANNEL:
                if self._initialize_task.is_running:
                    self._create_components()
                else:
                    self.update()
        else:
            super(LaunchControlXL, self).handle_sysex(midi_bytes)
