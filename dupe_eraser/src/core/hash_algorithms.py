from enum import Enum
import hashlib
import zlib
from typing import Callable


class UnknownHashAlgorithm(Exception):
    def __init__(self):
        Exception.__init__(self, "This hash algorithm is not availaible.")


class HashAlgorithm(Enum):
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


def hash_algorithm_to_function(hash_algorithm: HashAlgorithm) -> Callable:
    if hash_algorithm in (HashAlgorithm.BLAKE2B, HashAlgorithm.BLAKE2S, HashAlgorithm.MD5, HashAlgorithm.SHA1,
                          HashAlgorithm.SHA224, HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA3_224,
                          HashAlgorithm.SHA3_256, HashAlgorithm.SHA3_384, HashAlgorithm.SHA3_512, HashAlgorithm.SHA512,
                          HashAlgorithm.SHAKE_128, HashAlgorithm.SHAKE_256):
        return hashlib.__get_builtin_constructor(hash_algorithm.value)
    elif hash_algorithm == HashAlgorithm.ADLER32:
        return zlib.adler32
    elif hash_algorithm == HashAlgorithm.CRC32:
        return zlib.crc32
    else:
        raise UnknownHashAlgorithm()
