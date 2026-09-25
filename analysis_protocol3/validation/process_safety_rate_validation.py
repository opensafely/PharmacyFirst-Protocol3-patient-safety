import pandas as pd


INPUT_FILE = "output/safety_measures_rate_validation.csv"
SUMMARY_FILE = "output/safety_rate_validation_summary.csv"
FLAGS_FILE = "output/safety_rate_validation_flags.csv"


RATE_WARNING_THRESHOLD = 0.01


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


SHARED_OUTCOME_PAIRS = [
    ("cellulitis_insectbite", "cellulitis_impetigo"),
    ("meningitis_sinusitis", "meningitis_om"),
    ("sinus_thrombosis_sinusitis", "sinus_thrombosis_om"),
]


MEASURE_PREFIXES = [
    "rate_gp_event",
    "rate_gp_consultation",
    "rate_ae_primary",
    "rate_ae_non_primary",
    "rate_hes_primary",
    "rate_hes_non_primary",
    "rate_hes_all_diagnoses",
]


def get_row(df, measure_name, interval_start):
    rows = df[
        (df["measure"] == measure_name)
        & (df["interval_start"] == interval_start)
    ]

    if rows.empty:
        return None

    return rows.iloc[0]


def add_flag(flags, interval_start, measure, check, status, detail):
    flags.append(
        {
            "interval_start": interval_start,
            "measure": measure,
            "check": check,
            "status": status,
            "detail": detail,
        }
    )


def parse_measure_name(measure):
    for prefix in MEASURE_PREFIXES:
        marker = f"{prefix}_"
        if measure.startswith(marker):
            return prefix, measure[len(marker):]

    if measure == "rate_hes_all_cause_hospitalisation":
        return "rate_hes_all_cause", "all_cause_hospitalisation"

    return "unknown", measure


def main():
    df = pd.read_csv(INPUT_FILE)

    summary = df[
        ["interval_start", "interval_end", "measure", "numerator", "denominator", "ratio"]
    ].copy()

    parsed = summary["measure"].apply(parse_measure_name)
    summary["measure_type"] = parsed.apply(lambda x: x[0])
    summary["outcome"] = parsed.apply(lambda x: x[1])

    summary.to_csv(SUMMARY_FILE, index=False)

    flags = []

    for _, row in summary.iterrows():
        measure = row["measure"]
        interval_start = row["interval_start"]
        numerator = row["numerator"]
        denominator = row["denominator"]
        ratio = row["ratio"]

        if pd.isna(denominator):
            add_flag(
                flags,
                interval_start,
                measure,
                "denominator_missing",
                "FAIL",
                "Denominator is missing.",
            )
            continue

        if denominator == 0:
            add_flag(
                flags,
                interval_start,
                measure,
                "denominator_zero",
                "FAIL",
                "Denominator is zero.",
            )
            continue

        if pd.isna(ratio):
            add_flag(
                flags,
                interval_start,
                measure,
                "ratio_missing",
                "WARNING",
                f"Ratio is missing despite denominator={denominator}.",
            )
            continue

        if ratio > RATE_WARNING_THRESHOLD:
            add_flag(
                flags,
                interval_start,
                measure,
                "rate_high",
                "WARNING",
                f"Rate is {ratio:.6f}, above threshold {RATE_WARNING_THRESHOLD:.6f}. Numerator={numerator}, denominator={denominator}.",
            )
        else:
            add_flag(
                flags,
                interval_start,
                measure,
                "rate_not_high",
                "PASS",
                f"Rate is {ratio:.6f}. Numerator={numerator}, denominator={denominator}.",
            )

    for interval_start in sorted(summary["interval_start"].unique()):
        for outcome_a, outcome_b in SHARED_OUTCOME_PAIRS:
            for prefix in MEASURE_PREFIXES:
                measure_a = f"{prefix}_{outcome_a}"
                measure_b = f"{prefix}_{outcome_b}"

                row_a = get_row(summary, measure_a, interval_start)
                row_b = get_row(summary, measure_b, interval_start)

                if row_a is None or row_b is None:
                    continue

                numerator_a = row_a["numerator"]
                numerator_b = row_b["numerator"]
                denominator_a = row_a["denominator"]
                denominator_b = row_b["denominator"]
                ratio_a = row_a["ratio"]
                ratio_b = row_b["ratio"]

                if numerator_a != numerator_b:
                    add_flag(
                        flags,
                        interval_start,
                        f"{measure_a}_vs_{measure_b}",
                        "shared_outcome_numerator_match",
                        "WARNING",
                        f"Numerators differ: {measure_a}={numerator_a}, {measure_b}={numerator_b}. These use the same codelist and should usually match before denominators are applied.",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"{measure_a}_vs_{measure_b}",
                        "shared_outcome_numerator_match",
                        "PASS",
                        f"Numerators match at {numerator_a}.",
                    )

                if denominator_a == denominator_b:
                    add_flag(
                        flags,
                        interval_start,
                        f"{measure_a}_vs_{measure_b}",
                        "shared_outcome_denominator_difference",
                        "INFO",
                        f"Denominators are the same ({denominator_a}). This may be expected for some paired outcomes but should be checked.",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"{measure_a}_vs_{measure_b}",
                        "shared_outcome_denominator_difference",
                        "PASS",
                        f"Denominators differ as expected: {measure_a}={denominator_a}, {measure_b}={denominator_b}.",
                    )

                if ratio_a == ratio_b:
                    add_flag(
                        flags,
                        interval_start,
                        f"{measure_a}_vs_{measure_b}",
                        "shared_outcome_rate_difference",
                        "INFO",
                        f"Rates are the same ({ratio_a}). This may happen if denominators are the same or numerators are zero.",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"{measure_a}_vs_{measure_b}",
                        "shared_outcome_rate_difference",
                        "PASS",
                        f"Rates differ: {measure_a}={ratio_a}, {measure_b}={ratio_b}.",
                    )

    flags_df = pd.DataFrame(flags)
    flags_df.to_csv(FLAGS_FILE, index=False)


if __name__ == "__main__":
    main()