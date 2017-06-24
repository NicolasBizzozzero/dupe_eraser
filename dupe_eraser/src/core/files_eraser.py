from path import Path
from typing import List
from dupe_eraser.src.getters.get_output_message import Message, vprint
import shutil


def remove_doublons(list_files: List[Path], index_to_remove: List[int],
                    safe_mode: bool, check_mode: bool,
                    safe_directory: Path) -> List[Path]:
    # If we remove indexes from the highest to the lowest, we don't have to
    # increment each index at each removal
    for index in reversed(index_to_remove):
        file = list_files.pop(index)

        if safe_mode:
            vprint(Message.MOVING_FILE, file=file.realpath())
            Path.mkdir_p(Path(safe_directory))
            while True:
                try:
                    Path.move(file, Path(safe_directory))
                    break
                except shutil.Error:
                    file = Path(file.parent) / Path("copy_" + file.name)
        elif check_mode:
            vprint(Message.CHECKING_FILE, file=file.realpath())
        else:
            vprint(Message.DELETING_FILE, file=file.realpath())
            file.remove()

    return list_files
