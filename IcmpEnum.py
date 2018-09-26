from enum import Enum


class IcmpEnum(Enum):
    ECHO_REPLY = 0
    DESTINATION_UNREACHABLE = 3
    ECHO_REQUEST = 8
    TIME_EXCEEDED = 11
