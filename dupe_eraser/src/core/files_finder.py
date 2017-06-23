from dupe_eraser.src.core.files_eraser import remove_doublons
from dupe_eraser.src.getters.get_output_message import vprint, Message
from path import Path
from typing import List
import itertools


def erase_doublons(*, main_directory: Path, hashing_algorithm: str, recursive: bool, safe_mode: bool, check_mode: bool,
                   safe_directory: Path) -> None:
    if recursive:
        files_to_examine = []
        for directory in main_directory.walkdirs():
            if directory.name != safe_directory.name:
                for file in directory.files():
                    files_to_examine.append(file)
        for file in main_directory.files():
            files_to_examine.append(file)
    else:
        files_to_examine = [file for file in main_directory.files()]

    while files_to_examine:
        file = files_to_examine.pop(0)
        vprint(Message.EXAMINING_FILE, file=file.realpath())
        files_to_examine = _find_doublons(original_file=file,
                                          other_files=files_to_examine,
                                          hashing_algorithm=hashing_algorithm,
                                          safe_mode=safe_mode,
                                          check_mode=check_mode,
                                          safe_directory=safe_directory)


def _find_doublons(original_file: Path, other_files: List[Path], hashing_algorithm: str, safe_mode: bool,
                   check_mode: bool, safe_directory: Path) -> List[Path]:
    file_hash = original_file.read_hexhash(hashing_algorithm)

    index_to_remove = list()
    for index, possible_doublon in enumerate(other_files):
        if possible_doublon.read_hexhash(hashing_algorithm) == file_hash:
            index_to_remove.append(index)

    return remove_doublons(list_files=other_files,
                           index_to_remove=index_to_remove,
                           safe_mode=safe_mode,
                           check_mode=check_mode,
                           safe_directory=safe_directory)
