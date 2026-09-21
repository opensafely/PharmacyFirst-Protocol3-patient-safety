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
preliminary rates using condition-specific denominators
'''

safety_outcome_names = [
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

safety_outcome_denominator_map = {
    "pyelonephritis": dataset.include_patient_uuti,
    "sepsis": dataset.include_patient_overall_eligible,
    "cellulitis_insectbite": dataset.include_patient_insect_bites,
    "cellulitis_impetigo": dataset.include_patient_impetigo,
    "quinsy": dataset.include_patient_sore_throat,
    "post_herpetic_neuralgia": dataset.include_patient_shingles,
    "mastoiditis": dataset.include_patient_otitis_media,
    "meningitis_sinusitis": dataset.include_patient_sinusitis,
    "meningitis_om": dataset.include_patient_otitis_media,
    "intracranial_abscess": dataset.include_patient_otitis_media,
    "sinus_thrombosis_om": dataset.include_patient_otitis_media,
    "sinus_thrombosis_sinusitis": dataset.include_patient_sinusitis,
    "facial_nerve_paralysis": dataset.include_patient_otitis_media,
}

for outcome, denominator in safety_outcome_denominator_map.items():
    condition_specific_denominator = denominator & measure_base_population

    ####################################################
    # GP preliminary rates
    # Primary numerator likely to be consultation count
    ####################################################

    measures.define_measure(
        name=f"rate_gp_event_{outcome}",
        numerator=getattr(dataset, f"numerator_gp_event_{outcome}"),
        denominator=condition_specific_denominator,
    )

    measures.define_measure(
        name=f"rate_gp_consultation_{outcome}",
        numerator=getattr(dataset, f"numerator_gp_consultation_{outcome}"),
        denominator=condition_specific_denominator,
    )

    ####################################################
    # A&E preliminary rates
    ####################################################

    measures.define_measure(
        name=f"rate_ae_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_ae_primary_{outcome}"),
        denominator=condition_specific_denominator,
    )

    measures.define_measure(
        name=f"rate_ae_non_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_ae_non_primary_{outcome}"),
        denominator=condition_specific_denominator,
    )

    ####################################################
    # HES preliminary rates
    ####################################################

    measures.define_measure(
        name=f"rate_hes_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_hes_primary_{outcome}"),
        denominator=condition_specific_denominator,
    )

    measures.define_measure(
        name=f"rate_hes_non_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_hes_non_primary_{outcome}"),
        denominator=condition_specific_denominator,
    )

    measures.define_measure(
        name=f"rate_hes_all_diagnoses_{outcome}",
        numerator=getattr(dataset, f"numerator_hes_all_diagnoses_{outcome}"),
        denominator=condition_specific_denominator,
    )

########################################################
# All-cause hospitalisation preliminary rate
########################################################

measures.define_measure(
    name="rate_hes_all_cause_hospitalisation",
    numerator=dataset.numerator_hes_all_cause_hospitalisation,
    denominator=dataset.include_patient_overall_eligible & measure_base_population,
)