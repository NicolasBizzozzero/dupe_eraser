import json
import os
from enum import IntEnum, Enum

import dupe_eraser.src.getters.environment as env


_PATH_OUTPUT_MESSAGES = "../../res/output_messages.json"
VERBOSE_KEY_PREFIX = "verbose_"
LABEL_KEY_PREFIX = "label_"


class Verbosity(IntEnum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    PROGRESS_BAR = 3


def string_to_verbosity(string: str) -> Verbosity:
    string = string.lower()
    if string == "quiet":
        return Verbosity.QUIET
    elif string == "normal":
        return Verbosity.NORMAL
    elif string == "verbose":
        return Verbosity.VERBOSE
    elif string == "progressbar":
        return Verbosity.PROGRESS_BAR
    else:
        raise UnknownVerbosity(string)


class UnknownVerbosity(Exception):
    def __init__(self, verbosity):
        Exception.__init__(self, "The verbosity level \"{verbosity}\""
                                 " is unknown to the "
                                 "software.".format(verbosity=verbosity))


class Message(Enum):
    # Verbose messages
    WELCOME_MESSAGE = VERBOSE_KEY_PREFIX + "welcome_message"
    GOODBYE_MESSAGE = VERBOSE_KEY_PREFIX + "goodbye_message"
    PARSING_ARGUMENTS = VERBOSE_KEY_PREFIX + "parsing_arguments"
    CLEANING_ARGUMENTS = VERBOSE_KEY_PREFIX + "cleaning_arguments"
    EXAMINING_FILE = VERBOSE_KEY_PREFIX + "examining_file"
    VERBOSE_DELETING_FILE = VERBOSE_KEY_PREFIX + "deleting_file"
    VERBOSE_MOVING_FILE = VERBOSE_KEY_PREFIX + "moving_file"
    VERBOSE_CHECKING_FILE = VERBOSE_KEY_PREFIX + "checking_file"

    # Normal messages
    DELETING_FILE = "deleting_file"
    MOVING_FILE = "moving_file"
    CHECKING_FILE = "checking_file"

    # Labels
    STORING_FILES = LABEL_KEY_PREFIX + "storing_files"
    COMPUTE_HASHES = LABEL_KEY_PREFIX + "compute_hashes"
    EXAMINING_FILES = LABEL_KEY_PREFIX + "examining_files"

    @staticmethod
    def contains(value):
        for m in Message:
            if m.value == value:
                return True
        return False


def _is_a_normal_message(message_key: str) -> bool:
    global VERBOSE_KEY_PREFIX

    return message_key[:len(VERBOSE_KEY_PREFIX)] != VERBOSE_KEY_PREFIX


def _get_message_from_file(value):
    global _PATH_OUTPUT_MESSAGES

    path = os.path.join(os.path.dirname(__file__),
                        _PATH_OUTPUT_MESSAGES)
    with open(path) as file:
        return json.load(file)[value]


def vprint(message: Message, **kwargs) -> None:
    message_key = message.value

    if env.verbosity == Verbosity.QUIET:
        return None
    elif env.verbosity == Verbosity.NORMAL:
        if _is_a_normal_message(message_key):
            message = _get_message_from_file(message_key)
        else:
            message = ""
    elif env.verbosity == Verbosity.VERBOSE:
        # Overwrite the same messages with their verbose version
        if Message.contains(VERBOSE_KEY_PREFIX + message_key):
            message = _get_message_from_file(VERBOSE_KEY_PREFIX + message_key)
        else:
            message = _get_message_from_file(message_key)
    elif env.verbosity == Verbosity.PROGRESS_BAR:
        return None
    else:
        raise UnknownVerbosity(env.verbosity)

    print(message.format(**kwargs), end="", sep="")


def vget(message: Message) -> str:
    if env.verbosity != Verbosity.PROGRESS_BAR:
        return ""

    message_key = message.value
    return _get_message_from_file(message_key)


if __name__ == '__main__':
    pass
