import os
import sys
import shutil

from pathlib import Path
from typing import List, Dict

from tqdm import tqdm

from dupe_eraser.hashing import compute_hash
from dupe_eraser.perceptual_hashing import compute_perceptual_hash
from dupe_eraser.utils import is_picture

_FORMAT_PROGRESS_BAR_HASHES = r"Hashing: {n_fmt}/{total_fmt} files, elapsed:{elapsed}, ETA:{remaining}{postfix}"
_FORMAT_PROGRESS_BAR_PHASHES = r"Perceptual hashing: {n_fmt}/{total_fmt} files, elapsed:{elapsed}, ETA:{remaining}{postfix}"
_FORMAT_PROGRESS_BAR_FINDING = r"Looking for dupe: {n_fmt}/{total_fmt} files, elapsed:{elapsed}, ETA:{remaining}{postfix}"


def get_files_to_examine(*, path_dir: Path, recursive: bool, safe_directory: Path) -> List[Path]:
    """ Retrieve a list of files from which to compute examine if it includes any dupe. """
    if recursive:
        return [path for path in Path(path_dir).rglob("*") if (path.is_file() and path != safe_directory)]
    else:
        return [path for path in path_dir.iterdir() if path.is_file()]


def computing_hashes(*, files_to_examine: List[Path], hashing_algorithm: str,
                     disable_progress_bar: bool) -> Dict[str, str]:
    """ Compute the hashes of all files. Returns a dictionary of paths linked to their given hash. """
    hashes = dict()
    with tqdm(bar_format=_FORMAT_PROGRESS_BAR_HASHES, total=len(files_to_examine),
              file=open(os.devnull, 'w') if disable_progress_bar else sys.stderr) as progress_bar:
        for file in files_to_examine:
            hashes[file.as_posix()] = compute_hash(file, hashing_algorithm)
            progress_bar.update()
    return hashes


def computing_perceptual_hashes(*, files_to_examine: List[Path], hashing_algorithm: str,
                                disable_progress_bar: bool) -> Dict[str, str]:
    """ Compute the perceptual hashes of all files. Returns a dictionary of paths linked to their given hash. """
    hashes = dict()
    with tqdm(bar_format=_FORMAT_PROGRESS_BAR_PHASHES, total=len(files_to_examine),
              file=open(os.devnull, 'w') if disable_progress_bar else sys.stderr) as progress_bar:
        for file in files_to_examine:
            if is_picture(file.as_posix()):
                hashes[file.as_posix()] = compute_perceptual_hash(file, hashing_algorithm)
            progress_bar.update()
    return hashes


def look_for_dupe(files_to_examine: List[Path], hashes: Dict[str, str], perceptual_hashes: Dict[str, str],
                  behavior: str, shallow: bool, safe_directory: Path, disable_progress_bar: bool) -> None:
    """ Given a dictionary of hashes, check if there is any duplicates in them, and act appropriately following a proper
    behavior.
    """
    n_of_files = len(files_to_examine)

    with tqdm(bar_format=_FORMAT_PROGRESS_BAR_FINDING, total=n_of_files,
              file=open(os.devnull, 'w') if disable_progress_bar else sys.stderr) as progress_bar:
        while len(files_to_examine) != 0:
            file = files_to_examine.pop(0).as_posix()
            n_files_removed = _find_doublons(original_file=file,
                                             other_files=files_to_examine,
                                             hashes=hashes,
                                             perceptual_hashes=perceptual_hashes,
                                             behavior=behavior,
                                             shallow=shallow,
                                             safe_directory=safe_directory)
            progress_bar.update(n_files_removed + 1)
    progress_bar.fp.close()


def _find_doublons(original_file: str, other_files: List[Path], hashes: Dict[str, str],
                   perceptual_hashes: Dict[str, str], behavior: str, shallow: bool, safe_directory: Path) -> int:
    file_hash = hashes[original_file]
    file_phash = perceptual_hashes[original_file]
    index_to_remove = list()
    for index, possible_doublon in enumerate(other_files):
        if hashes[possible_doublon.as_posix()] == file_hash:
            # File may be a duplicate, compares it shallowly to be sure
            if shallow:
                if _file_comparison_shallow(original_file, possible_doublon.as_posix()):
                    # Files contains exactly the same content
                    index_to_remove.append(index)
                else:
                    # Check if the perceptual hashes of the files are the same
                    if (perceptual_hashes is not None) and is_picture(possible_doublon.as_posix()):
                        if perceptual_hashes[possible_doublon.as_posix()] == file_phash:
                            index_to_remove.append(index)
                        else:
                            pass
                    else:
                        pass
            else:
                index_to_remove.append(index)
        else:
            # Check if the perceptual hashes of the files are the same
            if (perceptual_hashes is not None) and is_picture(possible_doublon.as_posix()):
                if perceptual_hashes[possible_doublon.as_posix()] == file_phash:
                    index_to_remove.append(index)
                else:
                    pass
            else:
                pass

    n_files_removed = len(index_to_remove)
    _remove_doublons(list_files=other_files,
                     index_to_remove=index_to_remove,
                     behavior=behavior,
                     safe_directory=safe_directory)
    return n_files_removed


def _remove_doublons(list_files: List[Path], index_to_remove: List[int], behavior: str,
                     safe_directory: Path) -> None:
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


def _file_comparison_shallow(file1: str, file2: str, buffer_size: int = 8192) -> bool:
    """ Perform a shallow comparison (by looking at the content) of two files by chunk of  buffer_size .
    Returns True if the two files are equals, False otherwise.
    """
    with open(file1, 'rb') as fp1, open(file2, 'rb') as fp2:
        while True:
            b1 = fp1.read(buffer_size)
            b2 = fp2.read(buffer_size)
            if b1 != b2:
                return False
            if (not b1) or (not b2):
                return True


if __name__ == "__main__":
    pass
