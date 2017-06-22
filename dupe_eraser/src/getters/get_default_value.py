import json
import os


_PATH_DEFAULT_VALUES = "../../res/default_values.json"


def _get_value_from_file(value):
    path = os.path.join(os.path.dirname(__file__),
                        _PATH_DEFAULT_VALUES)
    with open(path) as file:
        return json.load(file)[value]


def safe_directory() -> float:
    return _get_value_from_file("safe_directory")


def verbosity() -> float:
    return _get_value_from_file("verbosity")


if __name__ == '__main__':
    pass
