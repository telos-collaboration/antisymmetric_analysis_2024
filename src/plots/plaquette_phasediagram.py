#!/usr/bin/env python3

from argparse import ArgumentParser, FileType

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from ..definitions_common import format_definitions
from ..dump import read_files
from ..plots_common import save_or_show, ONE_COLUMN


def get_args():
    parser = ArgumentParser()

    parser.add_argument(
        "data_filenames",
        nargs="+",
        metavar="mean_filename",
        help="Filenames of files containing data to plot",
    )
    parser.add_argument(
        "--plot_file",
        default=None,
        help="Where to place the resulting plot. Default is to output to screen.",
    )
    parser.add_argument(
        "--plot_styles",
        default="styles/paperdraft.mplstyle",
        help="Stylesheet to use for plots",
    )
    parser.add_argument(
        "--definitions_file",
        type=FileType("w"),
        default="-",
        help="Where to place the generated definitions",
    )
    return parser.parse_args()


def plot(data):
    betas = sorted(set(data.beta))
    colours = {"unit": "C0", "random": "C3"}
    markers = {"unit": "x", "random": "o"}
    fig, axes = plt.subplots(
        nrows=len(betas),
        layout="constrained",
        figsize=(ONE_COLUMN, 1 + 1.5 * len(betas)),
    )

    for beta, ax in zip(betas, axes):
        beta_subset = data[data.beta == beta]
        ax.text(
            0.95, 0.95, f"$\\beta={beta}$", ha="right", va="top", transform=ax.transAxes
        )
        ax.set_ylabel(r"$\langle \mathcal {P} \rangle$")
        ax.set_xlabel("$am_0$")
        for start in ["unit", "random"]:
            plot_subset = beta_subset[beta_subset.start == start]
            ax.errorbar(
                plot_subset.mAS,
                plot_subset.avg_plaquette.map(lambda x: x.nominal_value),
                yerr=plot_subset.avg_plaquette.map(lambda x: x.std_dev),
                color=colours[start],
                marker=markers[start],
                ls="none",
            )
        ax.xaxis.set_major_locator(ticker.MultipleLocator(0.01))

    no_plot = [np.nan]
    ax.errorbar(
        no_plot,
        no_plot,
        yerr=no_plot,
        ls="none",
        color=colours["unit"],
        marker=markers["unit"],
        label="Cold start",
    )
    ax.errorbar(
        no_plot,
        no_plot,
        yerr=no_plot,
        ls="none",
        color=colours["random"],
        marker=markers["random"],
        label="Hot start",
    )
    fig.legend(loc="outside upper center", ncols=2)

    formatted_betas = r"$\beta = " + "$, $".join([f"{beta}" for beta in betas]) + "$"
    definitions = format_definitions({"PlaquettePhaseDiagramBetas": formatted_betas})
    return fig, definitions


def main():
    args = get_args()
    plt.style.use(args.plot_styles)
    data = read_files(args.data_filenames)
    fig, definitions = plot(data)
    print(definitions, file=args.definitions_file)
    save_or_show(fig, args.plot_file)


if __name__ == "__main__":
    main()
