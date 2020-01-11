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
from _Framework.ModesComponent import ReenterBehaviour as ReenterBehaviourBase, ModesComponent as ModesComponentBase, AddLayerMode
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import nop
from _Framework import Task
from .ButtonElement import ButtonElement
from .DeviceComponent import DeviceComponent
from .MixerComponent import MixerComponent
from .TransportComponent import TransportComponent
from .SessionComponent import SessionComponent
from .SkinDefault import make_biled_skin

import functools, logging, traceback
logger = logging.getLogger(__name__)
#logger.error('#### !!!!!!!!!!! #########')

NUM_TRACKS = 8
NUM_SCENES = 1
LIVE_CHANNEL = 8
PREFIX_TEMPLATE_SYSEX = (240, 0, 32, 41, 2, 17, 119)
LIVE_TEMPLATE_SYSEX = PREFIX_TEMPLATE_SYSEX + (LIVE_CHANNEL, 247)
TIMER_BLINK = 200

class ReenterBehaviour(ReenterBehaviourBase):
    def update_button(self, component, mode, selected_mode):
        button = component.get_mode_button(mode)
        groups = component.get_mode_groups(mode)
        selected_groups = component.get_mode_groups(selected_mode)
        button.set_light(mode == selected_mode or bool(groups & selected_groups))

class ModesComponent(ModesComponentBase):
    timer = None
    light_select = False
    button = None

    def __init__(self, mixer, device, transport, session, *a, **k):
        super(ModesComponent, self).__init__(*a, **k)
        self._mixer = mixer
        self._device = device
        self._transport = transport
        self._session = session

    def _do_enter_mode(self, name):
        self._mixer.clear_buttons()
        self._device.clear_buttons()
        self._transport.clear_buttons()
        self._session.clear_buttons()
        super(ModesComponent, self)._do_enter_mode(name)

        if name.find('mode_2') is not -1:
            self.application().view.show_view('Detail/Clip')
        else:
            self.application().view.show_view('Detail/DeviceChain')

        if name.find('mode_3') is not -1:
            self._mixer.enable_sends_for_selected_track_only(False)
        else:
            self._mixer.enable_sends_for_selected_track_only(True)

    def blink(self):
        self.light_select = not self.light_select
        self.button.set_light(self.light_select)

    def disconnect(self):
        super(ModesComponent, self).disconnect()
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.light_select = False
        return

    def _update_buttons(self, selected):
        super(ModesComponent, self)._update_buttons(selected)

        if self.timer:
            self.timer.stop()

        if self.is_enabled():
            if selected != None and selected.find('detail') is not -1:
                self.button = self.get_mode_button(selected.replace('_detail', ''))
                self.blink()
                self.timer = Live.Base.Timer(callback=self.blink, interval=TIMER_BLINK, repeat=True)
                self.timer.start()

class LaunchControlXL(IdentifiableControlSurface):
    def __init__(self, c_instance, *a, **k):
        super(LaunchControlXL, self).__init__(c_instance=c_instance, product_id_bytes=(0, 32, 41, 97), *a, **k)
        self._biled_skin = make_biled_skin()

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
            transport = self._create_transport()
            session.set_mixer(mixer)
            self.set_device_component(device)
            self.set_highlighting_session_component(session)

            mixer_modes = ModesComponent(mixer, device, transport, session)

            set_main_mode = partial(setattr, mixer_modes, 'selected_mode')

            mixer_modes.add_mode('mode_1', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights
                 )),
             AddLayerMode(mixer, Layer(
                 track_select_buttons=self._state_buttons1,
                 send_select_buttons=self._state_buttons3,
                 switch_sends_button=self._button_15,
                 master_select_button=self._button_16
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_1_detail')))

            mixer_modes.add_mode('mode_1_detail', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights,
                 device_buttons=self._state_buttons1,
                 on_off_button=self._button_9,
                 bank_prev_button=self._button_11,
                 bank_next_button=self._button_12,
                 prev_device_button=self._button_15,
                 next_device_button=self._button_16
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_1')))

            mixer_modes.add_mode('mode_2', [
             AddLayerMode(session, Layer(
                 page_left_button=self._button_1,
                 page_right_button=self._button_2,
                 track_bank_left_button=self._button_9,
                 track_bank_right_button=self._button_10,
                 clip_left_button=self._button_6,
                 clip_right_button=self._button_7,
                 scene_up_button=self._button_8,
                 scene_down_button=self._button_16
                 )),
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights
                 )),
             AddLayerMode(transport, Layer(
                 metronome_button = self._button_4,
                 delete_clip_button=self._button_5,
                 overdub_button=self._button_12,
                 arm_button=self._button_13,
                 stop_clip_button=self._button_14,
                 play_clip_button=self._button_15
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_2_detail')))

            mixer_modes.add_mode('mode_2_detail', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights
                 )),
             AddLayerMode(mixer, Layer(
                 track_select_buttons=self._state_buttons1,
                 arm_buttons=self._state_buttons2
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_2')))

            mixer_modes.add_mode('mode_3', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights
                 )),
             AddLayerMode(mixer, Layer(
                 track_activate_send_buttons=self._state_buttons1,
                 #send_mute_buttons=self._state_buttons3,
                 send_select_buttons=self._state_buttons3,
                 switch_sends_button=self._button_15,
                 tracks_activate_send_button=self._button_16
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_3_detail')))

            mixer_modes.add_mode('mode_3_detail', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights,
                 device_buttons=self._state_buttons1,
                 on_off_button=self._button_9,
                 bank_prev_button=self._button_11,
                 bank_next_button=self._button_12,
                 prev_device_button=self._button_15,
                 next_device_button=self._button_16
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_3')))

            mixer_modes.add_mode('mode_4', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights
                 )),
             AddLayerMode(mixer, Layer(
                 mute_buttons=self._state_buttons1,
                 solo_buttons=self._state_buttons2
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_4_detail')))

            mixer_modes.add_mode('mode_4_detail', [
             AddLayerMode(device, Layer(
                 parameter_controls=self._device_controls,
                 parameter_lights=self._device_controls_lights
                 )),
             AddLayerMode(mixer, Layer(
                 crossfader_buttons_A=self._state_buttons1,
                 crossfader_buttons_B=self._state_buttons2
                 ))
             ], behaviour=ReenterBehaviour(on_reenter=partial(set_main_mode, 'mode_4')))

            mixer_modes.layer = Layer(
                    mode_1_button=self._mode_1_button,
                    mode_2_button=self._mode_2_button,
                    mode_3_button=self._mode_3_button,
                    mode_4_button=self._mode_4_button
                    )

            mixer_modes.selected_mode = 'mode_1'

    def _create_controls(self):

        def make_button(identifier, name, midi_type=MIDI_CC_TYPE, skin=self._biled_skin):
            return ButtonElement(True, midi_type, LIVE_CHANNEL, identifier, name=name, skin=skin)

        def make_button_list(identifiers, name):
            return [ make_button(identifier, name % (i + 1), MIDI_NOTE_TYPE, self._biled_skin) for i, identifier in enumerate(identifiers)
                   ]

        def make_encoder(identifier, name):
            return EncoderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, Live.MidiMap.MapMode.absolute, name=name)

        def make_slider(identifier, name):
            return SliderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, name=name)

        # controls
        # 13 14 15 16 17 18 19 20
        # 29 30 31 32 33 34 35 36
        # 49 50 51 52 53 54 55 56

        # controls lights
        # 13 29 45 61 77 93 109 125
        # 14 30 46 62 78 94 110 126
        # 15 31 47 63 79 95 111 127

        # buttons
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

        # mode_1
        self._mode_1_button = make_button(105, 'Mode_1', MIDI_NOTE_TYPE)
        # mode_2
        self._mode_2_button = make_button(106, 'Mode_2', MIDI_NOTE_TYPE)
        # mode_3
        self._mode_3_button = make_button(107, 'Mode_3', MIDI_NOTE_TYPE)
        # mode_4
        self._mode_4_button = make_button(108, 'Mode_4', MIDI_NOTE_TYPE)

        self._up_button = make_button(104, 'Up')
        self._down_button = make_button(105, 'Down')
        self._left_button = make_button(106, 'Left')
        self._right_button = make_button(107, 'Right')

        self._crossfader_control = make_encoder(53, 'Crossfader_Control')
        self._tempo_control = make_encoder(54, 'Tempo_Control')
        self._prehear_volume_control = make_encoder(55, 'Prehear_Volume_Control')
        self._master_volume_control = make_encoder(56, 'Master_Volume_Control')

        self._crossfader_control_light = make_button(79, 'Crossfader_Control_Light', MIDI_NOTE_TYPE)
        self._tempo_control_light = make_button(95, 'Tempo_Control_Light', MIDI_NOTE_TYPE)
        self._prehear_volume_light = make_button(111, 'Prehear_Volume_Light', MIDI_NOTE_TYPE)
        self._master_volume_light = make_button(127, 'Master_Volume_Light', MIDI_NOTE_TYPE)

        self._volume_faders = ButtonMatrixElement(rows=[[ make_slider(77 + i, 'Volume_%d' % (i + 1)) for i in xrange(8) ]])

        self._send_controls_lights = ButtonMatrixElement(rows=[
         make_button_list([
          13, 14, 15, 45, 46, 47], 'Send_Control_Light_%d')])

        self.send_volumes = ButtonMatrixElement(rows=[[
            make_encoder(14, 'Send_Volume_1'),
            make_encoder(30, 'Send_Volume_2'),
            make_encoder(50, 'Send_Volume_3'),
            make_encoder(16, 'Send_Volume_4'),
            make_encoder(32, 'Send_Volume_5'),
            make_encoder(52, 'Send_Volume_6')
            ]])

        self._send_volumes_lights = ButtonMatrixElement(rows=[
         make_button_list([
          29, 30, 31, 61, 62, 63], 'Send_Volume_Light_%d')])

        self._state_buttons1 = ButtonMatrixElement(rows=[
         make_button_list(chain(xrange(41, 45), xrange(57, 61)), 'Track_Select_%d')])
        self._state_buttons2 = ButtonMatrixElement(rows=[
         make_button_list(chain(xrange(73, 77), xrange(89, 93)), 'Track_State_%d')])
        self._state_buttons3 = ButtonMatrixElement(rows=[
         make_button_list(chain(xrange(73, 77), xrange(89, 91)), 'Track_State_%d')])

        self._button_1 =  make_button(41, 'Button_1', MIDI_NOTE_TYPE)
        self._button_2 =  make_button(42, 'Button_2', MIDI_NOTE_TYPE)
        self._button_3 =  make_button(43, 'Button_3', MIDI_NOTE_TYPE)
        self._button_4 =  make_button(44, 'Button_4', MIDI_NOTE_TYPE)
        self._button_5 =  make_button(57, 'Button_5', MIDI_NOTE_TYPE)
        self._button_6 =  make_button(58, 'Button_6', MIDI_NOTE_TYPE)
        self._button_7 =  make_button(59, 'Button_7', MIDI_NOTE_TYPE)
        self._button_8 =  make_button(60, 'Button_8', MIDI_NOTE_TYPE)
        self._button_9 =  make_button(73, 'Button_9', MIDI_NOTE_TYPE)
        self._button_10 =  make_button(74, 'Button_10', MIDI_NOTE_TYPE)
        self._button_11 =  make_button(75, 'Button_11', MIDI_NOTE_TYPE)
        self._button_12 =  make_button(76, 'Button_12', MIDI_NOTE_TYPE)
        self._button_13 =  make_button(89, 'Button_13', MIDI_NOTE_TYPE)
        self._button_14 =  make_button(90, 'Button_14', MIDI_NOTE_TYPE)
        self._button_15 =  make_button(91, 'Button_15', MIDI_NOTE_TYPE)
        self._button_16 =  make_button(92, 'Button_16', MIDI_NOTE_TYPE)

    def _create_device(self):
        device = DeviceComponent(name='Device_Component', is_enabled=True, device_selection_follows_track_selection=True)
        return device

    def _create_mixer(self):
        mixer = MixerComponent(
                self.send_volumes,
                NUM_TRACKS,
                is_enabled=True,
                auto_name=True
                )
        mixer.layer = Layer(
                volume_controls=self._volume_faders,
                send_controls_lights=self._send_controls_lights,
                send_volumes_lights=self._send_volumes_lights,
                crossfader_control_light=self._crossfader_control_light,
                tempo_control_light=self._tempo_control_light,
                prehear_volume_light=self._prehear_volume_light,
                master_volume_light=self._master_volume_light
                )

        mixer.set_crossfader_control(self._crossfader_control)
        mixer.set_prehear_volume_control(self._prehear_volume_control)
        mixer.master_strip().set_volume_control(self._master_volume_control)

        for channel_strip in map(mixer.channel_strip, xrange(NUM_TRACKS)):
            channel_strip.empty_color = 'Color.Off'

        return mixer

    def _create_session(self):
        session = SessionComponent(num_tracks=NUM_TRACKS, num_scenes=NUM_SCENES, is_enabled=True, auto_name=True, enable_skinning=True)
        session.layer = Layer(
                scene_stop_button=self._left_button,
                scene_play_button=self._right_button,
                scene_bank_up_button=self._up_button,
                scene_bank_down_button=self._down_button
                )

        self._on_session_offset_changed.subject = session
        return session

    def _create_transport(self):
        transport = TransportComponent(name='Transport', is_enabled=True)
        transport.layer = Layer(tempo_control=self._tempo_control)
        return transport

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
