import hashlib
from enum import Enum
from pathlib import Path

# from dupe_eraser.src.utils import chunks
from src.utils import chunks


class HashingAlgorithmNotSupported(Exception):
    def __init__(self, algorithm: str):
        Exception.__init__(self, "The hashing algorithm \"{algorithm}\" does not exists or is currently "
                                 "not supported.".format(algorithm=algorithm))


class HashingAlgorithm(Enum):
    # hashlib's algorithms
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"
    MD5 = "md5"
    SHA1 = "sha1"
    SHA224 = "sha224"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA3_224 = "sha3_224"
    SHA3_256 = "sha3_256"
    SHA3_384 = "sha3_384"
    SHA3_512 = "sha3_512"
    SHA512 = "sha512"
    SHAKE_128 = "shake_128"
    SHAKE_256 = "shake_256"

    # zlib's algorithms
    ADLER32 = "adler32"
    CRC32 = "crc32"


def check_hashing_algorithm_supported(algorithm: str) -> None:
    algorithm = algorithm.lower()
    if not HashingAlgorithm(algorithm):
        raise HashingAlgorithmNotSupported(algorithm)


def compute_hash(file: Path, hashing_algorithm: str) -> str:
    m = hashlib.new(hashing_algorithm)
    for chunk in chunks(file, chunk_size=8192):
        m.update(chunk)
    return m.hexdigest()


if __name__ == "__main__":
    pass
