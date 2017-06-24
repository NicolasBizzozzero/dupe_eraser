from dupe_eraser.src.core.files_eraser import remove_doublons
from dupe_eraser.src.getters.get_output_message import vprint, Message, vget
from path import Path
from typing import List, Dict
import progressbar


def dupe_eraser(*, main_directory: Path, hashing_algorithm: str,
                recursive: bool, safe_mode: bool, check_mode: bool,
                safe_directory: Path, progress_bar: bool) -> None:
    if progress_bar:
        files_to_examine = _get_files_to_examine_pb(main_directory, recursive, safe_directory)
        hashes = _computing_hashes_pb(files_to_examine, hashing_algorithm)
        _init_finding_pb(files_to_examine, hashes, safe_mode, check_mode, safe_directory)
    else:
        files_to_examine = _get_files_to_examine(main_directory, recursive, safe_directory)
        hashes = _computing_hashes(files_to_examine, hashing_algorithm)
        _init_finding(files_to_examine, hashes, safe_mode, check_mode, safe_directory)


def _get_files_to_examine(main_directory: Path, recursive: bool, safe_directory: Path) -> List[Path]:
    if recursive:
        files_to_examine = []
        for directory in main_directory.walkdirs():
            if directory.name != safe_directory.name:
                for file in directory.files():
                    files_to_examine.append(file)
        for file in main_directory.files():
            files_to_examine.append(file)
        return files_to_examine
    else:
        return [file for file in main_directory.files()]


def _get_files_to_examine_pb(main_directory: Path, recursive: bool, safe_directory: Path) -> List[Path]:
    widgets = [progressbar.FormatLabel(vget(Message.STORING_FILES)), ' ',
               progressbar.Percentage(), ' ',
               progressbar.Bar('='), ' ',
               progressbar.ETA()]

    if recursive:
        currentval = 0
        bar = progressbar.ProgressBar(widgets=widgets, maxval=progressbar.UnknownLength).start()
        files_to_examine = []
        for directory in main_directory.walkdirs():
            if directory.name != safe_directory.name:
                for file in directory.files():
                    files_to_examine.append(file)
                    currentval += 1
                    bar.update(currentval)
        for file in main_directory.files():
            files_to_examine.append(file)
            currentval += 1
            bar.update(currentval)
        bar.finish()
        return files_to_examine
    else:
        maxval = len(main_directory.files())
        bar = progressbar.ProgressBar(widgets=widgets, maxval=maxval)
        files_to_examine = [file for file in bar(main_directory.files())]
        return files_to_examine


def _computing_hashes(files_to_examine: List[Path], hashing_algorithm: str) -> Dict[Path, str]:
    hashes = dict()
    for file in files_to_examine:
        hashes[file] = file.read_hexhash(hashing_algorithm)
    return hashes


def _computing_hashes_pb(files_to_examine: List[Path], hashing_algorithm: str) -> Dict[Path, str]:
    widgets = [progressbar.FormatLabel(vget(Message.COMPUTE_HASHES)), ' ',
               progressbar.Percentage(), ' ',
               progressbar.Bar('='), ' ',
               progressbar.ETA()]
    maxval = len(files_to_examine)
    bar = progressbar.ProgressBar(widgets=widgets, maxval=maxval)

    hashes = dict()
    for file in bar(files_to_examine):
        hashes[file] = file.read_hexhash(hashing_algorithm)
    return hashes


def _init_finding(files_to_examine: List[Path], hashes: Dict[Path, str],
                  safe_mode: bool, check_mode: bool,
                  safe_directory: Path) -> None:

    while files_to_examine:
        file = files_to_examine.pop(0)
        vprint(Message.EXAMINING_FILE, file=file.realpath())
        files_to_examine = _find_doublons(original_file=file,
                                          other_files=files_to_examine,
                                          hashes=hashes,
                                          safe_mode=safe_mode,
                                          check_mode=check_mode,
                                          safe_directory=safe_directory)


def _init_finding_pb(files_to_examine: List[Path], hashes: Dict[Path, str],
                               safe_mode: bool, check_mode: bool,
                               safe_directory: Path) -> None:
    widgets = [progressbar.FormatLabel(vget(Message.EXAMINING_FILES)), ' ',
               progressbar.Percentage(), ' ',
               progressbar.Bar('='), ' ',
               progressbar.ETA()]

    maxval = len(files_to_examine)
    bar = progressbar.ProgressBar(widgets=widgets, maxval=maxval).start()
    while files_to_examine:
        file = files_to_examine.pop(0)
        vprint(Message.EXAMINING_FILE, file=file.realpath())
        files_to_examine = _find_doublons(original_file=file,
                                          other_files=files_to_examine,
                                          hashes=hashes,
                                          safe_mode=safe_mode,
                                          check_mode=check_mode,
                                          safe_directory=safe_directory)
        bar.update(maxval - len(files_to_examine))
    bar.finish()


def _find_doublons(original_file: Path, other_files: List[Path],
                   hashes: Dict[Path, str], safe_mode: bool, check_mode: bool,
                   safe_directory: Path) -> List[Path]:
    file_hash = hashes[original_file]
    index_to_remove = list()
    for index, possible_doublon in enumerate(other_files):
        if hashes[possible_doublon] == file_hash:
            index_to_remove.append(index)

    return remove_doublons(list_files=other_files,
                           index_to_remove=index_to_remove,
                           safe_mode=safe_mode,
                           check_mode=check_mode,
                           safe_directory=safe_directory)
