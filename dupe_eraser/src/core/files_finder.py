from dupe_eraser.src.core.files_eraser import remove_doublons
from dupe_eraser.src.core.hashing_algorithms import check_hashing_algorithm_supported
from path import Path


def erase_doublons(*, main_directory: Path, hashing_algorithm: str):
    files_to_examine = [file for file in main_directory.walkfiles()]
    while files_to_examine:
        file = files_to_examine.pop(0)
        files_to_examine = find_doublons(file, files_to_examine)


def find_doublons(file, list_files):
    file_hash = file.read_hexhash(HASHING_ALGORITHM)

    index_to_remove = list()
    for index, possible_doublon in enumerate(list_files):
        if possible_doublon.read_hexhash(HASHING_ALGORITHM) == file_hash:
            index_to_remove.append(index)

    return remove_doublons(list_files, index_to_remove)