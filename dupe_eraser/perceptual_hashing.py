""" Library containing implementations and API of perceptual hashing algorithms.

Source:
* https://github.com/VieVie31/scene_detection/blob/master/src/functions.py#L444
"""
from enum import Enum
from pathlib import Path

import numpy as np

from skimage.color import rgb2grey
from skimage.transform import resize
from skimage.io import imread


class PerceptualHashingAlgorithmNotSupported(Exception):
    def __init__(self, algorithm: str):
        Exception.__init__(self, "The hashing algorithm \"{algorithm}\" does not exists or is currently "
                                 "not supported.".format(algorithm=algorithm))


class PerceptualHashingAlgorithm(Enum):
    PHASH64 = "phash64"
    PHASH1 = "phash1"
    DHASH = "dhash"


def check_hashing_algorithm_supported(algorithm: str) -> None:
    algorithm = algorithm.lower()
    if not PerceptualHashingAlgorithm(algorithm):
        raise PerceptualHashingAlgorithmNotSupported(algorithm)


def compute_perceptual_hash(file: Path, hashing_algorithm: str) -> str:
    check_hashing_algorithm_supported(hashing_algorithm)
    hashing_algorithm = globals()[hashing_algorithm]
    return hashing_algorithm(imread(file))


def phash64(img: np.ndarray):
    """Compute a perceptual hash of an image.
    :param img: a rgb image to be hashed
    :type img: numpy.ndarray
    :return: a perceptrual hash of img coded on 64 bits
    :rtype: int
    """
    resized = rgb2grey(resize(img, (8, 8)))
    boolean_matrix = resized > resized.mean()
    hash_lst = boolean_matrix.reshape((1, 64))[0]
    hash_lst = list(map(int, hash_lst))
    im_hash = 0
    for v in hash_lst:
        im_hash = (im_hash << 1) | v
    return im_hash


def phash1(img: np.ndarray):
    """Return the hash of the image as a list of bits
    always ordered in the same order.
    :param img: the binarized image
    :type img: numpy.ndarray
    :return: the perceptual hash of img in a vector
    <!> the length of the hash returned depend of the size of image !!
    :ntype: np.array
    """
    return ((img > 0) * 1).reshape((1, img.shape[0] * img.shape[1]))[0]


def dhash(img: np.ndarray):
    """Compute a perceptual has of an image.
    Algo explained here :
    https://blog.bearstech.com/2014/07/numpy-par-lexemple-une-implementation-de-dhash.html
    :param img: an image
    :type img: numpy.ndarray
    :return: a perceptual hash of img coded on 64 bits
    :rtype: int
    """
    twos = np.array([2 ** n for n in range(7, -1, -1)])
    bigs = np.array([256 ** n for n in range(7, -1, -1)], dtype=np.uint64)
    img = rgb2grey(resize(img, (9, 8)))
    h = np.array([0] * 8, dtype=np.uint8)
    for i in range(8):
        h[i] = twos[img[i] > img[i + 1]].sum()
    return (bigs * h).sum()


if __name__ == "__main__":
    pass
