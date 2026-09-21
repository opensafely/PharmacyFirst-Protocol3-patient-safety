import pandas as pd


INPUT_FILE = "output/safety_measures_count_validation.csv"
SUMMARY_FILE = "output/safety_count_validation_summary.csv"
FLAGS_FILE = "output/safety_count_validation_flags.csv"


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


def get_numerator(df, measure_name, interval_start):
    rows = df[
        (df["measure"] == measure_name)
        & (df["interval_start"] == interval_start)
    ]

    if rows.empty:
        return None

    return rows["numerator"].iloc[0]


def add_flag(flags, interval_start, check, status, detail):
    flags.append(
        {
            "interval_start": interval_start,
            "check": check,
            "status": status,
            "detail": detail,
        }
    )


def main():
    df = pd.read_csv(INPUT_FILE)

    # Keep a tidy summary version of the raw measures output.
    summary = df[
        ["interval_start", "interval_end", "measure", "numerator", "denominator", "ratio"]
    ].copy()
    summary.to_csv(SUMMARY_FILE, index=False)

    flags = []

    for interval_start in sorted(df["interval_start"].unique()):
        for outcome in SAFETY_OUTCOMES:
            gp_event = get_numerator(
                df,
                f"qa_gp_event_{outcome}",
                interval_start,
            )
            gp_consultation = get_numerator(
                df,
                f"qa_gp_consultation_{outcome}",
                interval_start,
            )

            if gp_event is not None and gp_consultation is not None:
                if gp_event < gp_consultation:
                    add_flag(
                        flags,
                        interval_start,
                        f"gp_event_ge_consultation_{outcome}",
                        "FAIL",
                        f"GP event count ({gp_event}) is smaller than GP consultation count ({gp_consultation}).",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"gp_event_ge_consultation_{outcome}",
                        "PASS",
                        f"GP event count ({gp_event}) >= GP consultation count ({gp_consultation}).",
                    )

            ae_primary = get_numerator(
                df,
                f"qa_ae_primary_{outcome}",
                interval_start,
            )
            ae_non_primary = get_numerator(
                df,
                f"qa_ae_non_primary_{outcome}",
                interval_start,
            )

            if ae_primary is not None and ae_non_primary is not None:
                if ae_primary == 0 and ae_non_primary == 0:
                    add_flag(
                        flags,
                        interval_start,
                        f"ae_all_zero_{outcome}",
                        "WARNING",
                        "A&E primary and non-primary counts are both zero. Check whether A&E diagnosis fields use compatible codelists.",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"ae_any_nonzero_{outcome}",
                        "PASS",
                        f"A&E primary={ae_primary}, non-primary={ae_non_primary}.",
                    )

            hes_primary = get_numerator(
                df,
                f"qa_hes_primary_{outcome}",
                interval_start,
            )
            hes_non_primary = get_numerator(
                df,
                f"qa_hes_non_primary_{outcome}",
                interval_start,
            )
            hes_all = get_numerator(
                df,
                f"qa_hes_all_diagnoses_{outcome}",
                interval_start,
            )

            if (
                hes_primary is not None
                and hes_non_primary is not None
                and hes_all is not None
            ):
                if hes_all < hes_primary:
                    add_flag(
                        flags,
                        interval_start,
                        f"hes_all_ge_primary_{outcome}",
                        "FAIL",
                        f"HES all diagnoses count ({hes_all}) is smaller than primary count ({hes_primary}).",
                    )

                if hes_all < hes_non_primary:
                    add_flag(
                        flags,
                        interval_start,
                        f"hes_all_ge_non_primary_{outcome}",
                        "FAIL",
                        f"HES all diagnoses count ({hes_all}) is smaller than non-primary count ({hes_non_primary}).",
                    )

                if hes_primary + hes_non_primary != hes_all:
                    add_flag(
                        flags,
                        interval_start,
                        f"hes_primary_plus_non_primary_eq_all_{outcome}",
                        "WARNING",
                        f"Primary ({hes_primary}) + non-primary ({hes_non_primary}) != all diagnoses ({hes_all}).",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"hes_primary_plus_non_primary_eq_all_{outcome}",
                        "PASS",
                        f"Primary ({hes_primary}) + non-primary ({hes_non_primary}) = all diagnoses ({hes_all}).",
                    )

        for outcome_a, outcome_b in SHARED_OUTCOME_PAIRS:
            for prefix in [
                "qa_gp_event",
                "qa_gp_consultation",
                "qa_ae_primary",
                "qa_ae_non_primary",
                "qa_hes_primary",
                "qa_hes_non_primary",
                "qa_hes_all_diagnoses",
            ]:
                value_a = get_numerator(
                    df,
                    f"{prefix}_{outcome_a}",
                    interval_start,
                )
                value_b = get_numerator(
                    df,
                    f"{prefix}_{outcome_b}",
                    interval_start,
                )

                if value_a is None or value_b is None:
                    continue

                if value_a != value_b:
                    add_flag(
                        flags,
                        interval_start,
                        f"shared_outcome_match_{prefix}_{outcome_a}_vs_{outcome_b}",
                        "WARNING",
                        f"{prefix}_{outcome_a} ({value_a}) != {prefix}_{outcome_b} ({value_b}). These use the same codelist and should usually match before denominators are applied.",
                    )
                else:
                    add_flag(
                        flags,
                        interval_start,
                        f"shared_outcome_match_{prefix}_{outcome_a}_vs_{outcome_b}",
                        "PASS",
                        f"Both values are {value_a}.",
                    )

    flags_df = pd.DataFrame(flags)
    flags_df.to_csv(FLAGS_FILE, index=False)


if __name__ == "__main__":
    main()