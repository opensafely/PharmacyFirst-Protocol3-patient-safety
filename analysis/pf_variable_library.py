# Functions to check status of a condition within a specified time window etc
# Copy from https://github.com/opensafely/pharmacy-first/blob/main/analysis/pf_variables_library.py

from ehrql import months, days, weeks
from ehrql.tables.tpp import (case,when)

# copied from dataset_definition.py
def get_imd(addresses, index_date):
    """
    copied from https://github.com/opensafely/pharmacy-first/blob/main/analysis/pf_dataset.py
    Date: 26 Feb 2026
    """
    imd_rounded = addresses.for_patient_on(index_date).imd_rounded
    max_imd = 32844
    imd_quintile = case(
        when((imd_rounded >= 0) & (imd_rounded < int(max_imd * 1 / 5))).then("1 (Most Deprived)"),
        when(imd_rounded < int(max_imd * 2 / 5)).then("2"),
        when(imd_rounded < int(max_imd * 3 / 5)).then("3"),
        when(imd_rounded < int(max_imd * 4 / 5)).then("4"),
        when(imd_rounded <= max_imd).then("5 (Least Deprived)"),
        otherwise="Missing",
    )
    return imd_quintile

def check_code_in_time_window(start_date, end_date, selected_events, codelist):
    """
    Returns True if a patient has any code from the given codelist
    recorded between start_date and end_date (inclusive).
    """
    return (
        selected_events
        .where(selected_events.snomedct_code.is_in(codelist))
        .where(selected_events.date.is_on_or_between(start_date, end_date))
        .exists_for_patient()
    )

def get_recurrent_anchor_date(start_date, pf_condition_events):
    """
    Define anchor date for recurrent condition checks.

    If the patient has a relevant PF consultation in the monthly interval,
    use the day before their first PF consultation date.

    If the patient has no relevant PF consultation in the monthly interval,
    use the day before the monthly interval start date.
    """

    first_pf_condition_date = (
        pf_condition_events
        .sort_by(pf_condition_events.date)
        .first_for_patient()
        .date
    )

    return case(
        when(first_pf_condition_date.is_not_null()).then(first_pf_condition_date - days(1)),
        otherwise=start_date - days(1),
    )

# Generic recurrent condition checker
# def check_recurrent_status(index_date,events,codelist,lookback_months,gap_weeks=4,min_episodes=2):
#     """
#     Utilised the function https://docs.opensafely.org/ehrql/reference/language/#DateEventSeries.count_episodes_for_patient
#     """
#     # condition_events = (
#     #     events
#     #     .where(events.snomedct_code.is_in(codelist))
#     #     .where(events.date.is_on_or_between(index_date - months(lookback_months),index_date,)
#     #     )
#     # )
#     condition_events = (
#         events
#         .where(events.snomedct_code.is_in(codelist))
#         .where(events.date.is_on_or_between(index_date - months(lookback_months), index_date))
#         .date
#     )

#     episode_count = (condition_events.count_episodes_for_patient(weeks(gap_weeks)))

#     return episode_count >= min_episodes
def check_recurrent_status(window_start,window_end,events,codelist,gap_weeks=4,min_episodes=2):
    """
    Utilised the function https://docs.opensafely.org/ehrql/reference/language/#DateEventSeries.count_episodes_for_patient
    """
    condition_events = (
        events
        .where(events.snomedct_code.is_in(codelist))
        .where(events.date.is_on_or_between(window_start, window_end))
        .date
    )

    episode_count = (condition_events.count_episodes_for_patient(weeks(gap_weeks)))

    return episode_count >= min_episodes

# Function to count number of coded events within a specified time window
def count_past_events(index_date, selected_events, codelist, num_months):
    return (
        selected_events.where(selected_events.snomedct_code.is_in(codelist))
        .where(
            selected_events.date.is_on_or_between(
                index_date - months(num_months), index_date
            )
        )
        .count_for_patient()
    )

# Function to count 
def has_event_count(events, codelist):
    filtered = events.where(events.snomedct_code.is_in(codelist))
    # flag = filtered.exists_for_patient()
    count_events = filtered.count_for_patient()
    count_consultations = filtered.consultation_id.count_distinct_for_patient() # https://docs.opensafely.org/ehrql/reference/language/#BoolEventSeries.count_distinct_for_patient
    # count_episode = filtered.date.count_episodes_for_patient(days(1))
    count_dates = filtered.date.count_distinct_for_patient()
    return count_events, count_consultations, count_dates

# Function to get events linked to a specified codelist
def select_events_from_codelist(event_frame, codelist):
    selected_events = event_frame.where(event_frame.snomedct_code.is_in(codelist))

    return selected_events


# Function to get events with specific consultation IDs
def select_events_by_consultation_id(event_frame, consultation_ids):
    selected_events = event_frame.where(
        event_frame.consultation_id.is_in(consultation_ids)
    )
    return selected_events


# Function to get events within a time frame
def select_events_between(event_frame, start_date, end_date):
    selected_events = event_frame.where(
        event_frame.date.is_on_or_between(start_date, end_date)
    )
    return selected_events


def select_events(
    event_frame, codelist=None, consultation_ids=None, start_date=None, end_date=None
):
    """
    Wrapper function to select events based on codelist, consultation IDs, or a date range.
    Allows combining multiple selection criteria.
    """
    selected_events = event_frame

    if codelist is not None:
        selected_events = select_events_from_codelist(selected_events, codelist)
    if consultation_ids is not None:
        selected_events = select_events_by_consultation_id(
            selected_events, consultation_ids
        )
    if start_date is not None and end_date is not None:
        selected_events = select_events_between(selected_events, start_date, end_date)

    return selected_events

def get_latest_ethnicity(index_date, clinical_events, ethnicity_codelist, ethnicity_from_sus, grouping=6):
    """
    copied from https://github.com/opensafely/pharmacy-first/blob/main/analysis/pf_dataset.py
    Date: 26 Feb 2026
    """
    latest_ethnicity_from_codes_category_num = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
        .where(clinical_events.date.is_on_or_before(index_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(ethnicity_codelist)
    )

    if grouping == 6:
        latest_ethnicity_from_codes = case(
            when(latest_ethnicity_from_codes_category_num == "1").then("White"),
            when(latest_ethnicity_from_codes_category_num == "2").then("Mixed"),
            when(latest_ethnicity_from_codes_category_num == "3").then(
                "Asian or Asian British"
            ),
            when(latest_ethnicity_from_codes_category_num == "4").then(
                "Black or Black British"
            ),
            when(latest_ethnicity_from_codes_category_num == "5").then(
                "Chinese or Other Ethnic Groups"
            ),
        )

        ethnicity_from_sus = case(
            when(ethnicity_from_sus.code.is_in(["A", "B", "C"])).then("White"),
            when(ethnicity_from_sus.code.is_in(["D", "E", "F", "G"])).then("Mixed"),
            when(ethnicity_from_sus.code.is_in(["H", "J", "K", "L"])).then(
                "Asian or Asian British"
            ),
            when(ethnicity_from_sus.code.is_in(["M", "N", "P"])).then(
                "Black or Black British"
            ),
            when(ethnicity_from_sus.code.is_in(["R", "S"])).then(
                "Chinese or Other Ethnic Groups"
            ),
        )
    elif grouping == 16:
        latest_ethnicity_from_codes = case(
            when(latest_ethnicity_from_codes_category_num == "1").then("White British"),
            when(latest_ethnicity_from_codes_category_num == "2").then("White Irish"),
            when(latest_ethnicity_from_codes_category_num == "3").then("Other White"),
            when(latest_ethnicity_from_codes_category_num == "4").then(
                "White and Caribbean"
            ),
            when(latest_ethnicity_from_codes_category_num == "5").then(
                "White and African"
            ),
            when(latest_ethnicity_from_codes_category_num == "6").then(
                "White and Asian"
            ),
            when(latest_ethnicity_from_codes_category_num == "7").then("Other Mixed"),
            when(latest_ethnicity_from_codes_category_num == "8").then("Indian"),
            when(latest_ethnicity_from_codes_category_num == "9").then("Pakistani"),
            when(latest_ethnicity_from_codes_category_num == "10").then("Bangladeshi"),
            when(latest_ethnicity_from_codes_category_num == "11").then(
                "Other South Asian"
            ),
            when(latest_ethnicity_from_codes_category_num == "12").then("Caribbean"),
            when(latest_ethnicity_from_codes_category_num == "13").then("African"),
            when(latest_ethnicity_from_codes_category_num == "14").then("Other Black"),
            when(latest_ethnicity_from_codes_category_num == "15").then("Chinese"),
            when(latest_ethnicity_from_codes_category_num == "16").then(
                "All other ethnic groups"
            ),
        )

        ethnicity_from_sus = case(
            when(ethnicity_from_sus.code == "A").then("White British"),
            when(ethnicity_from_sus.code == "B").then("White Irish"),
            when(ethnicity_from_sus.code == "C").then("Other White"),
            when(ethnicity_from_sus.code == "D").then("White and Caribbean"),
            when(ethnicity_from_sus.code == "E").then("White and African"),
            when(ethnicity_from_sus.code == "F").then("White and Asian"),
            when(ethnicity_from_sus.code == "G").then("Other Mixed"),
            when(ethnicity_from_sus.code == "H").then("Indian"),
            when(ethnicity_from_sus.code == "J").then("Pakistani"),
            when(ethnicity_from_sus.code == "K").then("Bangladeshi"),
            when(ethnicity_from_sus.code == "L").then("Other South Asian"),
            when(ethnicity_from_sus.code == "M").then("Caribbean"),
            when(ethnicity_from_sus.code == "N").then("African"),
            when(ethnicity_from_sus.code == "P").then("Other Black"),
            when(ethnicity_from_sus.code == "R").then("Chinese"),
            when(ethnicity_from_sus.code == "S").then("All other ethnic groups"),
        )

    ethnicity_combined = case(
        when(latest_ethnicity_from_codes.is_not_null()).then(
            latest_ethnicity_from_codes
        ),
        when(
            latest_ethnicity_from_codes.is_null() & ethnicity_from_sus.is_not_null()
        ).then(ethnicity_from_sus),
        otherwise="Missing",
    )

    return ethnicity_combined

def ae_non_primary_diagnosis_matches(ae_events, codelist):
    """
    Returns True if any of the non-primary diagnosis fields in the A&E events match a code from the given codelist.
    A&E diagnosis field (diagnosis_02–24) matches the given codelist.
    """
    match = (
        # ae_events.diagnosis_01.is_in(codelist) |
        ae_events.diagnosis_02.is_in(codelist) |
        ae_events.diagnosis_03.is_in(codelist) |
        ae_events.diagnosis_04.is_in(codelist) |
        ae_events.diagnosis_05.is_in(codelist) |
        ae_events.diagnosis_06.is_in(codelist) |
        ae_events.diagnosis_07.is_in(codelist) |
        ae_events.diagnosis_08.is_in(codelist) |
        ae_events.diagnosis_09.is_in(codelist) |
        ae_events.diagnosis_10.is_in(codelist) |
        ae_events.diagnosis_11.is_in(codelist) |
        ae_events.diagnosis_12.is_in(codelist) |
        ae_events.diagnosis_13.is_in(codelist) |
        ae_events.diagnosis_14.is_in(codelist) |
        ae_events.diagnosis_15.is_in(codelist) |
        ae_events.diagnosis_16.is_in(codelist) |
        ae_events.diagnosis_17.is_in(codelist) |
        ae_events.diagnosis_18.is_in(codelist) |
        ae_events.diagnosis_19.is_in(codelist) |
        ae_events.diagnosis_20.is_in(codelist) |
        ae_events.diagnosis_21.is_in(codelist) |
        ae_events.diagnosis_22.is_in(codelist) |
        ae_events.diagnosis_23.is_in(codelist) |
        ae_events.diagnosis_24.is_in(codelist)
    )
    return ae_events.where(match).exists_for_patient()

def ae_non_primary_diagnosis_match_events(ae_events, codelist):
    """
    Return A&E attendance rows where any non-primary diagnosis field
    diagnosis_02-24 matches the given codelist.
    """
    match = (
        ae_events.diagnosis_02.is_in(codelist) |
        ae_events.diagnosis_03.is_in(codelist) |
        ae_events.diagnosis_04.is_in(codelist) |
        ae_events.diagnosis_05.is_in(codelist) |
        ae_events.diagnosis_06.is_in(codelist) |
        ae_events.diagnosis_07.is_in(codelist) |
        ae_events.diagnosis_08.is_in(codelist) |
        ae_events.diagnosis_09.is_in(codelist) |
        ae_events.diagnosis_10.is_in(codelist) |
        ae_events.diagnosis_11.is_in(codelist) |
        ae_events.diagnosis_12.is_in(codelist) |
        ae_events.diagnosis_13.is_in(codelist) |
        ae_events.diagnosis_14.is_in(codelist) |
        ae_events.diagnosis_15.is_in(codelist) |
        ae_events.diagnosis_16.is_in(codelist) |
        ae_events.diagnosis_17.is_in(codelist) |
        ae_events.diagnosis_18.is_in(codelist) |
        ae_events.diagnosis_19.is_in(codelist) |
        ae_events.diagnosis_20.is_in(codelist) |
        ae_events.diagnosis_21.is_in(codelist) |
        ae_events.diagnosis_22.is_in(codelist) |
        ae_events.diagnosis_23.is_in(codelist) |
        ae_events.diagnosis_24.is_in(codelist)
    )

    return ae_events.where(match)