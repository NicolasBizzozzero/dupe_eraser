from dupe_eraser.src.core.initialization.args_parser import \
    parse_args_main_entry_point
import dupe_eraser.src.getters.environment as env
from dupe_eraser.src.core.files_finder import dupe_eraser
from path import Path
from dupe_eraser.src.getters.get_output_message import Verbosity


def main_entry_point():
    parse_args_main_entry_point()
    dupe_eraser(main_directory=Path.getcwd(),
                hashing_algorithm=env.hashing_algorithm,
                recursive=env.recursive,
                safe_mode=env.safe,
                check_mode=env.check,
                safe_directory=env.safe_directory,
                progress_bar=env.verbosity == Verbosity.PROGRESS_BAR)


if __name__ == "__main__":
    pass
