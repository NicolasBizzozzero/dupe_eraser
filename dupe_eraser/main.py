from dupe_eraser.src.core.initialization.args_parser import parse_args_main_entry_point
from dupe_eraser.src.getters.get_output_message import vprint, Message
from dupe_eraser.src.core.files_finder import erase_doublons
from path import Path


def main_entry_point():
    parse_args_main_entry_point()

    erase_doublons(main_directory=Path.getcwd())

    vprint(Message.GOODBYE_MESSAGE)


if __name__ == "__main__":
    pass
