# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import EnumDescriptor as google___protobuf___descriptor___EnumDescriptor

from google.protobuf.internal.containers import (
    RepeatedCompositeFieldContainer as google___protobuf___internal___containers___RepeatedCompositeFieldContainer,
    RepeatedScalarFieldContainer as google___protobuf___internal___containers___RepeatedScalarFieldContainer,
)

from google.protobuf.message import Message as google___protobuf___message___Message

from typing import (
    Iterable as typing___Iterable,
    List as typing___List,
    Optional as typing___Optional,
    Tuple as typing___Tuple,
    cast as typing___cast,
)

from typing_extensions import Literal as typing_extensions___Literal

class Suit(int):
    DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
    @classmethod
    def Name(cls, number: int) -> str: ...
    @classmethod
    def Value(cls, name: str) -> Suit: ...
    @classmethod
    def keys(cls) -> typing___List[str]: ...
    @classmethod
    def values(cls) -> typing___List[Suit]: ...
    @classmethod
    def items(cls) -> typing___List[typing___Tuple[str, Suit]]: ...

UNKNOWN_SUIT = typing___cast(Suit, 0)
CLUBS = typing___cast(Suit, 1)
DIAMONDS = typing___cast(Suit, 2)
HEARTS = typing___cast(Suit, 3)
SPADES = typing___cast(Suit, 4)

class CardRank(int):
    DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
    @classmethod
    def Name(cls, number: int) -> str: ...
    @classmethod
    def Value(cls, name: str) -> CardRank: ...
    @classmethod
    def keys(cls) -> typing___List[str]: ...
    @classmethod
    def values(cls) -> typing___List[CardRank]: ...
    @classmethod
    def items(cls) -> typing___List[typing___Tuple[str, CardRank]]: ...

UNKNOWN_RANK = typing___cast(CardRank, 0)
ACE = typing___cast(CardRank, 1)
TWO = typing___cast(CardRank, 2)
THREE = typing___cast(CardRank, 3)
FOUR = typing___cast(CardRank, 4)
FIVE = typing___cast(CardRank, 5)
SIX = typing___cast(CardRank, 6)
SEVEN = typing___cast(CardRank, 7)
EIGHT = typing___cast(CardRank, 8)
NINE = typing___cast(CardRank, 9)
TEN = typing___cast(CardRank, 10)
JACK = typing___cast(CardRank, 11)
QUEEN = typing___cast(CardRank, 12)
KING = typing___cast(CardRank, 13)

class ActionType(int):
    DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
    @classmethod
    def Name(cls, number: int) -> str: ...
    @classmethod
    def Value(cls, name: str) -> ActionType: ...
    @classmethod
    def keys(cls) -> typing___List[str]: ...
    @classmethod
    def values(cls) -> typing___List[ActionType]: ...
    @classmethod
    def items(cls) -> typing___List[typing___Tuple[str, ActionType]]: ...

UNKNWON_ACTION = typing___cast(ActionType, 0)
TO_SS_S = typing___cast(ActionType, 1)
BS_N_TO_BS_N = typing___cast(ActionType, 2)
TALON_S_TO_BS_N = typing___cast(ActionType, 3)
SS_S_TO_BS_N = typing___cast(ActionType, 4)

class Card(google___protobuf___message___Message):
    suit = ...  # type: Suit
    rank = ...  # type: CardRank
    def __init__(
        self, suit: typing___Optional[Suit] = None, rank: typing___Optional[CardRank] = None
    ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> Card: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"rank", u"suit"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"rank", b"suit"]) -> None: ...

class VisibleGameState(google___protobuf___message___Message):
    talon = ...  # type: int
    suit_stack = ...  # type: int
    build_stacks = ...  # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[int]
    build_stacks_num_hidden = (
        ...
    )  # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[int]
    def __init__(
        self,
        talon: typing___Optional[int] = None,
        suit_stack: typing___Optional[int] = None,
        build_stacks: typing___Optional[typing___Iterable[int]] = None,
        build_stacks_num_hidden: typing___Optional[typing___Iterable[int]] = None,
    ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> VisibleGameState: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(
            self,
            field_name: typing_extensions___Literal[
                u"build_stacks", u"build_stacks_num_hidden", u"suit_stack", u"talon"
            ],
        ) -> None: ...
    else:
        def ClearField(
            self,
            field_name: typing_extensions___Literal[
                b"build_stacks", b"build_stacks_num_hidden", b"suit_stack", b"talon"
            ],
        ) -> None: ...

class HiddenGameState(google___protobuf___message___Message):
    class HiddenStack(google___protobuf___message___Message):
        @property
        def cards(
            self
        ) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[Card]: ...
        def __init__(self, cards: typing___Optional[typing___Iterable[Card]] = None) -> None: ...
        @classmethod
        def FromString(cls, s: bytes) -> HiddenGameState.HiddenStack: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        if sys.version_info >= (3,):
            def ClearField(self, field_name: typing_extensions___Literal[u"cards"]) -> None: ...
        else:
            def ClearField(self, field_name: typing_extensions___Literal[b"cards"]) -> None: ...
    @property
    def stack(
        self
    ) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[
        HiddenGameState.HiddenStack
    ]: ...
    def __init__(
        self, stack: typing___Optional[typing___Iterable[HiddenGameState.HiddenStack]] = None
    ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> HiddenGameState: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(self, field_name: typing_extensions___Literal[u"stack"]) -> None: ...
    else:
        def ClearField(self, field_name: typing_extensions___Literal[b"stack"]) -> None: ...

class Action(google___protobuf___message___Message):
    type = ...  # type: ActionType
    suit = ...  # type: Suit
    build_stack_src = ...  # type: int
    build_stack_dest = ...  # type: int
    def __init__(
        self,
        type: typing___Optional[ActionType] = None,
        suit: typing___Optional[Suit] = None,
        build_stack_src: typing___Optional[int] = None,
        build_stack_dest: typing___Optional[int] = None,
    ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> Action: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def ClearField(
            self,
            field_name: typing_extensions___Literal[
                u"build_stack_dest", u"build_stack_src", u"suit", u"type"
            ],
        ) -> None: ...
    else:
        def ClearField(
            self,
            field_name: typing_extensions___Literal[
                b"build_stack_dest", b"build_stack_src", b"suit", b"type"
            ],
        ) -> None: ...

class GameRecord(google___protobuf___message___Message):
    won = ...  # type: bool
    won_effectively = ...  # type: bool
    @property
    def initial_state(self) -> VisibleGameState: ...
    @property
    def actions(
        self
    ) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[Action]: ...
    def __init__(
        self,
        initial_state: typing___Optional[VisibleGameState] = None,
        actions: typing___Optional[typing___Iterable[Action]] = None,
        won: typing___Optional[bool] = None,
        won_effectively: typing___Optional[bool] = None,
    ) -> None: ...
    @classmethod
    def FromString(cls, s: bytes) -> GameRecord: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    if sys.version_info >= (3,):
        def HasField(self, field_name: typing_extensions___Literal[u"initial_state"]) -> bool: ...
        def ClearField(
            self,
            field_name: typing_extensions___Literal[u"actions", u"initial_state", u"won", u"won_effectively"],
        ) -> None: ...
    else:
        def HasField(
            self, field_name: typing_extensions___Literal[u"initial_state", b"initial_state"]
        ) -> bool: ...
        def ClearField(
            self,
            field_name: typing_extensions___Literal[b"actions", b"initial_state", b"won", b"won_effectively"],
        ) -> None: ...
