#!/usr/bin/env python3

import matplotlib.pyplot as plt

from ..plots_common import (
    standard_plot_main,
    beta_iterator,
    add_figure_legend,
    ONE_COLUMN,
)


def plot(data, **kwargs):
    fig, ax = plt.subplots(layout="constrained", figsize=(ONE_COLUMN, 3.0))

    ax.set_xlabel(r"$\hat{m}_{\mathrm{PCAC}}$")
    ax.set_ylabel(r"$w_0 / a$")

    betas = sorted(set([datum["beta"] for datum in data]))
    for beta, colour, marker in beta_iterator(betas):
        to_plot = []
        for datum in data:
            if datum["beta"] != beta:
                continue
            if "w0_samples" not in datum or "mPCAC_samples" not in datum:
                continue

            w0_value = datum["w0_samples"].mean
            w0_error = datum["w0_samples"].std()
            w0_mPCAC = datum["w0_samples"] * datum["mPCAC_samples"]
            to_plot.append((w0_value, w0_error, w0_mPCAC.mean, w0_mPCAC.std()))

        y_values, y_errors, x_values, x_errors = zip(*to_plot)
        ax.errorbar(
            x_values,
            y_values,
            xerr=x_errors,
            yerr=y_errors,
            ls="none",
            color=colour,
            marker=marker,
            label=f"{beta}",
        )

    ax.set_xlim(0, None)
    ax.set_ylim(0, None)

    add_figure_legend(fig)
    return fig


if __name__ == "__main__":
    standard_plot_main(plot)
