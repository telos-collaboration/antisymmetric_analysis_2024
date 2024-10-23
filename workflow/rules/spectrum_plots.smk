from functools import partial


metadata = pd.read_csv("metadata/ensemble_metadata.csv")


def all_samples(wildcards, observables):
    return [
        f"intermediary_data/{dir_template}/{observable}_samples.json".format(**row)
        for observable in observables
        for row in metadata.to_dict(orient="records")
        if row["use_in_main_plots"]
        if row["use_smear"]
    ]

def mass_extp(wildcards, observables):
    return [
        f"intermediary_data/extrapolation_results/{observable}_samples.json".format(**row)
        for observable in observables
        for row in metadata.to_dict(orient="records")
        if row["use_in_main_plots"]
        if row["use_in_extrapolation"]
    ]

def volume_samples(wildcards, observables):
    return [
        f"intermediary_data/{dir_template}/{observable}_samples.json".format(**row)
        for observable in observables
        for row in metadata.to_dict(orient="records")
        if row["ASB4M3Ls"]
    ]

def ASB2s_samples(wildcards, observables):
    return [
        f"intermediary_data/{dir_template}/{observable}_samples.json".format(**row)
        for observable in observables
        for row in metadata.to_dict(orient="records")
        if row["ASB2s"]
    ]

rule plot_finite_volume:
    input:
        data=partial(volume_samples, observables=["meson_ps","meson_v"]),
        script="src/plots/finite_volume.py"
    output:
        plot="assets/plots/mps_mv_vs_mpsL.{plot_filetype}",
    conda:
        "../envs/flow_analysis.yml"
    shell:
        "python -m src.plots.finite_volume {input.data} --plot_styles {plot_styles} --plot_file {output.plot}"

rule plot_mpcac_vs_ratio:
    input:
        data=partial(ASB2s_samples, observables=["meson_ps","meson_v", "mpcac"]),
        script="src/plots/mpcac_vs_ratio.py"
    output:
        plot="assets/plots/mpsfps_vs_mpcac_b6p7.{plot_filetype}",
    conda:
        "../envs/flow_analysis.yml"
    shell:
        "python -m src.plots.mpcac_vs_ratio {input.data} --plot_styles {plot_styles} --plot_file {output.plot}"

rule plot_w0mps_vs_w0mv:
    input:
        data=partial(all_samples, observables=["w0", "smear_meson_ps", "smear_meson_v", "smear_meson_t","smear_meson_av","smear_meson_at","smear_meson_s", "gevp_smear_meson_rhoE1"]),
        fit_results=partial(mass_extp, observables=["v_extp_mass","t_extp_mass","av_extp_mass","at_extp_mass","s_extp_mass","rhoE1_extp_mass"]),
        script="src/plots/w0mps_vs_meson.py",
    output:
        plot="assets/plots/m2_all_con_sp4as.{plot_filetype}",
        plot2="assets/plots/meson_spectrum_con.{plot_filetype}"
    conda:
        "../envs/flow_analysis.yml"
    shell:
        "python -m src.plots.w0mps_vs_meson {input.data} --plot_styles {plot_styles} --plot_file {output.plot} --plot_file2 {output.plot2} --fit_parameters {input.fit_results}"
