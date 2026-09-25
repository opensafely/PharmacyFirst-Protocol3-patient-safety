from ehrql import codelist_from_csv

 ####################################################
# SNOMED UK ethnicity category codelist - latest version 22911876
ethnicity_group6_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)
ethnicity_group16_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_16",
)

# consultation type -- pending update
gp_codelist_consultation_f2f = codelist_from_csv(
    "codelists/pharmacy-first-project-face-to-face-consultation-codes-for-pharmacy-first.csv",
    column="code"
)
gp_codelist_consultation_online = codelist_from_csv(
    "codelists/pharmacy-first-project-online-consultation-codes-for-pharmacy-first.csv",
    column="code"
)
gp_codelist_consultation_telephone = codelist_from_csv(
    "codelists/pharmacy-first-project-telephone-consultation-codes-for-pharmacy-first.csv",
    column="code"
)

gp_codelist_consultation_econsultation = ["1068881000000101"]

#PF conditions snomed codes used within PF
tx_codelist_pf_otitis_media = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-acute-otitis-media-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_impetigo = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-impetigo-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_infected_insect_bites = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-infected-insect-bites-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_shingles = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-shingles-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_sinusitis = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sinusitis-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_sore_throat = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sore-throat-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_urinary_tract_infection = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-urinary-tract-infection-treatment-full-dmd-codelist.csv",
    column="code",
)

####################################################
#Snomed codes used for PF conditions by GPs
# Updated from Protocol 2 to Protocol 3
gp_snomed_codelist_uti = codelist_from_csv(
    # "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions.csv",
    # "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions-for-pharamcy-first-clone.csv",
    "codelists/pharmacy-first-project-urinary-tract-infection-codes-for-pharmacy-first-clone.csv",
    column="code",
)  
gp_snomed_codelist_impetigo = codelist_from_csv(
    # "codelists/pharmacy-first-project-impetigo-related-conditions-administration-codes-for-pharmacy-first.csv",
    "codelists/pharmacy-first-project-impetigo-codes-for-pharmacy-first-clone.csv",
    column="code",
) 
gp_snomed_codelist_otitis_media = codelist_from_csv(
    # "codelists/pharmacy-first-project-otitis-media-and-related-conditions.csv",
    "codelists/pharmacy-first-project-otitis-media-codes-for-pharmacy-first-clone.csv",
    column="code",
) 
gp_snomed_codelist_sinusitis = codelist_from_csv(
    # "codelists/pharmacy-first-project-sinusitis-related-conditions-administration-codes-for-pharmacy-first.csv",
    "codelists/pharmacy-first-project-sinusitis-codes-for-pharmacy-first-clone.csv",
    column="code",
) 
gp_snomed_codelist_sore_throat = codelist_from_csv(
    # "codelists/pharmacy-first-project-Sore-throat-and-related-conditions.csv",
    "codelists/pharmacy-first-project-sore-throat-codes-for-pharmacy-first-clone.csv",
    column="code",
) 
gp_snomed_codelist_insect_bites = codelist_from_csv(
    # "codelists/pharmacy-first-project-insect-bites-and-related-conditions-administration-codes-for-pharmacy-first.csv",
    "codelists/pharmacy-first-project-infected-insect-bites-codes-for-pharmacy-first-strict-definition.csv",
    column="code",
) 
gp_snomed_codelist_shingles = codelist_from_csv(
    # "codelists/pharmacy-first-project-shingles-and-related-conditions-for-pharmacy-first.csv",
    "codelists/pharmacy-first-project-shingles-for-pharmacy-first-clone.csv",
    column="code",
)
####################################################
#Snomed codes used for deciding which one to use for insect bites - Protocol 2

# gp_snomed_codelist_insect_bites_strict = codelist_from_csv(
#     "codelists/pharmacy-first-project-infected-insect-bites-codes-for-pharmacy-first-strict-definition.csv",
#     column="code",
# ) 

# gp_snomed_codelist_insect_bites_all = codelist_from_csv(
#     "codelists/pharmacy-first-project-all-insect-bites-codes-for-pharmacy-first.csv",
#     column="code",
# ) 

gp_snomed_codelist_cellulitis_only = codelist_from_csv(
    "codelists/pharmacy-first-project-cellulitis-using-snomed-ct-codes.csv",
    column="code",
) 

####################################################
#Snomed codes used for control conditions by GPs
gp_snomed_codelist_lower_back_pain = codelist_from_csv(
    "codelists/pharmacy-first-project-lower-back-pain-for-pf-control.csv",
    column="code",
)


####################################################
#Snomed codes used for specific conditions by GPs - population exclusion criteria
gp_snomed_codelist_urinary_catheter = codelist_from_csv(
    "codelists/pharmacy-first-project-urinary-catheter-administration-codes-for-pharmacy-first.csv",
    column="code",
)

#Snomed codes used for specific conditions by GPs - population exclusion criteria
gp_snomed_codelist_bullous_impetigo = codelist_from_csv(
    "codelists/pharmacy-first-project-bullous-impetigo-administration-codes-for-pharmacy-first.csv",
    column="code",
)

#Snomed codes used for specific conditions by GPs - population exclusion criteria
#current version: pregnancy code by NHSD
gp_snomed_codelist_pregnancy = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv",
    column="code",
    category_column="term",
)

# Import no-longer-pregnant codelist
gp_snomed_codelist_end_pregnancy = codelist_from_csv(
    "codelists/pharmacy-first-project-end-of-pregnancy-narrow.csv",
    column="code",
    category_column="term",
)

gp_snomed_codelist_miscarriage = codelist_from_csv(
    "codelists/user-paolomazzone-openpregnosis-miscarriage-codes_v1.csv",
    column="code",
)

gp_snomed_codelist_molar_pregnancy = codelist_from_csv(
    "codelists/user-paolomazzone-openpregnosis-molar-codes_v1.csv",
    column="code",
)

gp_snomed_codelist_blighted_ovum_pregnancy = codelist_from_csv(
    "codelists/user-paolomazzone-openpregnosis-blighted-ovum-codes_v1.csv",
    column="code",
)

gp_snomed_codelist_ectopic_pregnancy = codelist_from_csv(
    "codelists/user-paolomazzone-openpregnosis-ectopic-codes_v1.csv",
    column="code",
)

gp_snomed_codelist_early_loss_pregnancy = (
    gp_snomed_codelist_miscarriage
    + gp_snomed_codelist_molar_pregnancy
    + gp_snomed_codelist_blighted_ovum_pregnancy
    + gp_snomed_codelist_ectopic_pregnancy
)


# estimated date of delivery
gp_snomed_codelist_pregnancy_edd = codelist_from_csv (
    "codelists/user-VickiPalin-pregnancy_edd_snomed.csv"
    , column = "code"
)
####################################################
"""
pf_med_codelist = (
    acute_otitis_media_tx_codelist
    + impetigo_treatment_tx_codelist
    + infected_insect_bites_tx_codelist
    + shingles_treatment_tx_codelist
    + sinusitis_tx_codelist
    + sore_throat_tx_codelist
    + urinary_tract_infection_tx_codelist
)
"""

# Community Pharmacist Consultation Service for minor illness
pf_consultation_cp_minorillness = ["1577041000000109"]
# Pharmacy First service
pf_consultation_service = ["983341000000102"]
# Community Pharmacy First Service
pf_consultation_cp_service = ["2129921000000100"]
 
pf_consultation_events_dict = {
    "pf_consultation_cp_minorillness": pf_consultation_cp_minorillness, # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "pf_consultation_service": pf_consultation_service, # Pharmacy First service (qualifier value)
    "pf_consultation_cp_service": pf_consultation_cp_service, # Community Pharmacy Pharmacy First Service
    "pf_consultation_services_combined": pf_consultation_cp_minorillness + pf_consultation_service + pf_consultation_cp_service,
    # "pf_consultation_services_combined": pf_consultation_service + pf_consultation_cp_service,
}
 
uti_code = ["1090711000000102"]
sinusitis_code = ["15805002"]
insectbite_code = ["262550002"]
otitismedia_code = ["3110003"]
sorethroat_code = ["363746003"]
shingles_code = ["4740000"]
impetigo_code = ["48277006"]

####################################################
#Snomed codes used for safety evaluation - GP clinical events

gp_snomed_codelist_pyelonephritis = codelist_from_csv(
    "codelists/pharmacy-first-project-pyelonephritis-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_sepsis = codelist_from_csv(
    "codelists/pharmacy-first-project-sepsis-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_quinsy = codelist_from_csv(
    "codelists/pharmacy-first-project-quinsy-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_post_herpetic_neuralgia = codelist_from_csv(
    "codelists/pharmacy-first-project-post-herpetic-neuralgia-using-snomed-ct.csv",
    column="code"
)

gp_snomed_codelist_mastoiditis = codelist_from_csv(
    "codelists/pharmacy-first-project-mastoiditis-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_meningitis = codelist_from_csv(
    "codelists/pharmacy-first-project-meningitis-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_intracranial_abscess = codelist_from_csv(
    "codelists/pharmacy-first-project-intracranial-abscess-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_sinus_thrombosis = codelist_from_csv(
    "codelists/pharmacy-first-project-sinus-thrombosis-using-snomed-ct-codes.csv",
    column="code"
)

gp_snomed_codelist_facial_nerve_paralysis = codelist_from_csv(
    "codelists/pharmacy-first-project-facial-nerve-paralysis-using-snomed-ct-codes.csv",
    column="code"
)

####################################################
#ICD10 codes used for safety evaluation - hospital events

icd10_codelist_pyelonephritis = codelist_from_csv(
    "codelists/pharmacy-first-project-pyelonephritis-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_sepsis = codelist_from_csv(
    "codelists/pharmacy-first-project-sepsis-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_cellulitis = codelist_from_csv(
    "codelists/pharmacy-first-project-cellulitis-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_quinsy = codelist_from_csv(
    "codelists/pharmacy-first-project-quinsy-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_post_herpetic_neuralgia = codelist_from_csv(
    "codelists/pharmacy-first-project-post-herpetic-neuralgia-using-icd10.csv",
    column="code"
)

icd10_codelist_mastoiditis = codelist_from_csv(
    "codelists/pharmacy-first-project-mastoiditis-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_meningitis = codelist_from_csv(
    "codelists/pharmacy-first-project-meningitis-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_intracranial_abscess = codelist_from_csv(
    "codelists/pharmacy-first-project-intracranial-abscess-using-icd10-codes.csv",
    column="code"
)

icd10_codelist_sinus_thrombosis = codelist_from_csv(
    "codelists/pharmacy-first-project-sinus-thrombosis-usign-icd10-codes.csv",
    column="code"
)

icd10_codelist_facial_nerve_paralysis = codelist_from_csv(
    "codelists/pharmacy-first-project-facial-nerve-paralysis-using-icd10-codes.csv",
    column="code"
)
