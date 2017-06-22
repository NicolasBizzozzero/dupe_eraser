from path import Path

from dupe_eraser.src.core.files_finder import find_doublons


def main_entry_point():
    here = Path.getcwd()
    files = [file for file in here.walkfiles()]
    while files:
        file = files.pop(0)
        files = find_doublons(file, files)


def main():
    pass


if __name__ == "__main__":
    pass
