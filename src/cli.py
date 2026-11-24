"""CLI utility for Deflate (Gzip) file compression."""

import argparse
import gzip
import sys

BUFFER_SIZE = 8192


def compress_file(input_path: str, output_path: str) -> None:
    """Compress a file using the Deflate algorithm wrapped in gzip."""
    with open(input_path, "rb") as f_in:
        with gzip.open(output_path, "wb") as f_out:
            while True:
                chunk = f_in.read(BUFFER_SIZE)
                if not chunk:
                    break
                f_out.write(chunk)


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Compress a file using Deflate (Gzip)."
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to the input file to be compressed.",
    )
    parser.add_argument(
        "output",
        type=str,
        help="Path to the resulting .gz file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI utility."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        compress_file(args.input, args.output)
    except FileNotFoundError:
        print(f"Error: file '{args.input}' not found.", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(f"Successfully compressed '{args.input}' to '{args.output}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
