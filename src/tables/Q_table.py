#!/usr/bin/env python3

from argparse import ArgumentParser, FileType

import numpy as np
import pandas as pd

from ..dump import combine_df_ufloats

def get_args():
    parser = ArgumentParser()

    parser.add_argument("data_filenames", nargs="+", help="Filename of flow log to analyse")
    parser.add_argument("--output_file", type=FileType("w"), default="-")
    return parser.parse_args()


def read_files(filenames):
    Q_data = []
    w0_data = []
    for filename in filenames:
        data = pd.read_csv(filename)
        if "Q0_value" in data.columns:
            Q_data.append(data)
        elif "w0_value" in data.columns:
            w0_data.append(data)
        else:
            raise ValueError("Unrecognised data in {filename}.")

    Q_df = pd.concat(Q_data)
    w0_df = pd.concat(w0_data)

    return pd.merge(Q_df, w0_df, on="ensemble_name")


def format_table(df):
    header = (
        "\\begin{tabular}{|c|c|c|c|c|c|c|}\n"
        "\\hline\\hline\n"
        r"Ensemble & $Q_0$ & $\sigma_Q$ & $\tau_{\mathrm{exp}}$ & "
        r"$N_{\mathrm{traj}}^{\mathrm{GF}}$ & $\delta_{\mathrm{traj}}^{\mathrm{GF}}$ & "
        "$w_0 / a$ \\\\\n"
        r"\hline"
    )
    footer = "\\hline\\hline\n\\end{tabular}"
    content = []
    previous_prefix = None
    for row in df.itertuples():
        if (next_prefix := row.ensemble_name[:4]) != previous_prefix:
            previous_prefix = next_prefix
            content.append("\\hline\n")

        if np.isnan(row.w0.nominal_value) or np.isnan(row.w0.std_dev):
            w0 = r"\cdots"
            num_configs = r"$\cdots"
            trajectory_step = r"$\cdots"
        else:
            w0 = f"{row.w0:.02uSL}"
            num_configs = row.num_configs
            trajectory_step = row.trajectory_step

        content.append(
            (
                "{} & ${:.02uSL}$ & ${:.02uSL}$ & ${:.02uSL}$ & {} & {} & ${}$ \\\\\n"
            ).format(
                row.ensemble_name,
                row.Q0,
                row.sigma_Q,
                row.tau_exp_Q,
                num_configs,
                trajectory_step,
                w0,
            )
        )

    return header + "".join(content) + footer


def main():
    args = get_args()
    data = combine_df_ufloats(read_files(args.data_filenames))
    print(format_table(data.sort_values(by="ensemble_name")), file=args.output_file)


if __name__ == "__main__":
    main()