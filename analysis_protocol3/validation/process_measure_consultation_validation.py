import pandas as pd
import matplotlib.pyplot as plt

input_file = "output/patient_measures_consultation_validation.csv"
output_file = "output/patient_measures_consultation_validation_ordered.csv"

df = pd.read_csv(input_file)

########################################################
# Define measure order
########################################################

measure_order = [

    # PF overall totals
    "pf_consultation_general_total",
    "pf_consultation_general_butno_condition_total",
    "pf_consultation_condition_sum_total",

    # PF consultation counts
    "pf_consultation_uti",
    "pf_consultation_sinusitis",
    "pf_consultation_insectbite",
    "pf_consultation_otitismedia",
    "pf_consultation_sorethroat",
    "pf_consultation_shingles",
    "pf_consultation_impetigo",

    # GP consultations
    "gp_consultation_uti",
    "gp_consultation_sinusitis",
    "gp_consultation_insectbite",
    "gp_consultation_otitismedia",
    "gp_consultation_sorethroat",
    "gp_consultation_shingles",
    "gp_consultation_impetigo",

    # A&E primary
    "ae_attendance_total",
    "ae_uti_primary_count",
    "ae_sinusitis_primary_count",
    "ae_insectbite_primary_count",
    "ae_otitismedia_primary_count",
    "ae_sorethroat_primary_count",
    "ae_shingles_primary_count",
    "ae_impetigo_primary_count",

    # A&E non-primary
    "patient_has_non_primary_ae_uti",
    "patient_has_non_primary_ae_sinusitis",
    "patient_has_non_primary_ae_insectbite",
    "patient_has_non_primary_ae_otitismedia",
    "patient_has_non_primary_ae_sorethroat",
    "patient_has_non_primary_ae_shingles",
    "patient_has_non_primary_ae_impetigo",

    # Eligibility among PF consultation
    "pf_uti_eligible_among_pf_consultation",
    "pf_sinusitis_eligible_among_pf_consultation",
    "pf_insectbite_eligible_among_pf_consultation",
    "pf_otitismedia_eligible_among_pf_consultation",
    "pf_sorethroat_eligible_among_pf_consultation",
    "pf_shingles_eligible_among_pf_consultation",
    "pf_impetigo_eligible_among_pf_consultation",

    # Overall appointment totals
    "appointment_scheduled_total",
    "appointment_seen_total",
]

########################################################
# Apply ordering
########################################################

df["measure_order"] = df["measure"].apply(
    lambda x: measure_order.index(x) if x in measure_order else 999
)

df = df.sort_values(
    by=[
        "interval_start",
        "measure_order",
        "measure",
    ]
)

########################################################
# Save ordered output
########################################################
df = df.drop(columns=["measure_order"])
df.to_csv(output_file, index=False)

########################################################
# Condition-level validation summary table
########################################################

conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

summary_rows = []
months = sorted(df["interval_start"].unique())

for month in months:
    month_df = df[df["interval_start"] == month]

    def get_value(measure_name, column="numerator"):
        result = month_df.loc[month_df["measure"] == measure_name, column]
        if len(result) == 0:
            return None
        return result.iloc[0]

    for condition in conditions:
        eligibility_measure = f"pf_{condition}_eligible_among_pf_consultation"

        eligibility_numerator = get_value(eligibility_measure,column="numerator",)

        eligibility_denominator = get_value(eligibility_measure,column="denominator",)

        eligibility_ratio = get_value(eligibility_measure,column="ratio",)

        summary_rows.append({
            "month": month,
            "condition": condition,

            "pf_consultation": get_value(f"pf_consultation_{condition}"),
            "gp_consultation": get_value(f"gp_consultation_{condition}"),
            "ae_primary_count": get_value(f"ae_{condition}_primary_count"),
            "patient_has_non_primary_ae": get_value(f"patient_has_non_primary_ae_{condition}"),

            # Keep these for disclosure control of the ratio
            "pf_consultation_eligibility_ratio": eligibility_ratio, # Proportion of PF consultation patients who were eligible
            "pf_consultation_eligibility_numerator": eligibility_numerator, # Patients eligible for this PF condition
            "pf_consultation_eligibility_denominator": eligibility_denominator, # Patients with at least one PF consultation for this condition

        })

summary_df = pd.DataFrame(summary_rows)

summary_df.to_csv(
    "output/patient_measures_consultation_validation_summary.csv",
    index=False,
)

########################################################
# PF consultation counts by condition
########################################################

plot_df = df[df["measure"].str.startswith("pf_consultation_")].copy()

# exclude overall totals
plot_df = plot_df[
    ~plot_df["measure"].isin([
        "pf_consultation_general_total",
        "pf_consultation_general_butno_condition_total",
        "pf_consultation_condition_sum_total",
    ])
]

# simplify condition names
plot_df["condition"] = (plot_df["measure"].str.replace("pf_consultation_", "", regex=False))

# use month label
plot_df["month"] = pd.to_datetime(plot_df["interval_start"]).dt.strftime("%Y-%m")

# pivot for plotting
plot_pivot = plot_df.pivot(index="condition",columns="month",values="numerator",)
ax = plot_pivot.plot(kind="bar",figsize=(10, 6),)
ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.7,
)
ax.set_ylabel("PF consultation count")
ax.set_xlabel("Condition")
ax.set_title("PF consultation count by condition and month")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/patient_measures_pf_consultations_by_condition.png",dpi=300,)
plt.close()

########################################################
# GP consultation counts by condition
########################################################

plot_df = df[df["measure"].str.startswith("gp_consultation_")].copy()

# simplify condition names
plot_df["condition"] = (plot_df["measure"].str.replace("gp_consultation_", "", regex=False))

# use month label
plot_df["month"] = pd.to_datetime(plot_df["interval_start"]).dt.strftime("%Y-%m")

# pivot for plotting
plot_pivot = plot_df.pivot(index="condition",columns="month",values="numerator",)

ax = plot_pivot.plot(kind="bar",figsize=(10, 6),)
ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.7,
)
ax.set_ylabel("GP consultation count")
ax.set_xlabel("Condition")
ax.set_title("GP consultation count by condition and month")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/patient_measures_gp_consultation_by_condition.png", dpi=300,)
plt.close()