# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: game_state.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='game_state.proto',
  package='solitaire.solitaire_core',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x10game_state.proto\x12\x18solitaire.solitaire_core\"f\n\x04\x43\x61rd\x12,\n\x04suit\x18\x01 \x01(\x0e\x32\x1e.solitaire.solitaire_core.Suit\x12\x30\n\x04rank\x18\x02 \x01(\x0e\x32\".solitaire.solitaire_core.CardRank\"l\n\x10VisibleGameState\x12\r\n\x05talon\x18\x01 \x01(\x04\x12\x12\n\nsuit_stack\x18\x02 \x01(\x04\x12\x14\n\x0c\x62uild_stacks\x18\x03 \x03(\x04\x12\x1f\n\x17\x62uild_stacks_num_hidden\x18\x04 \x03(\r\"\x95\x01\n\x0fHiddenGameState\x12\x44\n\x05stack\x18\x01 \x03(\x0b\x32\x35.solitaire.solitaire_core.HiddenGameState.HiddenStack\x1a<\n\x0bHiddenStack\x12-\n\x05\x63\x61rds\x18\x01 \x03(\x0b\x32\x1e.solitaire.solitaire_core.Card\"\x9d\x01\n\x06\x41\x63tion\x12\x32\n\x04type\x18\x01 \x01(\x0e\x32$.solitaire.solitaire_core.ActionType\x12,\n\x04suit\x18\x02 \x01(\x0e\x32\x1e.solitaire.solitaire_core.Suit\x12\x17\n\x0f\x62uild_stack_src\x18\x03 \x01(\x05\x12\x18\n\x10\x62uild_stack_dest\x18\x04 \x01(\x05\"\xa8\x01\n\nGameRecord\x12\x41\n\rinitial_state\x18\x01 \x01(\x0b\x32*.solitaire.solitaire_core.VisibleGameState\x12\x31\n\x07\x61\x63tions\x18\x02 \x03(\x0b\x32 .solitaire.solitaire_core.Action\x12\x0b\n\x03won\x18\x03 \x01(\x08\x12\x17\n\x0fwon_effectively\x18\x04 \x01(\x08*I\n\x04Suit\x12\x10\n\x0cUNKNOWN_SUIT\x10\x00\x12\t\n\x05\x43LUBS\x10\x01\x12\x0c\n\x08\x44IAMONDS\x10\x02\x12\n\n\x06HEARTS\x10\x03\x12\n\n\x06SPADES\x10\x04*\x9e\x01\n\x08\x43\x61rdRank\x12\x10\n\x0cUNKNOWN_RANK\x10\x00\x12\x07\n\x03\x41\x43\x45\x10\x01\x12\x07\n\x03TWO\x10\x02\x12\t\n\x05THREE\x10\x03\x12\x08\n\x04\x46OUR\x10\x04\x12\x08\n\x04\x46IVE\x10\x05\x12\x07\n\x03SIX\x10\x06\x12\t\n\x05SEVEN\x10\x07\x12\t\n\x05\x45IGHT\x10\x08\x12\x08\n\x04NINE\x10\t\x12\x07\n\x03TEN\x10\n\x12\x08\n\x04JACK\x10\x0b\x12\t\n\x05QUEEN\x10\x0c\x12\x08\n\x04KING\x10\r*f\n\nActionType\x12\x12\n\x0eUNKNWON_ACTION\x10\x00\x12\x0b\n\x07TO_SS_S\x10\x01\x12\x10\n\x0c\x42S_N_TO_BS_N\x10\x02\x12\x13\n\x0fTALON_S_TO_BS_N\x10\x03\x12\x10\n\x0cSS_S_TO_BS_N\x10\x04\x62\x06proto3')
)

_SUIT = _descriptor.EnumDescriptor(
  name='Suit',
  full_name='solitaire.solitaire_core.Suit',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN_SUIT', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CLUBS', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DIAMONDS', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HEARTS', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SPADES', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=743,
  serialized_end=816,
)
_sym_db.RegisterEnumDescriptor(_SUIT)

Suit = enum_type_wrapper.EnumTypeWrapper(_SUIT)
_CARDRANK = _descriptor.EnumDescriptor(
  name='CardRank',
  full_name='solitaire.solitaire_core.CardRank',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN_RANK', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TWO', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='THREE', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FOUR', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FIVE', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SIX', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SEVEN', index=7, number=7,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EIGHT', index=8, number=8,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NINE', index=9, number=9,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TEN', index=10, number=10,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='JACK', index=11, number=11,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='QUEEN', index=12, number=12,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='KING', index=13, number=13,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=819,
  serialized_end=977,
)
_sym_db.RegisterEnumDescriptor(_CARDRANK)

CardRank = enum_type_wrapper.EnumTypeWrapper(_CARDRANK)
_ACTIONTYPE = _descriptor.EnumDescriptor(
  name='ActionType',
  full_name='solitaire.solitaire_core.ActionType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNWON_ACTION', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TO_SS_S', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BS_N_TO_BS_N', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TALON_S_TO_BS_N', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SS_S_TO_BS_N', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=979,
  serialized_end=1081,
)
_sym_db.RegisterEnumDescriptor(_ACTIONTYPE)

ActionType = enum_type_wrapper.EnumTypeWrapper(_ACTIONTYPE)
UNKNOWN_SUIT = 0
CLUBS = 1
DIAMONDS = 2
HEARTS = 3
SPADES = 4
UNKNOWN_RANK = 0
ACE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6
SEVEN = 7
EIGHT = 8
NINE = 9
TEN = 10
JACK = 11
QUEEN = 12
KING = 13
UNKNWON_ACTION = 0
TO_SS_S = 1
BS_N_TO_BS_N = 2
TALON_S_TO_BS_N = 3
SS_S_TO_BS_N = 4



_CARD = _descriptor.Descriptor(
  name='Card',
  full_name='solitaire.solitaire_core.Card',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='suit', full_name='solitaire.solitaire_core.Card.suit', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rank', full_name='solitaire.solitaire_core.Card.rank', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=46,
  serialized_end=148,
)


_VISIBLEGAMESTATE = _descriptor.Descriptor(
  name='VisibleGameState',
  full_name='solitaire.solitaire_core.VisibleGameState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='talon', full_name='solitaire.solitaire_core.VisibleGameState.talon', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='suit_stack', full_name='solitaire.solitaire_core.VisibleGameState.suit_stack', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='build_stacks', full_name='solitaire.solitaire_core.VisibleGameState.build_stacks', index=2,
      number=3, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='build_stacks_num_hidden', full_name='solitaire.solitaire_core.VisibleGameState.build_stacks_num_hidden', index=3,
      number=4, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=150,
  serialized_end=258,
)


_HIDDENGAMESTATE_HIDDENSTACK = _descriptor.Descriptor(
  name='HiddenStack',
  full_name='solitaire.solitaire_core.HiddenGameState.HiddenStack',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cards', full_name='solitaire.solitaire_core.HiddenGameState.HiddenStack.cards', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=350,
  serialized_end=410,
)

_HIDDENGAMESTATE = _descriptor.Descriptor(
  name='HiddenGameState',
  full_name='solitaire.solitaire_core.HiddenGameState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='stack', full_name='solitaire.solitaire_core.HiddenGameState.stack', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_HIDDENGAMESTATE_HIDDENSTACK, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=261,
  serialized_end=410,
)


_ACTION = _descriptor.Descriptor(
  name='Action',
  full_name='solitaire.solitaire_core.Action',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='solitaire.solitaire_core.Action.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='suit', full_name='solitaire.solitaire_core.Action.suit', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='build_stack_src', full_name='solitaire.solitaire_core.Action.build_stack_src', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='build_stack_dest', full_name='solitaire.solitaire_core.Action.build_stack_dest', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=413,
  serialized_end=570,
)


_GAMERECORD = _descriptor.Descriptor(
  name='GameRecord',
  full_name='solitaire.solitaire_core.GameRecord',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='initial_state', full_name='solitaire.solitaire_core.GameRecord.initial_state', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='actions', full_name='solitaire.solitaire_core.GameRecord.actions', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='won', full_name='solitaire.solitaire_core.GameRecord.won', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='won_effectively', full_name='solitaire.solitaire_core.GameRecord.won_effectively', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=573,
  serialized_end=741,
)

_CARD.fields_by_name['suit'].enum_type = _SUIT
_CARD.fields_by_name['rank'].enum_type = _CARDRANK
_HIDDENGAMESTATE_HIDDENSTACK.fields_by_name['cards'].message_type = _CARD
_HIDDENGAMESTATE_HIDDENSTACK.containing_type = _HIDDENGAMESTATE
_HIDDENGAMESTATE.fields_by_name['stack'].message_type = _HIDDENGAMESTATE_HIDDENSTACK
_ACTION.fields_by_name['type'].enum_type = _ACTIONTYPE
_ACTION.fields_by_name['suit'].enum_type = _SUIT
_GAMERECORD.fields_by_name['initial_state'].message_type = _VISIBLEGAMESTATE
_GAMERECORD.fields_by_name['actions'].message_type = _ACTION
DESCRIPTOR.message_types_by_name['Card'] = _CARD
DESCRIPTOR.message_types_by_name['VisibleGameState'] = _VISIBLEGAMESTATE
DESCRIPTOR.message_types_by_name['HiddenGameState'] = _HIDDENGAMESTATE
DESCRIPTOR.message_types_by_name['Action'] = _ACTION
DESCRIPTOR.message_types_by_name['GameRecord'] = _GAMERECORD
DESCRIPTOR.enum_types_by_name['Suit'] = _SUIT
DESCRIPTOR.enum_types_by_name['CardRank'] = _CARDRANK
DESCRIPTOR.enum_types_by_name['ActionType'] = _ACTIONTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Card = _reflection.GeneratedProtocolMessageType('Card', (_message.Message,), dict(
  DESCRIPTOR = _CARD,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:solitaire.solitaire_core.Card)
  ))
_sym_db.RegisterMessage(Card)

VisibleGameState = _reflection.GeneratedProtocolMessageType('VisibleGameState', (_message.Message,), dict(
  DESCRIPTOR = _VISIBLEGAMESTATE,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:solitaire.solitaire_core.VisibleGameState)
  ))
_sym_db.RegisterMessage(VisibleGameState)

HiddenGameState = _reflection.GeneratedProtocolMessageType('HiddenGameState', (_message.Message,), dict(

  HiddenStack = _reflection.GeneratedProtocolMessageType('HiddenStack', (_message.Message,), dict(
    DESCRIPTOR = _HIDDENGAMESTATE_HIDDENSTACK,
    __module__ = 'game_state_pb2'
    # @@protoc_insertion_point(class_scope:solitaire.solitaire_core.HiddenGameState.HiddenStack)
    ))
  ,
  DESCRIPTOR = _HIDDENGAMESTATE,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:solitaire.solitaire_core.HiddenGameState)
  ))
_sym_db.RegisterMessage(HiddenGameState)
_sym_db.RegisterMessage(HiddenGameState.HiddenStack)

Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), dict(
  DESCRIPTOR = _ACTION,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:solitaire.solitaire_core.Action)
  ))
_sym_db.RegisterMessage(Action)

GameRecord = _reflection.GeneratedProtocolMessageType('GameRecord', (_message.Message,), dict(
  DESCRIPTOR = _GAMERECORD,
  __module__ = 'game_state_pb2'
  # @@protoc_insertion_point(class_scope:solitaire.solitaire_core.GameRecord)
  ))
_sym_db.RegisterMessage(GameRecord)


# @@protoc_insertion_point(module_scope)
