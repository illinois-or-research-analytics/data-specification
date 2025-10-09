import argparse
import pandas as pd
from pathlib import Path
import csv


def get_delimiter(filepath: str) -> str:
    with open(filepath, "r") as f:
        for current_line in f:
            if "," in current_line:
                return ","
            elif " " in current_line:
                return " "
            elif "\t" in current_line:
                return "\t"
            else:
                raise ValueError(
                    "Unsupported delimiter: delimiter must be either comma, tab, or whitespace."
                )


def convert_delimiter(input, output, src_delimiter, tar_delimiter):
    Path(output).parent.mkdir(exist_ok=True, parents=True)
    pd.read_csv(input, sep=src_delimiter).to_csv(output, index=False, sep=tar_delimiter)


# TODO: enforce ordering
def check_header_and_columns(filename, delimiter, required_cols):
    with open(filename, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        first_row = next(reader, [])

        # detect header
        has_header = any(not cell.isdigit() for cell in first_row)

        if has_header:
            # first_row is the header
            missing = [col for col in required_cols if col not in first_row]
            return True, (len(missing) == 0), missing
        else:
            return False, (len(required_cols) == 0), required_cols


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate and process a character-delimited file, converting it to use a specified delimiter"
    )

    parser.add_argument("input", help="Path to the input character-delimited file")
    parser.add_argument("--output", help="Path to the output character-delimited file")
    parser.add_argument(
        "--delimiter",
        default=None,
        choices=["\\t", "\\s", "comma"],
        help="Target delimiter to use. When specified, the input file will be converted to use that delimiter",
    )
    parser.add_argument(
        "--format",
        default=None,
        choices=["edgelist", "nodelist", "cluster_list"],
        help="Target format of the input. If specified, the script will check if it conforms to the specification",
    )

    args = parser.parse_args()

    # Get delimiter
    delimiter = get_delimiter(args.input)
    if args.delimiter == "\\t":
        args.delimiter = "\t"
    elif args.delimiter == "\\s":
        args.delimiter = " "
    elif args.delimiter == "comma":
        args.delimiter = ","

    # Validate format
    if args.format is not None:
        if args.format == "edgelist":
            has_header, valid, missing = check_header_and_columns(
                args.input, delimiter, required_cols=["source", "target"]
            )

            if has_header and valid:
                print("Input file is a valid edgelist")
            else:
                print("Input file is not a valid edgelist", end=". ")
                if not has_header:
                    print("It has no header.")
                elif not valid:
                    print(f"Missing columns: {missing}.")
                exit(1)
        elif args.format == "nodelist":
            has_header, valid, missing = check_header_and_columns(
                args.input, delimiter, required_cols=["node_id"]
            )

            if has_header and valid:
                print("Input file is a valid nodelist")
            else:
                print("Input file is not a valid nodelist", end=". ")
                if not has_header:
                    print("It has no header.")
                elif not valid:
                    print(f"Missing columns: {missing}.")
                exit(1)
        elif args.format == "cluster_list":
            has_header, valid, missing = check_header_and_columns(
                args.input, delimiter, required_cols=["node_id", "cluster_id"]
            )

            if has_header and valid:
                print("Input file is a valid cluster list")
            else:
                print("Input file is not a valid cluster list", end=". ")
                if not has_header:
                    print("It has no header.")
                elif not valid:
                    print(f"Missing columns: {missing}.")
                exit(1)

    # Convert delimiter
    if args.delimiter is not None:
        if args.delimiter == delimiter:
            print(f"No need to change delimiter")

        if args.output is not None:
            convert_delimiter(args.input, args.output, delimiter, args.delimiter)
