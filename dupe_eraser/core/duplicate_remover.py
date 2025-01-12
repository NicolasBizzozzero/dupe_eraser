import hashlib
import logging
import os
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import blake3
import humanize
import mmh3
import xxhash
from tqdm import tqdm
from PIL import Image
import imagehash
from tabulate import tabulate

from core.comparison_method import ComparisonMethod
from core.hash_performance import HashPerformance


class DuplicateRemover:
    # Cryptographic hash functions
    CRYPTO_HASHES = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "sha3_256": hashlib.sha3_256,
        "sha3_512": hashlib.sha3_512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
        "blake3": lambda: blake3.blake3(),
    }

    # Non-cryptographic hash functions (faster)
    FAST_HASHES = {
        "xxh32": lambda: xxhash.xxh32(),
        "xxh64": lambda: xxhash.xxh64(),
        "xxh3_64": lambda: xxhash.xxh3_64(),
        "xxh3_128": lambda: xxhash.xxh3_128(),
        "murmur3_32": lambda: mmh3,
    }

    # Perceptual hash functions for images
    PERCEPTUAL_HASHES = {
        "phash": imagehash.average_hash,
        "dhash": imagehash.dhash,
        "whash": imagehash.whash,
        "colorhash": imagehash.colorhash,
    }

    def __init__(
        self,
        comparison_method: str = ComparisonMethod.HASH,
        hash_algorithm: str = "xxh3_128",
        hash_progress_threshold_mb: int = 10,
        perceptual_threshold: int = 5,  # Hamming distance threshold for perceptual hashes
        show_progress: bool = True,
        print_only: bool = False,
    ):
        """Initialize DuplicateRemover with configurable settings.

        Args:
            comparison_method: Method to use for file comparison (hash or bytes)
            hash_algorithm: Hash algorithm to use for file comparison
            hash_progress_threshold_mb: Show hash progress for files larger than
                this size in MB
            perceptual_threshold: Hamming distance threshold for perceptual hashes
        """
        self.comparison_method = comparison_method
        self.hash_algorithm = hash_algorithm
        self.perceptual_threshold = perceptual_threshold
        self.show_progress = show_progress
        self.print_only = print_only

        # Select appropriate hash function if using hash comparison
        if comparison_method == ComparisonMethod.HASH:
            if hash_algorithm in self.CRYPTO_HASHES:
                self.hash_func = self.CRYPTO_HASHES[hash_algorithm]
                self.hash_type = "crypto"
            elif hash_algorithm in self.FAST_HASHES:
                self.hash_func = self.FAST_HASHES[hash_algorithm]
                self.hash_type = "fast"
            elif hash_algorithm in self.PERCEPTUAL_HASHES:
                self.hash_func = self.PERCEPTUAL_HASHES[hash_algorithm]
                self.hash_type = "perceptual"
            else:
                raise ValueError(
                    f"Unsupported hash algorithm. Available options:\n"
                    f"Cryptographic: {', '.join(self.CRYPTO_HASHES.keys())}\n"
                    f"Fast: {', '.join(self.FAST_HASHES.keys())}\n"
                    f"Perceptual: {', '.join(self.PERCEPTUAL_HASHES.keys())}"
                )

        self.hash_threshold = hash_progress_threshold_mb * 1024 * 1024
        self.total_files_processed = 0
        self.total_bytes_processed = 0
        self.duplicates_found = 0
        self.space_saved = 0
        self.performance = HashPerformance(
            hash_algorithm if comparison_method == ComparisonMethod.HASH else "bytes"
        )

    def compare_files_bytes(self, file1: str, file2: str, file_size: int) -> bool:
        """Compare two files byte by byte with progress bar for large files.

        Args:
            file1: Path to first file
            file2: Path to second file
            file_size: Size of the files (should be same for both)

        Returns:
            bool: True if files are identical
        """
        chunk_size = 8192  # Larger chunk size for byte comparison
        total_chunks = (file_size + chunk_size - 1) // chunk_size

        if file_size > self.hash_threshold:
            with tqdm(
                total=total_chunks,
                desc=f"Comparing {os.path.basename(file1)} and {os.path.basename(file2)}",
                unit="chunk",
                colour="yellow",
                leave=False,
                disable=not self.show_progress,
            ) as pbar:
                with open(file1, "rb") as f1, open(file2, "rb") as f2:
                    while True:
                        chunk1 = f1.read(chunk_size)
                        chunk2 = f2.read(chunk_size)
                        if chunk1 != chunk2:
                            return False
                        if not chunk1:  # EOF
                            break
                        pbar.update(1)
        else:
            with open(file1, "rb") as f1, open(file2, "rb") as f2:
                while True:
                    chunk1 = f1.read(chunk_size)
                    chunk2 = f2.read(chunk_size)
                    if chunk1 != chunk2:
                        return False
                    if not chunk1:  # EOF
                        break

        return True

    def are_files_equal(self, file1: str, file2: str, file_size: int) -> bool:
        """Compare two files using the selected comparison method.

        Args:
            file1: Path to first file
            file2: Path to second file
            file_size: Size of the files

        Returns:
            bool: True if files are considered equal
        """
        if self.comparison_method == ComparisonMethod.BYTES:
            return self.compare_files_bytes(file1, file2, file_size)
        else:
            hash1 = self.get_file_hash(file1, file_size)
            hash2 = self.get_file_hash(file2, file_size)
            return hash1 == hash2

    def group_files_by_size(
        self, dirpath: str, filenames: List[str]
    ) -> Dict[int, List[str]]:
        """Group files by size for initial quick comparison.

        Args:
            dirpath: Directory path
            filenames: List of filenames

        Returns:
            Dictionary mapping file sizes to lists of file paths
        """
        size_groups = defaultdict(list)
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                try:
                    file_size = os.path.getsize(filepath)
                    size_groups[file_size].append(filepath)
                except OSError:
                    continue
        return size_groups

    def find_duplicates_in_dir(
        self, dirpath: str, filenames: List[str]
    ) -> Dict[str, List[Tuple[str, int]]]:
        """Find duplicate files within a directory.

        Args:
            dirpath: Directory path
            filenames: List of filenames

        Returns:
            Dictionary mapping file identifiers to lists of duplicate files
        """
        # First group by size
        size_groups = self.group_files_by_size(dirpath, filenames)

        # Then compare files of the same size
        duplicates = defaultdict(list)
        for size, files in size_groups.items():
            if len(files) > 1:
                # Use first file as reference
                reference = files[0]
                duplicates[reference].append((reference, size))

                # Compare others to reference
                for other in files[1:]:
                    if self.are_files_equal(reference, other, size):
                        duplicates[reference].append((other, size))

        return {ref: dups for ref, dups in duplicates.items() if len(dups) > 1}

    def find_and_remove_duplicates(
        self, root_dir: str, disable_progress: bool = False
    ) -> Dict[str, str]:
        """Recursively scan directories and remove duplicate files."""
        deleted_files = {}

        logging.info("Calculating total files and size...")
        total_files, total_size = self.count_files_and_size(root_dir)
        logging.info(
            f"Found {total_files} files (Total size: {humanize.naturalsize(total_size)})"
        )

        method_str = (
            "byte-by-byte comparison"
            if self.comparison_method == ComparisonMethod.BYTES
            else f"{self.hash_algorithm} hashing"
        )
        logging.info(f"Using {method_str} for file comparison")

        if not disable_progress:
            progress_bar = tqdm(
                total=total_files,
                desc="Processing files",
                unit="file",
                colour="green",
                postfix=self._get_progress_stats(),
            )
        else:
            progress_bar = None

        for dirpath, _, filenames in os.walk(root_dir):
            if not filenames:
                continue

            duplicates = self.find_duplicates_in_dir(dirpath, filenames)

            for original, duplicate_list in duplicates.items():
                for filepath, size in duplicate_list[1:]:
                    try:
                        if not self.print_only:
                            os.remove(filepath)
                        deleted_files[filepath] = original
                        self.space_saved += size
                        self.duplicates_found += 1
                        logging.info(
                            f"Deleted duplicate: {filepath} ({humanize.naturalsize(size)})"
                        )
                    except OSError as e:
                        logging.error(f"Error deleting {filepath}: {e}")

            if progress_bar:
                self.total_files_processed += len(filenames)
                progress_bar.update(len(filenames))
                progress_bar.set_postfix(**self._get_progress_stats())

        if progress_bar:
            progress_bar.close()

        return deleted_files

    def is_image_file(self, filepath: str) -> bool:
        """Check if file is an image based on extension."""
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
        return os.path.splitext(filepath)[1].lower() in image_extensions

    def get_file_hash(self, filepath: str, file_size: int) -> str:
        """Calculate file hash with progress bar for large files.

        Args:
            filepath: Path to the file to hash
            file_size: Size of the file in bytes

        Returns:
            str: Hex digest of file hash or perceptual hash distance
        """
        start_time = time.time()

        # Handle perceptual hashing for images
        if self.hash_type == "perceptual":
            if not self.is_image_file(filepath):
                return "non_image"
            try:
                with Image.open(filepath) as img:
                    hash_value = str(self.hash_func(img))
            except Exception:
                return "invalid_image"

        # Handle regular file hashing
        else:
            hasher = self.hash_func()
            chunk_size = 4096

            if file_size > self.hash_threshold:
                with tqdm(
                    total=file_size,
                    desc=f"Hashing {os.path.basename(filepath)} ({self.hash_algorithm})",
                    unit="B",
                    unit_scale=True,
                    colour="yellow",
                    leave=False,
                    disable=not self.show_progress,
                ) as pbar:
                    with open(filepath, "rb") as f:
                        for byte_block in iter(lambda: f.read(chunk_size), b""):
                            if (
                                self.hash_type == "fast"
                                and self.hash_algorithm == "murmur3_32"
                            ):
                                hasher.hash_bytes(byte_block)
                            else:
                                hasher.update(byte_block)
                            pbar.update(len(byte_block))
            else:
                with open(filepath, "rb") as f:
                    for byte_block in iter(lambda: f.read(chunk_size), b""):
                        if (
                            self.hash_type == "fast"
                            and self.hash_algorithm == "murmur3_32"
                        ):
                            hasher.hash_bytes(byte_block)
                        else:
                            hasher.update(byte_block)

            hash_value = (
                hasher.hexdigest() if hasattr(hasher, "hexdigest") else str(hasher)
            )

        # Record performance metrics
        elapsed_time = time.time() - start_time
        self.performance.times.append(elapsed_time)
        self.performance.sizes.append(file_size)

        return hash_value

    @staticmethod
    def benchmark_hashes(
        sample_file: str, iterations: int = 3
    ) -> List[HashPerformance]:
        """Benchmark different hash algorithms on a sample file.

        Args:
            sample_file: Path to file for benchmarking
            iterations: Number of iterations for each algorithm

        Returns:
            List of HashPerformance objects with results
        """
        results = []
        file_size = os.path.getsize(sample_file)

        # Test all hash algorithms
        all_hashes = {**DuplicateRemover.CRYPTO_HASHES, **DuplicateRemover.FAST_HASHES}

        for name, hash_func in all_hashes.items():
            perf = HashPerformance(name)

            for _ in range(iterations):
                hasher = hash_func()
                start_time = time.time()

                with open(sample_file, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        if name == "murmur3_32":
                            hasher.hash_bytes(chunk)
                        else:
                            hasher.update(chunk)

                elapsed_time = time.time() - start_time
                perf.times.append(elapsed_time)
                perf.sizes.append(file_size)

            results.append(perf)

        # Sort results by average speed
        results.sort(key=lambda x: x.avg_speed_mbps, reverse=True)
        return results

    @staticmethod
    def print_benchmark_results(results: List[HashPerformance]) -> None:
        """Print benchmark results in a formatted table.

        Args:
            results: List of HashPerformance objects
        """
        table_data = []
        for perf in results:
            table_data.append(
                [
                    perf.name,
                    f"{perf.avg_speed_mbps:.1f} MB/s",
                    f"{perf.avg_time_ms:.2f} ms",
                ]
            )

        logging.info("\nHash Algorithm Benchmark Results:")
        logging.info(
            tabulate(
                table_data, headers=["Algorithm", "Speed", "Avg Time"], tablefmt="grid"
            )
        )

    def count_files_and_size(self, root_dir: str) -> Tuple[int, int]:
        """Count total number of files and their combined size.

        Args:
            root_dir: Root directory to scan

        Returns:
            Tuple containing total file count and total size in bytes
        """
        total_files = 0
        total_size = 0
        for _, _, files in os.walk(root_dir):
            total_files += len(files)
            for file in files:
                try:
                    total_size += os.path.getsize(os.path.join(root_dir, file))
                except OSError:
                    continue
        return total_files, total_size

    def _remove_duplicates(
        self, files_by_hash: Dict[str, list], deleted_files: Dict[str, str]
    ) -> None:
        """Remove duplicate files from the given hash groups.

        Args:
            files_by_hash: Dictionary mapping file hashes to file paths and sizes
            deleted_files: Dictionary to track deleted files
        """
        for file_list in files_by_hash.values():
            if len(file_list) > 1:
                original, _ = file_list[0]
                for duplicate, dup_size in file_list[1:]:
                    try:
                        if not self.print_only:
                            os.remove(duplicate)
                        deleted_files[duplicate] = original
                        self.space_saved += dup_size
                        self.duplicates_found += 1
                        logging.info(
                            f"\nDeleted duplicate: {duplicate} "
                            f"({humanize.naturalsize(dup_size)})"
                        )
                    except OSError as e:
                        logging.error(f"\nError deleting {duplicate}: {e}")

    def _get_progress_stats(self, current_dir: Optional[str] = None) -> dict:
        """Generate statistics for progress bar display.

        Args:
            current_dir: Current directory being processed (optional)

        Returns:
            Dictionary of statistics for progress display
        """
        stats = {
            "processed": f"{self.total_files_processed} files",
            "data": humanize.naturalsize(self.total_bytes_processed),
            "duplicates": str(self.duplicates_found),
            "saved": humanize.naturalsize(self.space_saved),
        }
        if current_dir:
            stats["dir"] = current_dir
        return stats
