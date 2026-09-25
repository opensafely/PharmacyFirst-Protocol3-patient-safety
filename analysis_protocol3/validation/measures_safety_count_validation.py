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
1. safety outcome variables
numerator_gp_event_*
numerator_gp_consultation_*
numerator_ae_primary_*
numerator_ae_non_primary_*
numerator_hes_primary_*
numerator_hes_non_primary_*
numerator_hes_all_diagnoses_*
numerator_hes_all_cause_hospitalisation
2. GP event vs consultation
3. A&E primary vs non-primary
4. HES primary / non-primary / all diagnoses
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

for outcome in safety_outcome_names:
    ####################################################
    # 1. GP: event vs consultation sanity check
    ####################################################

    measures.define_measure(
        name=f"qa_gp_event_{outcome}",
        numerator=getattr(dataset, f"numerator_gp_event_{outcome}"),
        denominator=measure_base_population,
    )

    measures.define_measure(
        name=f"qa_gp_consultation_{outcome}",
        numerator=getattr(dataset, f"numerator_gp_consultation_{outcome}"),
        denominator=measure_base_population,
    )

    ####################################################
    # 2. A&E: primary vs non-primary sanity check
    ####################################################

    measures.define_measure(
        name=f"qa_ae_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_ae_primary_{outcome}"),
        denominator=measure_base_population,
    )

    measures.define_measure(
        name=f"qa_ae_non_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_ae_non_primary_{outcome}"),
        denominator=measure_base_population,
    )

    ####################################################
    # 3. HES: primary vs non-primary vs all diagnoses
    ####################################################

    measures.define_measure(
        name=f"qa_hes_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_hes_primary_{outcome}"),
        denominator=measure_base_population,
    )

    measures.define_measure(
        name=f"qa_hes_non_primary_{outcome}",
        numerator=getattr(dataset, f"numerator_hes_non_primary_{outcome}"),
        denominator=measure_base_population,
    )

    measures.define_measure(
        name=f"qa_hes_all_diagnoses_{outcome}",
        numerator=getattr(dataset, f"numerator_hes_all_diagnoses_{outcome}"),
        denominator=measure_base_population,
    )

########################################################
# HES all-cause hospitalisation QA measure
########################################################

measures.define_measure(
    name="qa_hes_all_cause_hospitalisation",
    numerator=dataset.numerator_hes_all_cause_hospitalisation,
    denominator=measure_base_population,
)