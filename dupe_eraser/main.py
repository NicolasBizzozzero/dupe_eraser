from path import Path

from dupe_eraser.src.core.files_finder import find_doublons
from dupe_eraser.src.core.initialization.args_parser import parse_args_main_entry_point
import dupe_eraser.src.getters.environment as env


def main_entry_point():
    """
        here = Path.getcwd()
        files = [file for file in here.walkfiles()]
        while files:
            file = files.pop(0)
            files = find_doublons(file, files)
    """
    parse_args_main_entry_point()
    print(env.args)


def main():
    pass


if __name__ == "__main__":
    main_entry_point()
