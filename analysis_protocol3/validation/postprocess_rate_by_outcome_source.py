import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


INPUT_FILE = "output/safety_measures_rate_validation.csv"
OUTPUT_FILE = "output/safety_rate_by_outcome_source.csv"

GP_NUMERATOR_PLOT_FILE = "output/safety_numerator_gp_consultation_by_month.png"
AE_NUMERATOR_PLOT_FILE = "output/safety_numerator_ae_primary_non_primary_by_month.png"
HES_NUMERATOR_PLOT_FILE = "output/safety_numerator_hes_primary_non_primary_by_month.png"


SAFETY_OUTCOMES = [
    "pyelonephritis",
    "sepsis",
    "cellulitis_insectbite",
    "cellulitis_impetigo",
    "quinsy",
    "post_herpetic_neuralgia",
    "mastoiditis",
    "meningitis_sinusitis",
    "meningitis_om",
    "intracranial_abscess",
    "sinus_thrombosis_om",
    "sinus_thrombosis_sinusitis",
    "facial_nerve_paralysis",
]


RATE_MEASURE_MAP = {
    "gp_consultation_rate": "rate_gp_consultation",
    "ae_primary_rate": "rate_ae_primary",
    "ae_non_primary_rate": "rate_ae_non_primary",
    "hes_primary_rate": "rate_hes_primary",
    "hes_non_primary_rate": "rate_hes_non_primary",
    "hes_all_diagnoses_rate": "rate_hes_all_diagnoses",
}


def get_measure_row(df, measure_name, interval_start):
    rows = df[
        (df["measure"] == measure_name)
        & (df["interval_start"] == interval_start)
    ]

    if rows.empty:
        return None

    return rows.iloc[0]


def format_month_label(interval_start):
    return pd.to_datetime(interval_start).strftime("%b %Y")


def create_single_numerator_plot(output, numerator_column, title, ylabel, plot_file):
    intervals = sorted(output["interval_start"].unique())
    x = np.arange(len(SAFETY_OUTCOMES))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, interval_start in enumerate(intervals):
        month_data = (
            output[output["interval_start"] == interval_start]
            .set_index("outcome")
            .reindex(SAFETY_OUTCOMES)
        )

        values = month_data[numerator_column].fillna(0).values
        offset = (i - (len(intervals) - 1) / 2) * width

        ax.bar(
            x + offset,
            values,
            width=width,
            label=format_month_label(interval_start),
        )

    ax.set_title(title)
    ax.set_xlabel("Outcome")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(SAFETY_OUTCOMES, rotation=45, ha="right")
    ax.legend(title="Month")

    plt.tight_layout()
    plt.savefig(plot_file, dpi=300)
    plt.close()


def create_stacked_numerator_plot(
    output,
    primary_numerator_column,
    non_primary_numerator_column,
    title,
    primary_label,
    non_primary_label,
    plot_file,
):
    intervals = sorted(output["interval_start"].unique())
    x = np.arange(len(SAFETY_OUTCOMES))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, interval_start in enumerate(intervals):
        month_data = (
            output[output["interval_start"] == interval_start]
            .set_index("outcome")
            .reindex(SAFETY_OUTCOMES)
        )

        primary_values = month_data[primary_numerator_column].fillna(0).values
        non_primary_values = month_data[non_primary_numerator_column].fillna(0).values

        offset = (i - (len(intervals) - 1) / 2) * width
        month_label = format_month_label(interval_start)

        ax.bar(
            x + offset,
            primary_values,
            width=width,
            label=f"{month_label}: {primary_label}",
        )

        ax.bar(
            x + offset,
            non_primary_values,
            width=width,
            bottom=primary_values,
            label=f"{month_label}: {non_primary_label}",
        )

    ax.set_title(title)
    ax.set_xlabel("Outcome")
    ax.set_ylabel("Numerator count")
    ax.set_xticks(x)
    ax.set_xticklabels(SAFETY_OUTCOMES, rotation=45, ha="right")
    ax.legend(title="Month and diagnosis type")

    plt.tight_layout()
    plt.savefig(plot_file, dpi=300)
    plt.close()


def create_plots(output):
    create_single_numerator_plot(
        output=output,
        numerator_column="gp_consultation_rate_numerator",
        title="GP consultation safety outcome numerator counts",
        ylabel="Numerator count",
        plot_file=GP_NUMERATOR_PLOT_FILE,
    )

    create_stacked_numerator_plot(
        output=output,
        primary_numerator_column="ae_primary_rate_numerator",
        non_primary_numerator_column="ae_non_primary_rate_numerator",
        title="A&E primary and non-primary safety outcome numerator counts",
        primary_label="primary",
        non_primary_label="non-primary",
        plot_file=AE_NUMERATOR_PLOT_FILE,
    )

    create_stacked_numerator_plot(
        output=output,
        primary_numerator_column="hes_primary_rate_numerator",
        non_primary_numerator_column="hes_non_primary_rate_numerator",
        title="HES primary and non-primary safety outcome numerator counts",
        primary_label="primary",
        non_primary_label="non-primary",
        plot_file=HES_NUMERATOR_PLOT_FILE,
    )


def main():
    df = pd.read_csv(INPUT_FILE)

    rows = []

    for interval_start in sorted(df["interval_start"].unique()):
        interval_rows = df[df["interval_start"] == interval_start]
        interval_end = interval_rows["interval_end"].iloc[0]

        for outcome in SAFETY_OUTCOMES:
            row = {
                "interval_start": interval_start,
                "interval_end": interval_end,
                "outcome": outcome,
            }

            denominator = None

            for column_name, measure_prefix in RATE_MEASURE_MAP.items():
                measure_name = f"{measure_prefix}_{outcome}"
                measure_row = get_measure_row(df, measure_name, interval_start)

                if measure_row is None:
                    row[column_name] = None
                    row[f"{column_name}_numerator"] = None
                    continue

                row[column_name] = measure_row["ratio"]
                row[f"{column_name}_numerator"] = measure_row["numerator"]

                if denominator is None:
                    denominator = measure_row["denominator"]

            row["denominator"] = denominator
            rows.append(row)

    output = pd.DataFrame(rows)
    output.to_csv(OUTPUT_FILE, index=False)

    create_plots(output)


if __name__ == "__main__":
    main()