from ehrql import create_dataset, INTERVAL, create_measures, months
from ehrql.tables.tpp import patients, practice_registrations

dataset = create_dataset()
dataset.configure_dummy_data(population_size=500)

start_date = INTERVAL.start_date
index_date = INTERVAL.end_date

alive = patients.is_alive_on(index_date)
alive_start = patients.is_alive_on(start_date)
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()
age = patients.age_on(index_date)

dataset.define_population(patients.exists_for_patient())

dataset.start_date = start_date
dataset.index_date = index_date
dataset.alive = alive
dataset.alive_start = alive_start
dataset.registered_start = registered_start
dataset.registered_index = registered_index
dataset.age = age

measures = create_measures()
measures.configure_disclosure_control(enabled=False)

measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01"),
)

measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

measures.define_measure(
    name="measure_base_population_total",
    numerator=measure_base_population,
    denominator=patients.exists_for_patient(),
)

measures.define_measure(
    name="alive_total",
    numerator=dataset.alive,
    denominator=patients.exists_for_patient(),
)

measures.define_measure(
    name="alive_start_total",
    numerator=dataset.alive_start,
    denominator=patients.exists_for_patient(),
)

measures.define_measure(
    name="registered_start_total",
    numerator=dataset.registered_start,
    denominator=patients.exists_for_patient(),
)

measures.define_measure(
    name="registered_index_total",
    numerator=dataset.registered_index,
    denominator=patients.exists_for_patient(),
)

measures.define_measure(
    name="age_valid_total",
    numerator=dataset.age <= 120,
    denominator=patients.exists_for_patient(),
)