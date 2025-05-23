#!/usr/bin/env python3
import numpy as np
from argparse import ArgumentParser, FileType

from .dump import read_sample_files, dump_dict, dump_samples
from .mass import renormalisation_constant


def get_args():
    parser = ArgumentParser()

    parser.add_argument(
        "data_filename",
        nargs="+",
        metavar="sample_filename",
        help="Filename of a sample file",
    )
    parser.add_argument(
        "--channel",
        choices=["ps", "v", "av"],
        default=None,
        help="Measuring channel",
    )
    parser.add_argument(
        "--output_file_mean",
        type=FileType("w"),
        default="-",
        help="Where to output the mean and uncertainty",
    )
    parser.add_argument(
        "--output_file_samples",
        type=FileType("w"),
        default=None,
        help="Where to output the bootstrap samples",
    )

    return parser.parse_args()


def main():
    args = get_args()

    datum = read_sample_files(args.data_filename)[0]

    #  calculation of renormalisation factor based on Eqs. (29) and (30)
    Z_factor = 1 + 2 * (renormalisation_constant(args.channel)) * (
        8 / datum["beta"]
    ) / (16 * np.pi**2 * datum["plaquette_samples"])

    decay_constant = datum[f"{args.channel}_matrix_element_samples"] * Z_factor

    metadata = {
        "ensemble_name": datum["ensemble_name"],
        "beta": datum["beta"],
        "mAS": datum["mAS"],
        "Nt": datum["Nt"],
        "Ns": datum["Ns"],
    }
    dump_dict(
        {
            **metadata,
            f"{args.channel}_decay_constant": decay_constant.to_ufloat(),
        },
        args.output_file_mean,
    )
    if args.output_file_samples:
        dump_samples(
            {
                **metadata,
                f"{args.channel}_decay_constant": decay_constant,
            },
            args.output_file_samples,
        )


if __name__ == "__main__":
    main()
