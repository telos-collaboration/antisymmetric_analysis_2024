#!/usr/bin/env python3

import matplotlib.pyplot as plt
from ..plots_common import standard_plot_main, channel_color


def plot(data):
    fig, ax = plt.subplots(1, 2, num="Figure_8", figsize=(12, 4), layout="constrained")

    ax[0].set_ylim(0, 1.4)
    ax[0].set_xlim(-1.08, -1.01)
    ax[0].set_xlabel(r"$am_0$")
    ax[0].set_ylabel(r"$am_{\rm M}$")

    ax[1].set_ylim(0, 1.4)
    ax[1].set_xlim(0, 0.17)
    ax[1].set_xlabel(r"$am_{\rm PCAC}$")
    ax[1].set_ylabel(r"$am_{\rm M}$")

    channels = ["ps", "v", "t", "av", "at", "s"]
    markers = "o^vsx+"

    for channel_idx, (channel, marker) in enumerate(zip(channels, markers)):
        to_plot = []
        bare_mass = []
        for datum in data:
            if "mPCAC_samples" not in datum:
                continue

            if f"{channel}_mass_samples" not in datum:
                continue

            X = datum["mPCAC_samples"].samples
            Y = datum[f"{channel}_mass_samples"].samples

            bare_mass.append(datum["mAS"])

            to_plot.append((Y.mean(), Y.std(), X.mean(), X.std()))

        y_values, y_errors, x_values, x_errors = zip(*to_plot)

        ax[0].errorbar(
            bare_mass,
            y_values,
            yerr=y_errors,
            ls="none",
            alpha=0.7,
            color=channel_color(channel),
            marker=marker,
        )

        ax[1].errorbar(
            x_values,
            y_values,
            xerr=x_errors,
            yerr=y_errors,
            ls="none",
            alpha=0.7,
            color=channel_color(channel),
            label=channel,
            marker=marker,
        )

    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig.legend(
        by_label.values(),
        by_label.keys(),
        loc="outside upper center",
        ncol=6,
        borderaxespad=0.2,
    )

    return fig


if __name__ == "__main__":
    standard_plot_main(plot)