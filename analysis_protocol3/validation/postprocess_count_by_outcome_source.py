import pandas as pd


INPUT_FILE = "output/safety_measures_count_validation.csv"
OUTPUT_FILE = "output/safety_count_by_outcome_source.csv"


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


COUNT_MEASURE_MAP = {
    "gp_consultation": "qa_gp_consultation",
    "ae_primary": "qa_ae_primary",
    "ae_non_primary": "qa_ae_non_primary",
    "hes_all_diagnoses": "qa_hes_all_diagnoses",
}


def get_numerator(df, measure_name, interval_start):
    rows = df[
        (df["measure"] == measure_name)
        & (df["interval_start"] == interval_start)
    ]

    if rows.empty:
        return None

    return rows["numerator"].iloc[0]


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

            for column_name, measure_prefix in COUNT_MEASURE_MAP.items():
                measure_name = f"{measure_prefix}_{outcome}"
                row[column_name] = get_numerator(df, measure_name, interval_start)

            rows.append(row)

    output = pd.DataFrame(rows)
    output.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()