import os
import sys
import argparse

from pathlib import Path

from dupe_eraser.core import get_files_to_examine, computing_hashes, look_for_dupe, computing_perceptual_hashes


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("path_dir", type=str, default=".",
                        help='Path of the directory from where to look for duplicate files')
    parser.add_argument("-b", "--behavior", choices=["c", "d", "s"], default="c",
                        help="Behavior to adopt when encountering a duplicate file. Possible values are :\n"
                             "- c: for 'checking', print the path of the duplicates without deleting or moving "
                             "anything.\n"
                             "- d: for 'delete', delete one of the duplicate file.\n"
                             "- s: for 'safe', move one of the duplicate file in the safe directory.")
    parser.add_argument("-r", "--recursive", action='store_true',
                        help='Look also for duplicates in the sub directories of your current directory')
    parser.add_argument("-s", "--shallow", action='store_true',
                        help='If two files have the same hash, perform a shallow comparison before acting on them.')
    parser.add_argument("-S", "--safe-directory", type=str, default="_safe_directory",
                        help="The name of the directory used during safe mode.")
    parser.add_argument("-H", "--hashing", choices=["blake2b", "blake2s", "md5", "sha1", "sha224", "sha256", "sha384",
                                                    "sha3_224", "sha3_256", "sha3_384", "sha3_512", "sha512",
                                                    "shake_128", "shake_256", "adler32", "crc32"], default="sha512",
                        help="The hashing algorithm used to compare hashes between files.")
    parser.add_argument("--phashing", action='store_true',
                        help='Set this flag if you want to enable perceptual hashing.')
    parser.add_argument("--perceptual-hashing-algorithm", choices=["phash64", "phash1", "dhash"], default="phash64",
                        help='The perceptual hashing algorithm used to compare hashes between files.')
    parser.add_argument("-q", "--quiet", action='store_true',
                        help='Set this flag if you want to completely silence all outputs to stdout.')
    parser.add_argument("--disable-progress-bar", action='store_true',
                        help='Set this flag if you want to completely disable the progress bar.')
    args = parser.parse_args()

    dupe_eraser(
        path_dir=args.path_dir,
        behavior=args.behavior,
        recursive=args.recursive,
        shallow=args.shallow,
        safe_directory=args.safe_directory,
        hashing_algorithm=args.hashing,
        perceptual_hash=args.perceptual_hash,
        perceptual_hashing_algorithm=args.perceptual_hashing_algorithm,
        quiet=args.quiet,
        disable_progress_bar=args.disable_progress_bar
    )


def dupe_eraser(path_dir: str = ".", behavior: str = "c", recursive: bool = False, shallow: bool = False,
                safe_directory: str = "_safe_directory", hashing_algorithm: str = "sha512",
                perceptual_hash: bool = False, perceptual_hashing_algorithm: str = "phash64", quiet: bool = False,
                disable_progress_bar: bool = False):
    parameters = locals()

    if quiet:
        sys.stdout = open(os.devnull, 'w')

    path_dir = Path(path_dir)
    safe_directory = Path(safe_directory).absolute()

    files_to_examine = get_files_to_examine(path_dir=path_dir, recursive=recursive, safe_directory=safe_directory)
    hashes = computing_hashes(files_to_examine=files_to_examine, hashing_algorithm=hashing_algorithm,
                              disable_progress_bar=disable_progress_bar)
    if perceptual_hash:
        perceptual_hashes = computing_perceptual_hashes(files_to_examine=files_to_examine,
                                                        hashing_algorithm=perceptual_hashing_algorithm,
                                                        disable_progress_bar=disable_progress_bar)
    else:
        perceptual_hashes = None
    look_for_dupe(files_to_examine=files_to_examine, hashes=hashes, perceptual_hashes=perceptual_hashes,
                  behavior=behavior, shallow=shallow, safe_directory=safe_directory,
                  disable_progress_bar=disable_progress_bar)


if __name__ == "__main__":
    main()
