from dupe_eraser.src.core.files_eraser import remove_doublons


def find_doublons(file, list_files):
    file_hash = file.read_hexhash(HASHING_ALGORITHM)

    index_to_remove = list()
    for index, possible_doublon in enumerate(list_files):
        if possible_doublon.read_hexhash(HASHING_ALGORITHM) == file_hash:
            index_to_remove.append(index)

    return remove_doublons(list_files, index_to_remove)