import json
import os


_PATH_PARAMS_NAMES = "../../res/parameters_names.json"


def _get_name_from_file(value):
    path = os.path.join(os.path.dirname(__file__),
                        _PATH_PARAMS_NAMES)
    with open(path) as file:
        return json.load(file)[value]


def help_message() -> str:
    return _get_name_from_file("help")


def version() -> str:
    return _get_name_from_file("version")


def recursive() -> str:
    return _get_name_from_file("recursive")


def safe() -> str:
    return _get_name_from_file("safe")


def safe_directory() -> str:
    return _get_name_from_file("safe_directory")


def check() -> str:
    return _get_name_from_file("check")


def verbosity() -> str:
    return _get_name_from_file("verbosity")


def low_memory() -> str:
    return _get_name_from_file("low_memory")


def hashing_algorithm() -> str:
    return _get_name_from_file("hashing_algorithm")


if __name__ == '__main__':
    pass
