import os
import sys

from pathlib import Path

import click

# from dupe_eraser.src.core.files_finder import get_files_to_examine, computing_hashes, look_for_dupe
from src.core.files_finder import get_files_to_examine, computing_hashes, look_for_dupe

# TODO: Parametize progress_bar
# TODO: Memory_consumption safe
# TODO: Batch-size of files to inspect
# TODO: Put all files to move into an array who can be traited by an extern process


_MAX_TEXT_OUTPUT_WIDTH = 120


@click.command(context_settings=dict(max_content_width=_MAX_TEXT_OUTPUT_WIDTH))
@click.option("-p", "--path-dir", type=str, default=".", show_default=True,
              help="Path of the directory where to look for duplicate files.")
@click.option("-b", "--behavior", type=click.Choice(["c", "d", "s"]), default="c", show_default=True,
              help="Behavior to adopt when encountering a duplicate file. Possible values are :\n"
                   "- c: for 'checking', print the path of the duplicates without deleting or moving anything.\n"
                   "- d: for 'delete', delete one of the duplicate file.\n"
                   "- s: for 'safe', move one of the duplicate file in the safe directory.")
@click.option("-r", "--recursive", is_flag=True,
              help="Look also for duplicates in the sub directories of your current directory.")
@click.option("-S", "--safe-directory", type=str, default="_safe_directory", show_default=True,
              help="The name of the directory used during safe mode.")
@click.option("-H", "--hashing-algorithm", type=str, default="sha512", show_default=True,
              help="The hashing algorithm used to compare hashes between files.")
@click.option("--quiet", is_flag=True,
              help="Set this flag if you want to completely silence all outputs to stdout.")
@click.option("--disable-progress-bar", is_flag=True,
              help="Set this flag if you want to completely disable the progress bar.")
def main(path_dir, behavior, recursive, safe_directory, hashing_algorithm, quiet, disable_progress_bar):
    parameters = locals()

    if quiet:
        sys.stdout = open(os.devnull, 'w')

    path_dir = Path(path_dir)
    safe_directory = Path(safe_directory).absolute()

    files_to_examine = get_files_to_examine(path_dir, recursive, safe_directory)
    hashes = computing_hashes(files_to_examine, hashing_algorithm, disable_progress_bar)
    look_for_dupe(files_to_examine, hashes, behavior, safe_directory, disable_progress_bar)


if __name__ == "__main__":
    main()
