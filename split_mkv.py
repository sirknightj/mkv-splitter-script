import argparse
import logging
import os
import sys

# An MKV file starts with an EBML header, identified by the byte sequence `0x1A 0x45 0xDF 0xA3`.
MAGIC_MKV_HEADER = b'\x1A\x45\xDF\xA3'

def find_mkv_headers(data: bytes) -> list[int]:
    """
    Finds the start positions of MKV headers in the data.

    This function scans the given byte stream to locate all occurrences of the header sequence.

    :param data: The raw byte stream of the MKV file.
    :return: A list of byte offsets where MKV headers are found.
    """
    return [i for i in range(len(data) - len(MAGIC_MKV_HEADER))
            if data[i:i + 4] == MAGIC_MKV_HEADER]


def split_mkv_stream(data: bytes, output_prefix: str) -> None:
    """
    Splits MKV data into separate files based on EBML header positions.

    :param input_file: Path to the concatenated MKV file.
    :param output_prefix: Prefix for the output MKV files (e.g., 'split_output').
    """
    start_indices = find_mkv_headers(data)
    if not start_indices:
        logging.error("No MKV headers found.")
        return

    output_dir = os.path.dirname(output_prefix) or '.'
    os.makedirs(output_dir, exist_ok=True)
    file_sizes = []

    for idx, start in enumerate(start_indices):
        end = start_indices[idx + 1] if idx + 1 < len(start_indices) else len(data)
        segment = data[start:end]

        # Validate that the split fragment starts with the EBML header
        if not segment.startswith(MAGIC_MKV_HEADER):
            logging.warning("Split #%d does not start with EBML header!", idx)
            continue

        output_file = f"{output_prefix}_{idx}.mkv"
        try:
            with open(output_file, 'wb') as f:
                f.write(segment)
            size = os.path.getsize(output_file)
            file_sizes.append((output_file, format_file_size(size)))
            logging.info("Created: %s (%s)", output_file, format_file_size(size))
        except IOError as e:
            logging.error("Error writing %s: %s", output_file, e)

    print_summary(file_sizes)


def print_summary(file_sizes):
    """
    Prints a summary table of the created files using string formatting.

    :param file_sizes: List of tuples containing (file name, file size)
    """
    col1_width = max(len(name) for name, _ in file_sizes)  # File name
    col2_width = max(len(size) for _, size in file_sizes)  # File size

    header = f"| {'File Name'.ljust(col1_width)} | {'Size'.ljust(col2_width)} |"
    separator = f"+{'-' * (col1_width + 2)}+{'-' * (col2_width + 2)}+"

    print("\nSummary of created files:")
    print(separator)
    print(header)
    print(separator)
    for name, size in file_sizes:
        print(f"| {name.ljust(col1_width)} | {size.ljust(col2_width)} |")
    print(separator)


def format_file_size(size_bytes: int) -> str:
    """
    Formats file size dynamically to show MB for larger files and KB for smaller ones.

    :param size_bytes: File size in bytes.
    :return: A formatted string representing the file size.
    """
    size_mb = size_bytes / (1024 * 1024)
    if size_mb >= 1:
        return f"{size_mb:.2f} MB"
    else:
        size_kb = size_bytes / 1024
        return f"{size_kb:.2f} KB"


def read_input_data(input_file: str | None) -> bytes:
    if input_file:
        with open(input_file, 'rb') as f:
            return f.read()
    else:
        logging.info("Reading from stdin...")
        return sys.stdin.buffer.read()

def main():
    """
    Parses command-line arguments and executes the MKV splitting process.

    The script takes an input MKV file and an output prefix, then processes the file
    to extract and save individual MKV segments.
    """
    parser = argparse.ArgumentParser(
        description="Splits concatenated MKV fragments (e.g., from KVS GetMedia) into separate files.")
    parser.add_argument("--output-prefix",
                        help="Prefix for output MKV files. (Default: './output/split_output').",
                        default="./output/split_output")
    parser.add_argument("--input", help="Path to input MKV file. If omitted, reads from stdin.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        data = read_input_data(args.input)
        split_mkv_stream(data, args.output_prefix)
    except Exception as e:
        logging.error("Unhandled exception: %s", e)


if __name__ == "__main__":
    main()
