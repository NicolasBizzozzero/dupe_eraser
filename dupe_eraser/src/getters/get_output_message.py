import json
import os
from enum import IntEnum, Enum

import dupe_eraser.src.getters.environment as env


_PATH_OUTPUT_MESSAGES = "../../res/default_values.json"
VERBOSE_KEY_PREFIX = "verbose_"


class Verbosity(IntEnum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


class UnknownVerbosity(Exception):
    def __init__(self, verbosity):
        Exception.__init__(self, "The verbosity level \"{verbosity}\" is unknown "
                                 "to the software.".format(verbosity=verbosity))


class Message(Enum):
    DELETING_FILE = "deleting_file"
    MOVING_FILE = "moving_file"

    def __str__(self):
        return _content_if_printable(self.value)


def _content_if_printable(message_key: str):
    if env.verbosity == Verbosity.QUIET:
        return None
    elif env.verbosity == Verbosity.NORMAL:
        if _is_a_normal_message(message_key):
            return _get_message_from_file(message_key)
    elif env.verbosity == Verbosity.VERBOSE:
        return _get_message_from_file(message_key)
    else:
        raise UnknownVerbosity(env.verbosity)


def _is_a_normal_message(message_key: str) -> bool:
    global VERBOSE_KEY_PREFIX

    return message_key[:len(VERBOSE_KEY_PREFIX)] != VERBOSE_KEY_PREFIX


def _get_message_from_file(value):
    global _PATH_OUTPUT_MESSAGES

    path = os.path.join(os.path.dirname(__file__),
                        _PATH_OUTPUT_MESSAGES)
    with open(path) as file:
        return json.load(file)[value]


def vprint(message: Message) -> None:
    print(message, end="", sep="")


if __name__ == '__main__':
    pass
