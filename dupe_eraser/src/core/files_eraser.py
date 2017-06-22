def remove_doublons(list_files, index_to_remove):
    for index in reversed(index_to_remove):
        file = list_files.pop(index)
        print(file)
        #file.remove()
    return list_files