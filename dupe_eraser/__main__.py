import os
import logging
import argparse
import humanize
from core.comparison_method import ComparisonMethod
from core.duplicate_remover import DuplicateRemover


def setup_logging(quiet_mode: bool):
    """Set up the logging configuration."""
    level = logging.ERROR if quiet_mode else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Recursively find and optionally remove duplicate files in a directory."
    )

    parser.add_argument(
        "root_dir",
        type=str,
        help="Root directory to scan for duplicates.",
    )
    parser.add_argument(
        "--method",
        choices=[ComparisonMethod.HASH, ComparisonMethod.BYTES],
        default=ComparisonMethod.HASH,
        help="File comparison method: 'hash' (default) or 'bytes' for byte-by-byte comparison.",
    )
    parser.add_argument(
        "--hash-algorithm",
        type=str,
        default="xxh3_128",
        help="Hash algorithm to use (only applicable if method is 'hash'). Default is 'xxh3_128'.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all output except critical errors.",
    )
    parser.add_argument(
        "--disable-progress-bar",
        action="store_true",
        help="Disable progress bars during file processing.",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Only print duplicate files without removing them.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Set up logging
    setup_logging(args.quiet)

    # Validate root directory
    root_dir = os.path.abspath(args.root_dir)
    if not os.path.isdir(root_dir):
        logging.error(f"Invalid directory path: {root_dir}")
        return

    logging.info(f"Scanning directory: {root_dir}")

    try:
        remover = DuplicateRemover(
            comparison_method=args.method,
            hash_algorithm=args.hash_algorithm,
            show_progress=not args.disable_progress_bar,
            print_only=args.print_only,
        )

        # Find and remove duplicates
        deleted_files = remover.find_and_remove_duplicates(
            root_dir,
        )

        # Log summary
        logging.info("\nOperation completed!")
        logging.info(f"Comparison method: {args.method}")
        if args.method == ComparisonMethod.HASH:
            logging.info(f"Hash algorithm used: {remover.hash_algorithm}")
        logging.info(
            f"Average processing speed: {remover.performance.avg_speed_mbps:.1f} MB/s"
        )
        logging.info(f"Total duplicate files removed: {len(deleted_files)}")
        logging.info(f"Total space saved: {humanize.naturalsize(remover.space_saved)}")
        logging.info(f"Total files processed: {remover.total_files_processed}")
        logging.info(
            f"Total data processed: "
            f"{humanize.naturalsize(remover.total_bytes_processed)}"
        )

    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except Exception as e:
        logging.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
