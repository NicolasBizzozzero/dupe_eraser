import os
from pathlib import Path


def count_n_of_files(path_dir: str, recursive: bool = False) -> int:
    if recursive:
        return sum(1 for path in Path(path_dir).rglob("*") if path.is_file())
    else:
        return sum(1 for entry in os.listdir(path_dir) if os.path.isfile(os.path.join(path_dir, entry)))


def chunks(file: Path, chunk_size: int):
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size) or None, None):
            yield chunk


def is_picture(file: str) -> bool:
    """ Check if a file is a picture based on its extension. """
    try:
        extension = file.split(".")[-1]
    except IndexError:
        # No extension to check
        return False
    return extension.lower() in (
        "png",
        "jpg", "jpeg",
        "bmp",
        "gif",
    )


if __name__ == "__main__":
    pass
