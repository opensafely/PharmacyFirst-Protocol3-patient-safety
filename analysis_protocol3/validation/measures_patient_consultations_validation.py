from ehrql import case, create_measures, months, when
from analysis_protocol3.protocol3_dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(2).starting_on("2025-10-01"),
    # intervals=months(2).starting_on("2024-02-01")
)

measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

'''
Checks:
1. PF consultation count
- pf_consultation_general_total should capture all consultations with PF service codes.
- pf_consultation_general_butno_condition_total should be smaller than pf_consultation_general_total.
- pf_consultation_condition_sum_total should be compared with pf_consultation_general_total - pf_consultation_general_butno_condition_total.
- - If condition sum is larger, this suggests some PF consultations may be assigned to more than one condition.
2. PF consultation count vs same-day consultation count ('date')
- For each condition, pf_date_<condition> should be less than or equal to pf_consultation_<condition>.
3. GP consultation vs date
- For each condition, gp_date_<condition> should be less than or equal to gp_consultation_<condition>.
4. PF consultation count vs GP consultation count 
- compare by condition
- change by month
5. A&E variables
- ae_<condition>_primary_count should generally be low
- ae_<condition>_non_primary_flag may be higher than primary counts, but very high values may suggest broad diagnosis matching.
6. Among patients with PF consultations for a given condition, all of them should meet the corresponding eligibility criteria.
'''

measures.define_measure(
    name="pf_consultation_general_total",
    numerator=dataset.pf_consultation_general,
    denominator=measure_base_population,
)
measures.define_measure(
    name="pf_consultation_general_butno_condition_total",
    numerator=dataset.pf_consultation_general_butno_condition,
    denominator=measure_base_population,
)
pf_condition_consultation_sum = (
    dataset.numerator_pf_consultation_uti
    + dataset.numerator_pf_consultation_sinusitis
    + dataset.numerator_pf_consultation_insectbite
    + dataset.numerator_pf_consultation_otitismedia
    + dataset.numerator_pf_consultation_sorethroat
    + dataset.numerator_pf_consultation_shingles
    + dataset.numerator_pf_consultation_impetigo
)
measures.define_measure(
    name="pf_consultation_condition_sum_total",
    numerator=pf_condition_consultation_sum,
    denominator=measure_base_population,
)

pf_conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

for condition in pf_conditions:

    # check numerator only
    measures.define_measure(
        name=f"pf_consultation_{condition}",
        numerator=getattr(dataset, f"numerator_pf_consultation_{condition}"),
        denominator=measure_base_population,
    )

    # check numerator only
    measures.define_measure(
        name=f"gp_consultation_{condition}",
        numerator=getattr(dataset, f"numerator_gp_consultation_{condition}"),
        denominator=measure_base_population,
    )

    # check numerator only
    measures.define_measure(
        name=f"ae_{condition}_primary_count",
        numerator=getattr(dataset, f"ae_{condition}_primary_count"),
        denominator=measure_base_population,
    )

    # proportion of patients with ≥1 non-primary A&E diagnosis
    measures.define_measure(
        name=f"patient_has_non_primary_ae_{condition}",
        numerator=getattr(dataset, f"has_ae_{condition}_non_primary"),
        denominator=measure_base_population,
    )

# check numerator only
measures.define_measure(
    name="ae_attendance_total",
    numerator=dataset.ae_attendance_count,
    denominator=measure_base_population,
)

pf_condition_map = {
    "uti": "uuti",
    "sinusitis": "sinusitis",
    "insectbite": "insect_bites",
    "otitismedia": "otitis_media",
    "sorethroat": "sore_throat",
    "shingles": "shingles",
    "impetigo": "impetigo",
}

# retrive total number of appointments
########################################################
# Overall appointment totals
########################################################

measures.define_measure(
    name="appointment_scheduled_total",
    numerator=dataset.appointment_scheduled,
    denominator=measure_base_population,
)

measures.define_measure(
    name="appointment_seen_total",
    numerator=dataset.appointment_seen,
    denominator=measure_base_population,
)