#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from datetime import datetime, timezone
import hashlib
import json
import os
import pathlib
import psutil
import socket
import subprocess


def get_commit_id():
    return (
        subprocess.run(
            ["git", "describe", "--always", "--dirty"],
            capture_output=True,
        )
        .stdout.decode()
        .strip()
    )


def sha256_file(filename):
    with open(filename, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def get_basic_metadata(*data_filenames):
    now = datetime.now(timezone.utc).isoformat()
    metadata = {}
    metadata["_comment"] = (
        "This file and all the files in this directory were generated automatically. "
        "Do not modify them; re-run the analysis workflow!"
    )
    metadata["workflow_run"] = {
        "completed": now,
        "user_name": os.getlogin(),
        "machine_name": socket.gethostname(),
    }
    metadata["analysis_code"] = {"version": get_commit_id()}
    metadata["workflow_step"] = {
        "command_line": " ".join(psutil.Process(os.getpid()).cmdline()),
        "completed": now,
    }
    if data_filenames:
        metadata["input_data"] = {
            filename: {
                "filename": filename,
                "last_updated": datetime.fromtimestamp(
                    pathlib.Path(filename).stat().st_mtime, timezone.utc
                ).isoformat(),
                "sha256": sha256_file(filename),
            }
            for filename in data_filenames
        }

    return metadata


def flatten_metadata(metadata):
    flat_metadata = {
        "_comment": (
            "This file was generated automatically. "
            "Do not modify it directly; re-run the analysis workflow!"
        )
    }

    for outer_key, inner_metadata in metadata.items():
        if outer_key == "_comment":
            continue
        flat_metadata.update(
            {f"{outer_key}::{k}": v for k, v in inner_metadata.items()}
        )

    flat_metadata["generated"] = flat_metadata["workflow_run::completed"]
    del flat_metadata["workflow_run::completed"]
    return flat_metadata


def get_flat_metadata():
    return flatten_metadata(get_basic_metadata())


def text_metadata(metadata, comment_char="#"):
    return "\n".join(
        [
            f"{comment_char} {k}: {v.replace('\n', '\n{comment_char} ')}"
            for k, v in flatten_metadata(metadata).items()
        ]
    )


number_names = {
    "1": "One",
    "2": "Two",
    "3": "Three",
    "4": "Four",
    "5": "Five",
    "6": "Six",
    "7": "Seven",
    "8": "Eight",
    "9": "Nine",
    "0": "Zero",
    ".": "Point",
}


def number_to_latex(number, tolerate_non_numbers=False):
    result = str(number)
    if not tolerate_non_numbers:
        if not set(result) < set(number_names):
            raise ValueError(
                "Non-numeric characters found but tolerate_non_numbers disabled"
            )

    for char, substitution in number_names.items():
        result = result.replace(char, substitution)
    return result


def add_provenance_hdf5(h5file):
    provenance_group = h5file.create_group("_comment")
    for key, value in sorted(get_flat_metadata().items()):
        provenance_group.create_dataset(key, data=value)


def get_args():
    parser = ArgumentParser(
        description="Summarise inputs to a workflow in a JSON file."
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        metavar="input_file",
        help="Input file whose details to include in the stamp.",
    )
    parser.add_argument(
        "--output_file",
        type=FileType("w"),
        default="-",
        help="Where to output the stamp.",
    )
    return parser.parse_args()


def main():
    args = get_args()
    metadata = get_basic_metadata(*args.input_files)
    print(json.dumps(metadata, sort_keys=True, indent=4), file=args.output_file)


if __name__ == "__main__":
    main()
