from enum import Enum


class HashingAlgorithmNotSupported(Exception):
    def __init__(self, algorithm: str):
        Exception.__init__(self, "The hashing algorithm \"{algorithm}\" is currently "
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
    if algorithm not in HashingAlgorithm:
        raise HashingAlgorithmNotSupported(algorithm)
