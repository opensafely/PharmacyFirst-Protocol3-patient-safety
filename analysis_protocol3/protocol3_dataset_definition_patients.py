# This file defines the population and selects the fields that need to be included in the data for analysis. 
# Get new dummy tables: opensafely exec ehrql:v1 create-dummy-tables analysis/dataset_definition_patients.py dummy_tables
# gunzip -c output/dataset_definition_patients.csv.gz > output/dataset_definition_patients.csv

from ehrql import create_dataset, show, days, weeks, months, years, case, when, get_parameter
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events, addresses, 
                              ethnicity_from_sus,
                              emergency_care_attendances,appointments)
import analysis.codelists as codelists

from analysis.pf_variable_library import (get_imd, get_latest_ethnicity, 
                                          select_events_between, select_events_from_codelist, select_events_by_consultation_id,
                                          has_event_count, ae_non_primary_diagnosis_matches)
from ehrql import claim_permissions
claim_permissions("appointments")

dataset = create_dataset()
dataset.configure_dummy_data(population_size=500)

# One month time period (to start with this is Nov 25) 
# start_date = "2025-10-31"     
# index_date = "2025-11-30"  
start_date = get_parameter("start_date", default="2024-02-01")
index_date = start_date + months(1) - days(1)
# index_date = start_date + years(1)

"""
Monthly patient-level denominator + numerator dataset
Patient table key fields:
- Patient identifiers: patient_id, month (start_date, index_date), registration_status, alive_status, 
- Demographics: age, sex, ethnicity, IMD
- Practice info: practice_id, STP, region
- PF consultation count
- GP consultation count (conditions: 7 PF conditions + a control condition)
- Eligibility/clinical characteristics flag (True/False)
- A&E attendance
- Appointment count: scheduled; seen.

Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible: at least one condition

The above variables require:
- pregnant_this_month: True/False, developed by Helen
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti

A&E variables:
- total number of A&E attendances in month based on arrival_date
- for each PF condition, using GP wider SNOMED codelists, create variables for:
    - count of A&E attendances with primary diagnosis (diagnosis_01) match to the condition-specific GP codelist
    - flag for any non-primary diagnosis (diagnosis_02-24) match to the condition-specific GP codelist (T/F)

Appointment variables:
- total number of appointments that were scheduled to date in month (based on start_date)
- total number of appointments that were seen in month (based on seen_date)
       
Notes: 
- run for every month - specify parameters in .yaml
"""

########################################################
# Patient identifiers: alive_status, registration_status
alive = patients.is_alive_on(index_date) # alive at the end of month
alive_start = patients.is_alive_on(start_date) # alive at the start of month

# Only include the patient if they were registered for the whole month, 
# so registered before the month starts and not deregistered or died during the month
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()

# Demographics: sex, age, patient_imd
sex = patients.sex
age = patients.age_on(index_date)

# Define population
# base_population = patients.exists_for_patient()
age_valid = (patients.age_on(index_date) <= 120) # "Exclude any patients over 120 years old as the date of birth is most likely to be missing"
base_population = alive & registered_start & registered_index & age_valid 
dataset.define_population(base_population) # include all patients or those alive and registered

dataset.start_date = case(when(base_population).then(start_date))
dataset.index_date = case(when(base_population).then(index_date))
dataset.registered_start = registered_start
dataset.registered_index = registered_index
dataset.alive = alive
dataset.sex = sex
dataset.age = age
dataset.date_of_birth = patients.date_of_birth # debug

dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(index_date,clinical_events,codelists.ethnicity_group16_codelist,ethnicity_from_sus,grouping=16,)
# Patient identifiers: practice_id, stp, region
dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id
dataset.stp = practice_registrations.for_patient_on(index_date).practice_stp
# dataset.region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name
dataset.region = case(
    when(practice_registrations.for_patient_on(index_date).practice_nuts1_region_name.is_null()).then("Missing"),
    otherwise=practice_registrations.for_patient_on(index_date).practice_nuts1_region_name,
)
########################################################
'''
This section counts the number of PF consultations for each condition.
Outputs:
- pf_consultation_general: consultation count where their clinical events have any of the three general PF codes
- pf_consultation_general_butno_condition: consultation count where their clinical events have any of the three general PF codes BUT no PF condition codes
- numerator_pf_consultation_{name}: number of PF consultations for a specific PF condition
- numerator_pf_date_{name}: number of PF consultation dates for a specific PF condition
'''

selected_events = select_events_between(clinical_events, start_date, index_date)
pf_consultation_events = select_events_from_codelist(selected_events, codelists.pf_consultation_events_dict["pf_consultation_services_combined"])
# 'pf_ids' is a set of consultation ids where their clinical events have any of the three general PF codes
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = select_events_by_consultation_id(selected_events, pf_ids)

# dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
dataset.pf_consultation_general = pf_consultation_events.consultation_id.count_distinct_for_patient()

pf_conditions_pf_codes = {
    "uti": codelists.uti_code,
    "sinusitis": codelists.sinusitis_code,
    "insectbite": codelists.insectbite_code,
    "otitismedia": codelists.otitismedia_code,
    "sorethroat": codelists.sorethroat_code,
    "shingles": codelists.shingles_code,
    "impetigo": codelists.impetigo_code,
}

# a set of codes for any PF condition
pf_conditions_pf_code_set = []
for codes in pf_conditions_pf_codes.values():
    pf_conditions_pf_code_set += codes

# select events with both general PF codes and PF condition codes
pf_condition_events = selected_pf_id_events.where(selected_pf_id_events.snomedct_code.is_in(pf_conditions_pf_code_set))
# extract consultation IDs for these events
pf_condition_consultation_ids = pf_condition_events.consultation_id
# select PF consultation events (those with general PF codes) that the consultation id is not in the set of consultation ids with condition codes
pf_consultations_general_butno_condition_events = pf_consultation_events.where(
    ~pf_consultation_events.consultation_id.is_in(pf_condition_consultation_ids)
)
# count number of consultations from the above event selection
dataset.pf_consultation_general_butno_condition = (
    pf_consultations_general_butno_condition_events.consultation_id.count_distinct_for_patient()
)

for name, codes in pf_conditions_pf_codes.items():
    # count consultations and consultation dates
    count_pf_event, count_pf_consultation, count_pf_date = has_event_count(selected_pf_id_events, codes)
    setattr(dataset, f"numerator_pf_event_{name}", count_pf_event)
    setattr(dataset, f"numerator_pf_consultation_{name}", count_pf_consultation)
    setattr(dataset, f"numerator_pf_date_{name}", count_pf_date)

########################################################
'''
This section counts the number of GP consultations for PF-related conditions and control conditions, explicitly excluding consultations identified as PF consultations using general PF service codes.

Key logic:
- pf_ids' represents consultation IDs where at least one event contains a general PF service code.

1. 'gp_events_clean' is derived by excluding all events belonging to consultations in 'pf_ids'. 
- This ensures that GP consultation counts do not overlap with PF consultation counts.
2. Identify PF-related conditions in managed in GP using the condition-specific SNOMED codelists (e.g. UTI, sinusitis)
3. Consultations are counted using distinct consultation IDs per patient and consultation dates

Outputs:
- numerator_gp_consultation_{name}: number of GP consultations for a specific PF condition
- numerator_gp_date_{name}: number of GP consultation dates for a specific PF condition
'''

gp_events_clean = selected_events.where(
    ~selected_events.consultation_id.is_in(pf_ids)
)

pf_conditions_gp_codes = {
    "uti": codelists.gp_snomed_codelist_uti,
    "sinusitis": codelists.gp_snomed_codelist_sinusitis,
    "insectbite": codelists.gp_snomed_codelist_insect_bites,
    "otitismedia": codelists.gp_snomed_codelist_otitis_media,
    "sorethroat": codelists.gp_snomed_codelist_sore_throat,
    "shingles": codelists.gp_snomed_codelist_shingles,
    "impetigo": codelists.gp_snomed_codelist_impetigo,
}

# Combined definition: strict infected insect bites OR all insect bites
insectbite_all_or_strict_event_codes = (
    *codelists.gp_snomed_codelist_insect_bites_strict,
    *codelists.gp_snomed_codelist_insect_bites_all,
)

otherinsectbite_gp_codes = {
    "insectbite_strict": codelists.gp_snomed_codelist_insect_bites_strict,
    "insectbite_all": codelists.gp_snomed_codelist_insect_bites_all,
    "cellulitis_only": codelists.gp_snomed_codelist_cellulitis_only,
    "insectbite_strict_or_all": insectbite_all_or_strict_event_codes,
}

control_conditions_gp_codes = {
    "lowerbackpain": codelists.gp_snomed_codelist_lower_back_pain,
}

all_conditions_gp_codes = {
    **pf_conditions_gp_codes,
    **otherinsectbite_gp_codes,
    **control_conditions_gp_codes,
}

# for name, codes in pf_conditions_gp_codes.items():
for name, codes in all_conditions_gp_codes.items():
    count_gp_event, count_gp_consultation, count_gp_date = has_event_count(gp_events_clean, codes)
    setattr(dataset, f"numerator_gp_event_{name}", count_gp_event)
    setattr(dataset, f"numerator_gp_consultation_{name}", count_gp_consultation)
    setattr(dataset, f"numerator_gp_date_{name}", count_gp_date)

# ------------------------------------------------------
# Definition 5: at least one code from the all-insect-bites codelist AND at least one cellulitis code.
# ------------------------------------------------------
# Combined definition: all insect bites PLUS cellulitis
insectbite_all_and_cellulitis_event_codes = (
    *codelists.gp_snomed_codelist_insect_bites_all,
    *codelists.gp_snomed_codelist_cellulitis_only,
)
# Events with an all-insect-bites code
insectbite_all_events = gp_events_clean.where(
    gp_events_clean.snomedct_code.is_in(
        codelists.gp_snomed_codelist_insect_bites_all
    )
)
# Events with a cellulitis code
cellulitis_events = gp_events_clean.where(
    gp_events_clean.snomedct_code.is_in(
        codelists.gp_snomed_codelist_cellulitis_only
    )
)
cellulitis_ids = cellulitis_events.consultation_id
# Consultations containing both an all-insect-bites code AND a cellulitis code
insectbite_all_plus_cellulitis_ids = (
    insectbite_all_events.where(
        insectbite_all_events.consultation_id.is_in(cellulitis_ids)
    ).consultation_id
)
# Retain relevant insect-bite and cellulitis events
# from consultations satisfying definition 5
insectbite_all_plus_cellulitis_condition_events = gp_events_clean.where(
    gp_events_clean.consultation_id.is_in(
        insectbite_all_plus_cellulitis_ids
    )
    & gp_events_clean.snomedct_code.is_in(
        insectbite_all_and_cellulitis_event_codes
    )
)

dataset.numerator_gp_event_insectbite_all_plus_cellulitis = (
    insectbite_all_plus_cellulitis_condition_events.count_for_patient()
)

dataset.numerator_gp_consultation_insectbite_all_plus_cellulitis = (
    insectbite_all_plus_cellulitis_condition_events.consultation_id
    .count_distinct_for_patient()
)

dataset.numerator_gp_date_insectbite_all_plus_cellulitis = (
    insectbite_all_plus_cellulitis_condition_events.date
    .count_distinct_for_patient()
)

# ------------------------------------------------------
# Definition combined: strict, or, at least one code from the all-insect-bites codelist AND at least one cellulitis code.
# ------------------------------------------------------
# Combined definition: definition 2 OR definition 5
insectbite_strict_or_all_plus_cellulitis_events = gp_events_clean.where(
    # Events identified by the strict codelist (definition 2)
    (
        gp_events_clean.snomedct_code.is_in(codelists.gp_snomed_codelist_insect_bites_strict)
    )
    |
    # Relevant insect-bite plus cellulitis events from definition-5 consultations
    (
        gp_events_clean.consultation_id.is_in(insectbite_all_plus_cellulitis_ids)
        & gp_events_clean.snomedct_code.is_in(insectbite_all_and_cellulitis_event_codes)
    )
)
dataset.numerator_gp_event_insectbite_strict_or_all_plus_cellulitis = (
    insectbite_strict_or_all_plus_cellulitis_events.count_for_patient()
)

dataset.numerator_gp_consultation_insectbite_strict_or_all_plus_cellulitis = (
    insectbite_strict_or_all_plus_cellulitis_events.consultation_id
    .count_distinct_for_patient()
)

dataset.numerator_gp_date_insectbite_strict_or_all_plus_cellulitis = (
    insectbite_strict_or_all_plus_cellulitis_events.date
    .count_distinct_for_patient()
)

########################################################
"""
Clinical variables for eligible population denominator:
- pregnant_this_month
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti
"""

from analysis.pf_variable_library import check_code_in_time_window, check_recurrent_status
# -- pregnancy_status - naive version
# pregnant_this_month = check_code_in_time_window(index_date-months(1),index_date, clinical_events, codelists.gp_snomed_codelist_pregnancy)
# dataset.pregnant_this_month = pregnant_this_month
# -- pregancy_status developed by Helen
# look back for recent end-of-pregnancy codes -- assume no longer pregnant if in last 12 weeks
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_end_pregnancy) &
    clinical_events.date.is_on_or_between(start_date - weeks(32), start_date - days(1))
    ).sort_by(clinical_events.date).last_for_patient().date
# look ahead 40 weeks for end-of-pregnancy codes
dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_end_pregnancy) &
    clinical_events.date.is_on_or_between(start_date, start_date + weeks(40))
    ).sort_by(clinical_events.date).first_for_patient().date
# estimated date of delivery (EDD) - very recent or in future to estimate the known start of pregnancy
dataset.pregnancy_edd = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date - weeks(2), start_date + weeks(34)) &
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_pregnancy_edd)
    ).sort_by(clinical_events.date).first_for_patient().date
# recent "pregnant" codes - this is to be used where no delivery or EDD recorded
dataset.pregnancy_code = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_pregnancy) &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(4))
    ).sort_by(clinical_events.date).first_for_patient().date
# combine criteria to create a pregnancy status for the current month:
dataset.pregnant = case(
    # recent delivery -> not pregnant now:
    when(dataset.pregnancy_end_recent.is_on_or_after(start_date - weeks(12))).then("0-R"),
    # EDD in month or next 8 months, not preceeded by an end-of-pregnancy
    when(dataset.pregnancy_edd.is_not_null() 
        # check that the pregnancy linked to the EDD did not end very early,
        # i.e prior to the last 12 weeks which is already captured above
         & (dataset.pregnancy_end_recent.is_null() # no past delivery captured
            | ~dataset.pregnancy_end_recent.is_on_or_between(dataset.pregnancy_edd-weeks(28),dataset.pregnancy_edd+weeks(3))
            )).then("P-EDD"),
    # end of pregnancy in month or next 2 months - currently pregnant:
    when(dataset.pregnancy_end.is_on_or_before(start_date + weeks(12))).then("P-E"),
    # recent pregnancy code
    when(dataset.pregnancy_code.is_not_null()).then("P"),
    otherwise="0",)
# pregnant_this_month = dataset.pregnant.is_in(("P-E", "P-EDD", "P"))
# Age <= 11: pregnancy flags are considered too unreliable and are not counted as pregnant.
pregnant_this_month = (dataset.pregnant.is_in(("P-E", "P-EDD", "P")) & (age >= 12))
dataset.pregnant_this_month = pregnant_this_month

# Anchor date for impetigo exclusion
# anchor is the day before the monthly interval start
impetigo_exclusion_anchor_date = start_date

# bullous_impetigo in one month
# When start_date = 2025-10-01, impetigo_exclusion_anchor_date = 2025-10-01
# the lookback window is [2025-09-01, 2025-09-30]
# bullous_impetigo_this_month = check_code_in_time_window(start_date,index_date,clinical_events,codelists.gp_snomed_codelist_bullous_impetigo)
bullous_impetigo_last_month = check_code_in_time_window(
    impetigo_exclusion_anchor_date-months(1),
    impetigo_exclusion_anchor_date-days(1),
    clinical_events,
    codelists.gp_snomed_codelist_bullous_impetigo)
dataset.bullous_impetigo_last_month = bullous_impetigo_last_month

# recurrent_impetigo: (defined as 2 or more episodes in one year) 
# episodes are distinguished using 4 weeks gap, so any codes within 4 weeks are considered to be part of the same episode.
# For recurrent eligibility criteria, 
# we use the start of the study month as the anchor date and exclude the study month from the lookback window. 
# Therefore, criteria defined over N months are implemented as N-1 months before the anchor date, 
# ending on two weeks before the study month starts.
recurrent_impetigo_window_start = impetigo_exclusion_anchor_date - months(11)
recurrent_impetigo_window_end = impetigo_exclusion_anchor_date - days(15)
recurrent_impetigo_12m = check_recurrent_status(
    recurrent_impetigo_window_start, 
    recurrent_impetigo_window_end,
    clinical_events, 
    codelists.gp_snomed_codelist_impetigo,
    gap_weeks=4, 
    min_episodes=2)
dataset.recurrent_impetigo_12m = recurrent_impetigo_12m

# Anchor date for uti exclusion
# anchor is the day before the monthly interval start
uti_exclusion_anchor_date = start_date

# catheter_status: excluding patients who clearly have a catheter, and for following 12 months after code is included
catheter_12m = check_code_in_time_window(
    uti_exclusion_anchor_date - months(11),
    uti_exclusion_anchor_date - days(1),
    clinical_events,
    codelists.gp_snomed_codelist_urinary_catheter,
)
dataset.catheter_12m = catheter_12m

# recurrent_uti: (2 episodes in last 6 months, or 3 episodes in last 12 months) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
# To avoid counting consultations in the study month itself, 
# criteria defined over N months are implemented as N-1 months before the anchor date, 
# ending on one week before the study month starts.
recurrent_uti_6m_window_start = uti_exclusion_anchor_date - months(5)
recurrent_uti_12m_window_start = uti_exclusion_anchor_date - months(11)
recurrent_uti_window_end = uti_exclusion_anchor_date - days(8)
recurrent_uti_6m = check_recurrent_status(
    recurrent_uti_6m_window_start, 
    recurrent_uti_window_end,
    clinical_events, 
    codelists.gp_snomed_codelist_uti,
    gap_weeks=4, 
    min_episodes=2)
recurrent_uti_12m = check_recurrent_status(
    recurrent_uti_12m_window_start, 
    recurrent_uti_window_end,
    clinical_events, 
    codelists.gp_snomed_codelist_uti,
    gap_weeks=4, 
    min_episodes=3)
recurrent_uti = recurrent_uti_6m | recurrent_uti_12m
dataset.recurrent_uti_6m = recurrent_uti_6m
dataset.recurrent_uti_12m = recurrent_uti_12m
dataset.recurrent_uti = recurrent_uti

########################################################
"""
Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible
"""
female = patients.sex.is_in(["female"])

# Condition: acute otitis media
# - inclusion: children aged 1 to 17 years
# - exclusion: none
include_patient_otitis_media = (age >= 1) & (age <= 17) 
dataset.include_patient_otitis_media = include_patient_otitis_media

# Condition: acute sinusitis
# - inclusion: age >= 12
# - exclusion: none
include_patient_sinusitis = (age >= 12)
dataset.include_patient_sinusitis = include_patient_sinusitis

# Condition: acute sore throat
# - inclusion: age >= 5
# - exclusion: pregnant female under 16s
age_eligible_sore_throat = (age >= 5)
exclusion_sore_throat = pregnant_this_month & (age < 16) & (female)
include_patient_sore_throat = (age_eligible_sore_throat & ~exclusion_sore_throat)
dataset.include_patient_sore_throat = include_patient_sore_throat

# Condition: infected insect bites
# - inclusion: age >= 1
# - exclusion: pregnant female under 16s
age_eligible_insect_bites = (age >= 1)
exclusion_insect_bites = pregnant_this_month & (age < 16) & (female)
include_patient_insect_bites = (age_eligible_insect_bites & ~exclusion_insect_bites)
dataset.include_patient_insect_bites = include_patient_insect_bites

# Condition: shingles
# - inclusion: age >= 18
# - exclusion: pregnant female
age_eligible_shingles = (age >= 18)
exclusion_shingles = pregnant_this_month & (female)
include_patient_shingles = (age_eligible_shingles & ~exclusion_shingles)
dataset.include_patient_shingles = include_patient_shingles

# Condition: impetigo
# - inclusion: age >= 1
# - exclusion: 
# - - bullous impetigo, 
# - - recurrent impetigo (defined as 2 or more episodes in the same year), 
# - - pregnant female under 16 years
impetigo_age_eligible = (age >= 1)
impetigo_exclusion = (bullous_impetigo_last_month | recurrent_impetigo_12m | (pregnant_this_month & (age < 16) & female))
include_patient_impetigo = (impetigo_age_eligible & ~impetigo_exclusion)
dataset.include_patient_impetigo = include_patient_impetigo

# Condition: Uncomplicated UTI
# - inclusion: women aged 16 to 64 years
# - exclusion: 
# - - pregnant female
# - - urinary catheter
# - - recurrent UTI: 2 episodes in last 6 months, or 3 episodes in last 12 months
uuti_eligible = (age >= 16) & (age <= 64) & female
uuti_exclusion = (pregnant_this_month | catheter_12m | recurrent_uti)
include_patient_uuti = (uuti_eligible & ~uuti_exclusion)
dataset.include_patient_uuti = include_patient_uuti

# include_patient_overall_eligible
include_patient_overall_eligible = (include_patient_otitis_media|include_patient_sinusitis
                                  |include_patient_sore_throat|include_patient_insect_bites
                                  |include_patient_shingles|include_patient_impetigo|include_patient_uuti)
dataset.include_patient_overall_eligible = include_patient_overall_eligible
########################################################
'''A&E variables'''
# select A&E clinical events in month based on arrival date
ae_events = emergency_care_attendances.where(emergency_care_attendances.arrival_date.is_on_or_between(start_date, index_date))
# overall A&E attendances in month
dataset.ae_attendance_count = ae_events.count_for_patient()
# A&E PF-condition matching using GP codelists
# for name, codes in pf_conditions_gp_codes.items():
for name, codes in all_conditions_gp_codes.items(): 
    # primary diagnosis match
    ae_primary = ae_events.where(ae_events.diagnosis_01.is_in(codes))
    # non-primary diagnosis match
    ae_non_primary = ae_non_primary_diagnosis_matches(ae_events, codes)
    # count and flag
    setattr(dataset, f"ae_{name}_primary_count", ae_primary.count_for_patient())
    setattr(dataset, f"has_ae_{name}_non_primary", ae_non_primary)

########################################################
'''Appointments variables'''
# select attended appointments in month
dataset.appointment_scheduled = appointments.where(
    (appointments.start_date.is_on_or_between(start_date, index_date)) &
    (appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Patient Walked Out",
            "Did Not Attend"
        ]))
).count_for_patient()
dataset.appointment_seen = appointments.where(
    (appointments.seen_date.is_on_or_between(start_date, index_date)) &
    (appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Patient Walked Out",
            "Did Not Attend"
        ]))
).count_for_patient()
########################################################
'''
Safety outcomes recorded in GP clinical events.

For each safety outcome, identify matching SNOMED-coded clinical events within the monthly study period using the corresponding GP codelist.
The outputs are event and consultation counts; meeting on Sept 18 discussed about using consultation count as the primary numerator.
'''

safety_outcomes_gp_codes = {
    "pyelonephritis": codelists.gp_snomed_codelist_pyelonephritis,
    "sepsis": codelists.gp_snomed_codelist_sepsis,
    "cellulitis_insectbite": codelists.gp_snomed_codelist_cellulitis_only,
    "cellulitis_impetigo": codelists.gp_snomed_codelist_cellulitis_only,
    "quinsy": codelists.gp_snomed_codelist_quinsy,
    "post_herpetic_neuralgia": codelists.gp_snomed_codelist_post_herpetic_neuralgia,
    "mastoiditis": codelists.gp_snomed_codelist_mastoiditis,
    "meningitis_sinusitis": codelists.gp_snomed_codelist_meningitis, 
    "meningitis_om": codelists.gp_snomed_codelist_meningitis,
    "intracranial_abscess": codelists.gp_snomed_codelist_intracranial_abscess,
    "sinus_thrombosis_om": codelists.gp_snomed_codelist_sinus_thrombosis,
    "sinus_thrombosis_sinusitis": codelists.gp_snomed_codelist_sinus_thrombosis,
    "facial_nerve_paralysis": codelists.gp_snomed_codelist_facial_nerve_paralysis,
}

safety_gp_events = selected_events

for name, codes in safety_outcomes_gp_codes.items():
    count_gp_event, count_gp_consultation, _ = has_event_count(safety_gp_events, codes)
    setattr(dataset, f"numerator_gp_event_{name}", count_gp_event)
    setattr(dataset, f"numerator_gp_consultation_{name}", count_gp_consultation)

########################################################
"""
TODO:
Safety outcomes recorded in A&E attendance data.
These outcomes should be sourced from TPP.emergency_care_attendances:
https://docs.opensafely.org/ehrql/reference/schemas/tpp/#emergency_care_attendances

The diagnosis fields should be used to count in several ways:
- primary, non-primary, any dignosis fields as separate outputs
"""
















########################################################
"""
TODO:
Safety outcomes recorded in hospital admission data.
These outcomes should be sourced from TPP.apcs:
https://docs.opensafely.org/ehrql/reference/schemas/tpp/#apcs

The counting unit for condition-based hospital outcomes is spells. 
These diagnosis fields should be used to create seperate outputs:
- primary_diagnosis only
- non-primary
- all_diagnoses 

The all-cause hospitalisation count the number of admission dates in the monthly regardless of diagnosis.
"""



















########################################################
'''
TODO:
PGD contravention

'''















########################################################

show(dataset) # DEBUG: show the patients in the base population

########################################################
# Define measures for analysis