# from dupe_eraser.src.core.files_eraser import remove_doublons
import os
import sys
import shutil

from pathlib import Path
from typing import List, Dict

from tqdm import tqdm

# from dupe_eraser.src.core.hashing_algorithms import compute_hash
from src.core.hashing_algorithms import compute_hash

_FORMAT_PROGRESS_BAR_HASHES = r"Hashing: {n_fmt}/{total_fmt} files, elapsed:{elapsed}, ETA:{remaining}{postfix}"
_FORMAT_PROGRESS_BAR_FINDING = r"Looking for dupe: {n_fmt}/{total_fmt} files, elapsed:{elapsed}, ETA:{remaining}{postfix}"


def get_files_to_examine(path_dir: Path, recursive: bool, safe_directory: Path) -> List[Path]:
    if recursive:
        return [path for path in Path(path_dir).rglob("*") if (path.is_file() and path != safe_directory)]
    else:
        return [path for path in path_dir.iterdir() if path.is_file()]


def computing_hashes(files_to_examine: List[Path], hashing_algorithm: str,
                     disable_progress_bar: bool) -> Dict[str, str]:
    hashes = dict()
    with tqdm(bar_format=_FORMAT_PROGRESS_BAR_HASHES, total=len(files_to_examine),
              file=open(os.devnull, 'w') if disable_progress_bar else sys.stderr) as progress_bar:
        for file in files_to_examine:
            hashes[file.as_posix()] = compute_hash(file, hashing_algorithm)
            progress_bar.update()
    return hashes


def look_for_dupe(files_to_examine: List[str], hashes: Dict[str, str], behavior: str, safe_directory: Path,
                  disable_progress_bar: bool) -> None:
    n_of_files = len(files_to_examine)

    with tqdm(bar_format=_FORMAT_PROGRESS_BAR_FINDING, total=n_of_files,
              file=open(os.devnull, 'w') if disable_progress_bar else sys.stderr) as progress_bar:
        while len(files_to_examine) != 0:
            file = files_to_examine.pop(0).as_posix()
            n_files_removed = _find_doublons(original_file=file,
                                             other_files=files_to_examine,
                                             hashes=hashes,
                                             behavior=behavior,
                                             safe_directory=safe_directory)
            progress_bar.update(n_files_removed + 1)
    progress_bar.fp.close()


def _find_doublons(original_file: str, other_files: List[str],
                   hashes: Dict[str, str], behavior: str, safe_directory: Path) -> List[str]:
    file_hash = hashes[original_file]
    index_to_remove = list()
    for index, possible_doublon in enumerate(other_files):
        if hashes[possible_doublon.as_posix()] == file_hash:
            index_to_remove.append(index)

    n_files_removed = len(index_to_remove)
    _remove_doublons(list_files=other_files,
                     index_to_remove=index_to_remove,
                     behavior=behavior,
                     safe_directory=safe_directory)
    return n_files_removed


def _remove_doublons(list_files: List[str], index_to_remove: List[int],
                     behavior: str, safe_directory: Path) -> List[str]:
    # If we remove indexes from the highest to the lowest, we don't have to
    # increment each index at each removal
    for index in reversed(index_to_remove):
        file = list_files.pop(index)

        if behavior == "s":
            tqdm.write("Moving file : \"{file}\" into the safe directory".format(file=file))
            os.makedirs(safe_directory.absolute().as_posix(), exist_ok=True)
            while True:
                try:
                    shutil.copy(file, os.path.join(safe_directory.absolute().as_posix()))
                    os.remove(file)
                    break
                except shutil.Error:
                    file = Path(file.parent) / Path(file).stemad + "_copy" + Path(file).suffix
        elif behavior == "c":
            tqdm.write("File : \"{file}\" is a duplicate".format(file=file))
        elif behavior == "d":
            tqdm.write("Deleting file : \"{file}\"".format(file=file))
            Path(file).unlink()
        else:
            print("Unknown behavior :", behavior, file=sys.stderr)
            exit(2)


if __name__ == "__main__":
    pass
