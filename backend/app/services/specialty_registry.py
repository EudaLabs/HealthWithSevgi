"""Registry of all 20 medical specialties — aligned with Clinical Specialties Dataset Collection."""
from __future__ import annotations

from app.models.schemas import SpecialtyInfo

SPECIALTIES: dict[str, SpecialtyInfo] = {
    "cardiology_hf": SpecialtyInfo(
        id="cardiology_hf",
        name="Cardiology",
        description="Predict 30-day mortality risk in heart failure patients using clinical biomarkers.",
        target_variable="DEATH_EVENT",
        target_type="binary",
        data_source="Heart Failure Clinical Records — kaggle.com/datasets/andrewmvd/heart-failure-clinical-data",
        what_ai_predicts="30-day mortality after heart failure discharge",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "anaemia", "creatinine_phosphokinase", "diabetes",
            "ejection_fraction", "high_blood_pressure", "platelets",
            "serum_creatinine", "serum_sodium", "sex", "smoking", "time",
        ],
        clinical_context=(
            "Heart failure affects over 64 million people worldwide and carries a 30-day readmission "
            "rate of approximately 20–25%. Early identification of high-risk patients at discharge "
            "enables targeted interventions such as intensive follow-up and medication optimisation. "
            "Key clinical predictors include left ventricular ejection fraction, serum creatinine, "
            "and serum sodium levels. This model uses 12 clinical variables routinely collected "
            "at discharge to predict which patients are at highest risk of 30-day mortality."
        ),
    ),
    "radiology_pneumonia": SpecialtyInfo(
        id="radiology_pneumonia",
        name="Radiology",
        description="Classify chest X-ray findings as normal or pneumonia using clinical and imaging metadata.",
        target_variable="Finding_Label",
        target_type="binary",
        data_source="NIH Chest X-Ray Metadata — kaggle.com/datasets/nih-chest-xrays/data",
        what_ai_predicts="Normal vs. Pneumonia from chest X-ray clinical metadata",
        license_type="CC0 1.0",
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        requires_attribution=False,
        feature_names=[
            "age", "sex", "view_position", "follow_up_number",
        ],
        clinical_context=(
            "Community-acquired pneumonia is a leading cause of hospitalisation, particularly in "
            "paediatric and elderly populations. Chest radiography is the standard diagnostic tool, "
            "but interpretation requires specialist expertise not always available at point of care. "
            "The NIH Chest X-Ray dataset contains over 100,000 frontal-view X-rays labelled across "
            "14 pathology categories. This model uses extracted radiological metadata features "
            "to distinguish normal findings from pneumonia, supporting rapid triage."
        ),
    ),
    "nephrology_ckd": SpecialtyInfo(
        id="nephrology_ckd",
        name="Nephrology",
        description="Classify patients as having chronic kidney disease or not from routine laboratory values.",
        target_variable="classification",
        target_type="binary",
        data_source="UCI CKD Dataset — archive.ics.uci.edu/dataset/336/chronic+kidney+disease",
        what_ai_predicts="Chronic kidney disease (ckd vs. notckd) from routine lab values",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "blood_pressure", "specific_gravity", "albumin", "sugar",
            "red_blood_cells", "pus_cell", "blood_glucose_random", "blood_urea",
            "serum_creatinine", "sodium", "haemoglobin",
            "packed_cell_volume", "hypertension", "diabetes_mellitus",
        ],
        clinical_context=(
            "Chronic kidney disease affects approximately 10% of the global population and is "
            "a major risk factor for cardiovascular disease and end-stage renal failure. "
            "Early detection through routine blood and urine tests enables timely intervention "
            "to slow disease progression. Key biomarkers include serum creatinine, haemoglobin, "
            "and specific gravity of urine. This model classifies patients into CKD or non-CKD "
            "categories using 15 routine laboratory and clinical measurements."
        ),
    ),
    "oncology_breast": SpecialtyInfo(
        id="oncology_breast",
        name="Oncology — Breast",
        description="Classify breast biopsies as malignant or benign from cell nucleus measurements.",
        target_variable="diagnosis",
        target_type="binary",
        data_source="Breast Cancer Wisconsin — archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic",
        what_ai_predicts="Malignancy of a breast biopsy from fine-needle aspirate cell measurements",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "mean_radius", "mean_texture", "mean_perimeter", "mean_area",
            "mean_smoothness", "mean_compactness", "mean_concavity",
            "mean_concave_points", "mean_symmetry", "worst_radius",
            "worst_texture", "worst_perimeter", "worst_area", "worst_smoothness",
        ],
        clinical_context=(
            "Breast cancer is the most common cancer in women worldwide, with early detection "
            "being critical for survival outcomes. Fine needle aspiration biopsies provide "
            "cellular material that can be analysed to determine malignancy. "
            "The Wisconsin dataset contains measurements of cell nuclei features extracted "
            "from digitised images of fine needle aspirates. This model classifies tumours "
            "as malignant (M) or benign (B) based on 14 geometric and textural features "
            "of cell nuclei, achieving clinical-grade discrimination performance."
        ),
    ),
    "neurology_parkinsons": SpecialtyInfo(
        id="neurology_parkinsons",
        name="Neurology — Parkinson's",
        description="Detect Parkinson's disease from vocal biomarkers extracted via sustained phonation.",
        target_variable="status",
        target_type="binary",
        data_source="UCI Parkinson's Dataset — archive.ics.uci.edu/dataset/174/parkinsons",
        what_ai_predicts="Parkinson's disease presence from voice biomarkers",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "MDVP_Fo_Hz", "MDVP_Fhi_Hz", "MDVP_Flo_Hz",
            "MDVP_Jitter_pct", "MDVP_Jitter_Abs", "MDVP_RAP", "MDVP_PPQ", "Jitter_DDP",
            "MDVP_Shimmer", "MDVP_Shimmer_dB", "Shimmer_APQ3", "Shimmer_APQ5",
            "MDVP_APQ", "Shimmer_DDA",
            "NHR", "HNR", "RPDE", "DFA", "spread1", "spread2", "D2", "PPE",
        ],
        clinical_context=(
            "Parkinson's disease is a progressive neurodegenerative disorder affecting "
            "approximately 10 million people globally. Vocal tremor and dysphonia are "
            "among the earliest and most consistent symptoms, often preceding motor symptoms. "
            "Voice recordings can be analysed non-invasively to extract biomarkers of vocal "
            "instability including jitter, shimmer, and harmonics-to-noise ratio. "
            "This model uses 17 voice measurement features to classify patients as "
            "having Parkinson's disease (status=1) or healthy controls (status=0)."
        ),
    ),
    "endocrinology_diabetes": SpecialtyInfo(
        id="endocrinology_diabetes",
        name="Endocrinology — Diabetes",
        description="Predict diabetes onset within 5 years from metabolic and demographic markers.",
        target_variable="Outcome",
        target_type="binary",
        data_source="Pima Indians Diabetes — kaggle.com/datasets/uciml/pima-indians-diabetes-database",
        what_ai_predicts="Diabetes onset within 5 years from metabolic markers",
        license_type="CC0 1.0 / CC BY 4.0",
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        requires_attribution=True,
        feature_names=[
            "pregnancies", "glucose", "blood_pressure", "skin_thickness",
            "insulin", "bmi", "diabetes_pedigree_function", "age",
        ],
        clinical_context=(
            "Type 2 diabetes affects over 400 million people globally, with millions more "
            "at risk due to metabolic syndrome and lifestyle factors. Early identification "
            "of high-risk individuals enables preventive interventions including dietary "
            "changes, exercise, and pharmacological treatment. "
            "The Pima Indians dataset contains metabolic measurements from a population "
            "with high diabetes prevalence. This model predicts diabetes onset within "
            "5 years using 8 clinical and laboratory features including fasting glucose, "
            "BMI, and diabetes pedigree function."
        ),
    ),
    "hepatology_liver": SpecialtyInfo(
        id="hepatology_liver",
        name="Hepatology — Liver",
        description="Identify liver disease from routine blood test results.",
        target_variable="Dataset",
        target_type="binary",
        data_source="Indian Liver Patient Dataset — archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset",
        what_ai_predicts="Liver disease vs. healthy from blood test results",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "gender", "total_bilirubin", "direct_bilirubin",
            "alkaline_phosphotase", "alamine_aminotransferase",
            "aspartate_aminotransferase", "total_proteins",
            "albumin", "albumin_globulin_ratio",
        ],
        clinical_context=(
            "Liver disease encompasses a spectrum of conditions from fatty liver to cirrhosis "
            "and hepatocellular carcinoma, representing a major global health burden. "
            "Biochemical liver function tests provide quantitative markers of hepatic injury "
            "and synthetic function. Early detection through blood test abnormalities "
            "allows timely referral and treatment. "
            "This model uses 10 routine liver function test parameters to classify "
            "patients as having liver disease or not, supporting clinical triage decisions."
        ),
    ),
    "cardiology_stroke": SpecialtyInfo(
        id="cardiology_stroke",
        name="Cardiology — Stroke",
        description="Predict stroke risk from demographics, comorbidities, and lifestyle factors.",
        target_variable="stroke",
        target_type="binary",
        data_source="Stroke Prediction Dataset — kaggle.com/datasets/fedesoriano/stroke-prediction-dataset",
        what_ai_predicts="Stroke occurrence from demographics and comorbidities",
        license_type="No formal license",
        license_url="",
        requires_attribution=False,
        feature_names=[
            "gender", "age", "hypertension", "heart_disease", "ever_married",
            "work_type", "residence_type", "avg_glucose_level", "bmi", "smoking_status",
        ],
        clinical_context=(
            "Stroke is the second leading cause of death globally and the leading cause "
            "of long-term disability. Identifying high-risk individuals enables preventive "
            "interventions such as anticoagulation, blood pressure control, and lifestyle "
            "modification. Key risk factors include hypertension, atrial fibrillation, "
            "diabetes, and smoking. "
            "This model uses 10 demographic, clinical, and lifestyle variables to predict "
            "stroke occurrence, supporting population-level screening and risk stratification."
        ),
    ),
    "mental_health": SpecialtyInfo(
        id="mental_health",
        name="Mental Health",
        description="Predict history of mental illness from lifestyle, demographic, and behavioural factors.",
        target_variable="severity_class",
        target_type="binary",
        data_source="Depression Dataset — kaggle.com/datasets/anthonytherrien/depression-dataset",
        what_ai_predicts="History of mental illness (has_condition / no_condition) from lifestyle and demographic data",
        license_type="CC BY-SA 4.0",
        license_url="https://creativecommons.org/licenses/by-sa/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "number_of_children", "income", "dietary_habits", "sleep_patterns",
            "alcohol_consumption", "physical_activity_level", "smoking_status",
            "employment_status", "history_substance_abuse",
            "family_history_depression", "chronic_medical_conditions",
            "marital_status", "education_level",
        ],
        clinical_context=(
            "Depression is the leading cause of disability worldwide, affecting over 280 million "
            "people. The PHQ-9 questionnaire is a validated screening tool used in primary care "
            "to assess depression severity across four categories: minimal, mild, moderate, "
            "and severe. Accurate severity classification guides treatment decisions from "
            "watchful waiting to pharmacotherapy and referral to specialist mental health services. "
            "This model classifies depression severity using lifestyle, occupational, "
            "and demographic factors alongside validated symptom responses."
        ),
    ),
    "pulmonology_copd": SpecialtyInfo(
        id="pulmonology_copd",
        name="Pulmonology — COPD",
        description="Predict COPD exacerbation risk from spirometry and clinical EHR data.",
        target_variable="exacerbation",
        target_type="binary",
        data_source="COPD Dataset — kaggle.com/datasets/prakharrathi25/copd-student-dataset",
        what_ai_predicts="COPD acute exacerbation risk from spirometry and EHR data",
        license_type="CC0 1.0",
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        requires_attribution=False,
        feature_names=[
            "age", "sex", "smoking_pack_years", "fev1_litres", "fvc_litres",
            "fev1_fvc_ratio", "prior_exacerbations_year", "bmi",
            "mrc_dyspnea_scale", "sgrq_score", "copd_gold_stage",
        ],
        clinical_context=(
            "Chronic obstructive pulmonary disease (COPD) affects approximately 300 million "
            "people and is a leading cause of morbidity and mortality. Acute exacerbations "
            "are episodes of worsening symptoms requiring increased treatment and are a major "
            "driver of hospitalisation and disease progression. "
            "Spirometry measurements, particularly FEV1 and the FEV1/FVC ratio, are "
            "the gold standard for COPD diagnosis and staging. "
            "This model predicts the risk of acute exacerbation using clinical, "
            "spirometric, and patient-reported outcome measures from the Kaggle COPD patient dataset."
        ),
    ),
    "haematology_anaemia": SpecialtyInfo(
        id="haematology_anaemia",
        name="Haematology — Anaemia",
        description="Detect anaemia from full blood count indices including haemoglobin, MCV, MCH, and MCHC.",
        target_variable="anemia_type",
        target_type="multiclass",
        data_source="Anaemia Classification Dataset — kaggle.com/datasets/biswaranjanrao/anemia-dataset",
        what_ai_predicts="Type of anaemia from full blood count (iron deficiency / megaloblastic / normocytic / normal)",
        license_type="Unknown",
        license_url="",
        requires_attribution=False,
        feature_names=[
            "gender", "haemoglobin", "mch", "mchc", "mcv",
        ],
        clinical_context=(
            "Anaemia affects approximately 1.62 billion people globally and is defined by "
            "haemoglobin below 12 g/dL in women and 13 g/dL in men. Full blood count indices "
            "including mean corpuscular volume (MCV), mean corpuscular haemoglobin (MCH), "
            "and mean corpuscular haemoglobin concentration (MCHC) are routinely used to "
            "screen for and characterise anaemia in primary care. Low MCV indicates "
            "microcytic anaemia (typically iron deficiency), while elevated MCV suggests "
            "macrocytic anaemia (B12 or folate deficiency). "
            "This model classifies patients as anaemic or non-anaemic using five standard "
            "full blood count parameters, supporting automated screening in high-volume settings."
        ),
    ),
    "dermatology": SpecialtyInfo(
        id="dermatology",
        name="Dermatology",
        description="Classify skin lesions as benign or malignant from HAM10000 dermoscopy metadata.",
        target_variable="dx_type",
        target_type="binary",
        data_source="HAM10000 Metadata — Harvard Dataverse doi:10.7910/DVN/DBW86T",
        what_ai_predicts="Benign vs. malignant skin lesion from dermoscopy metadata",
        license_type="CC BY-NC 4.0",
        license_url="https://creativecommons.org/licenses/by-nc/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "sex", "localization",
        ],
        clinical_context=(
            "Melanoma and other skin cancers are among the most rapidly increasing malignancies "
            "globally, with early detection being the primary determinant of survival. "
            "Dermoscopy improves diagnostic accuracy compared to naked-eye examination, "
            "but requires specialist training. The HAM10000 dataset contains over 10,000 "
            "dermoscopic images with clinical metadata from seven diagnostic categories. "
            "This model uses morphological and demographic features to distinguish benign "
            "from malignant skin lesions, supporting earlier referral for biopsy."
        ),
    ),
    "ophthalmology": SpecialtyInfo(
        id="ophthalmology",
        name="Ophthalmology",
        description="Detect diabetic retinopathy from retinal image analysis features.",
        target_variable="severity_grade",
        target_type="binary",
        data_source="Diabetic Retinopathy Debrecen Dataset — archive.ics.uci.edu/dataset/329/diabetic+retinopathy+debrecen+data+set",
        what_ai_predicts="Presence of diabetic retinopathy signs from retinal analysis (0=No DR, 1=DR present)",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "quality_assessment", "pre_screening", "ma_detection_0.5",
            "ma_detection_0.6", "ma_detection_0.7", "ma_detection_0.8",
            "ma_detection_0.9", "ma_detection_1.0",
            "exudate_1", "exudate_2", "exudate_3", "exudate_4",
            "exudate_5", "exudate_6", "exudate_7", "exudate_8",
            "macula_od_distance", "optic_disc_diameter", "am_fm_classification",
        ],
        clinical_context=(
            "Diabetic retinopathy is the leading cause of blindness in working-age adults globally, "
            "affecting approximately one third of people with diabetes. Regular ophthalmological "
            "screening is recommended but limited by specialist availability. "
            "Grading retinopathy severity from mild non-proliferative to proliferative disease "
            "determines urgency of laser treatment or anti-VEGF therapy. "
            "This model classifies retinopathy severity grade using 10 clinical and "
            "retinal examination features, prioritising high-risk patients for urgent review."
        ),
    ),
    "orthopaedics": SpecialtyInfo(
        id="orthopaedics",
        name="Orthopaedics — Spine",
        description="Classify spinal status as normal or abnormal from biomechanical measurements.",
        target_variable="class",
        target_type="binary",
        data_source="Vertebral Column Dataset — archive.ics.uci.edu/dataset/212/vertebral+column",
        what_ai_predicts="Normal vs. abnormal spinal status from pelvic biomechanical measurements",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "pelvic_incidence", "pelvic_tilt", "lumbar_lordosis_angle",
            "sacral_slope", "pelvic_radius", "degree_spondylolisthesis",
        ],
        clinical_context=(
            "Spinal disorders including disc herniation and spondylolisthesis are among the "
            "most common causes of chronic pain and disability worldwide. Biomechanical "
            "measurements of the pelvis and lumbar spine provide objective indicators "
            "of structural abnormality that complement clinical examination. "
            "The UCI Vertebral Column dataset contains six orthopaedic measurements "
            "extracted from lateral X-rays. This model classifies patients as having "
            "normal spinal anatomy or an abnormal condition (disc herniation / spondylolisthesis)."
        ),
    ),
    "icu_sepsis": SpecialtyInfo(
        id="icu_sepsis",
        name="ICU / Sepsis",
        description="Predict sepsis onset from vital signs and laboratory results in ICU patients.",
        target_variable="SepsisLabel",
        target_type="binary",
        data_source="PhysioNet Sepsis Dataset — physionet.org/content/challenge-2019/1.0.0/",
        what_ai_predicts="Sepsis onset (SepsisLabel=1) from ICU vital signs and lab results",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "HR", "O2Sat", "Temp", "SBP", "MAP", "Resp",
            "BaseExcess", "pH", "PaCO2", "Lactate", "Creatinine",
            "Bilirubin_total", "WBC", "Platelets", "Age", "Gender",
        ],
        clinical_context=(
            "Sepsis is a life-threatening organ dysfunction caused by a dysregulated host "
            "response to infection, with a mortality rate of 20–30% that rises to over 40% "
            "for septic shock. Early identification and treatment within the first hour "
            "significantly improves survival outcomes. "
            "Vital signs and laboratory biomarkers such as lactate, procalcitonin, and "
            "white blood cell count reflect the physiological derangement of sepsis. "
            "This model uses routinely collected ICU monitoring data to predict sepsis "
            "onset up to 6 hours before clinical diagnosis, enabling proactive management."
        ),
    ),
    "obstetrics_fetal": SpecialtyInfo(
        id="obstetrics_fetal",
        name="Obstetrics — Fetal Health",
        description="Classify fetal cardiotocography as normal, suspect, or pathological.",
        target_variable="fetal_health",
        target_type="multiclass",
        data_source="Cardiotocography Dataset — archive.ics.uci.edu/dataset/193/cardiotocography",
        what_ai_predicts="Fetal CTG classification: 1=Normal, 2=Suspect, 3=Pathological",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "baseline_value", "accelerations", "fetal_movement",
            "uterine_contractions", "light_decelerations", "severe_decelerations",
            "prolongued_decelerations", "abnormal_short_term_variability",
            "mean_value_short_term_variability", "pct_time_abnormal_long_term_variability",
            "mean_value_long_term_variability", "histogram_mode",
        ],
        clinical_context=(
            "Cardiotocography (CTG) is the standard method for monitoring fetal wellbeing "
            "during pregnancy and labour, recording fetal heart rate and uterine contractions. "
            "Abnormal CTG patterns may indicate fetal hypoxia requiring urgent intervention "
            "such as emergency caesarean section. CTG interpretation is subjective and "
            "varies between clinicians. "
            "This model classifies CTG recordings into three categories — Normal (class 1), "
            "Suspect (class 2), and Pathological (class 3) — using 12 quantitative "
            "cardiotocography features to support consistent clinical decision-making."
        ),
    ),
    "cardiology_arrhythmia": SpecialtyInfo(
        id="cardiology_arrhythmia",
        name="Cardiology — Arrhythmia",
        description="Detect cardiac arrhythmia from ECG interval and waveform features.",
        target_variable="arrhythmia",
        target_type="binary",
        data_source="UCI Arrhythmia Dataset — archive.ics.uci.edu/dataset/5/arrhythmia",
        what_ai_predicts="Cardiac arrhythmia presence vs. normal sinus rhythm from ECG features",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "sex", "height", "weight", "QRS_duration",
            "PR_interval", "QT_interval", "T_interval", "P_interval",
            "QRS_axis", "T_axis", "P_axis", "heart_rate", "J_point",
            "heart_rate_2",
            "DI_R", "DI_S", "DI_T", "DI_P", "DI_QRSA", "DI_QRSTA",
            "DII_R", "DII_S", "DII_T", "DII_P", "DII_QRSA", "DII_QRSTA",
            "V1_R", "V1_S", "V1_T", "V1_P", "V5_R", "V5_S",
        ],
        clinical_context=(
            "Cardiac arrhythmias encompass a diverse group of rhythm disorders ranging from "
            "benign atrial ectopics to life-threatening ventricular fibrillation. "
            "The 12-lead ECG is the primary diagnostic tool, providing measurements of "
            "conduction intervals and waveform morphology. Automated arrhythmia detection "
            "supports cardiac monitoring programs and remote cardiology services. "
            "This model uses 13 ECG-derived parameters to classify patients as having "
            "arrhythmia or normal cardiac rhythm, supporting cardiac screening programs."
        ),
    ),
    "oncology_cervical": SpecialtyInfo(
        id="oncology_cervical",
        name="Oncology — Cervical",
        description="Assess cervical cancer biopsy risk from demographic and behavioural risk factors.",
        target_variable="Biopsy",
        target_type="binary",
        data_source="Cervical Cancer Dataset — archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors",
        what_ai_predicts="Biopsy-confirmed cervical cancer from demographic and behavioural data",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "number_of_sexual_partners", "first_sexual_intercourse_age",
            "num_of_pregnancies",
            "smokes", "smokes_years",
            "hormonal_contraceptives", "hormonal_contraceptives_years",
            "iud", "iud_years",
            "stds", "stds_number", "stds_condylomatosis",
            "stds_cervical_condylomatosis", "stds_hpv",
            "dx_cancer", "dx_cin", "dx_hpv", "dx",
            "hinselmann", "schiller", "citology",
        ],
        clinical_context=(
            "Cervical cancer is the fourth most common cancer in women globally, with "
            "persistent HPV infection being the primary causative factor. Risk stratification "
            "using demographic and behavioural data can identify women who require "
            "expedited colposcopy or biopsy. Early detection through cytological and "
            "histological examination enables curative treatment. "
            "This model uses 11 demographic, sexual health, and medical history variables "
            "to predict biopsy-confirmed cervical cancer, supporting targeted screening "
            "in resource-limited settings."
        ),
    ),
    "thyroid": SpecialtyInfo(
        id="thyroid",
        name="Thyroid / Endocrinology",
        description="Classify thyroid function as hypothyroid, hyperthyroid, or normal from biochemical assay results.",
        target_variable="class",
        target_type="multiclass",
        data_source="UCI New Thyroid Dataset — archive.ics.uci.edu/dataset/102/thyroid+disease",
        what_ai_predicts="Thyroid function classification (hyperthyroid / normal / hypothyroid)",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "T3_resin_uptake", "total_serum_thyroxine", "T3", "TSH", "max_abs_diff_TSH",
        ],
        clinical_context=(
            "Thyroid dysfunction affects approximately 5% of the global population. "
            "Hyperthyroidism (excess hormone) and hypothyroidism (deficiency) are diagnosed "
            "primarily through laboratory thyroid function tests. "
            "The T3 resin uptake reflects thyroid hormone binding capacity, "
            "total serum thyroxine (T4) measures overall hormone production, "
            "and TSH (thyroid-stimulating hormone) is the most sensitive marker of thyroid status. "
            "This model uses 5 biochemical assay values from the UCI New Thyroid dataset "
            "to classify patients into three categories — hyperthyroid, normal, or hypothyroid — "
            "supporting primary care screening and endocrinology referral decisions."
        ),
    ),
    "pharmacy_readmission": SpecialtyInfo(
        id="pharmacy_readmission",
        name="Pharmacy — Readmission",
        description="Predict hospital readmission risk for diabetic inpatients using medication and clinical data.",
        target_variable="readmitted",
        target_type="multiclass",
        data_source="Diabetes 130-US Hospitals Dataset — archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008",
        what_ai_predicts="Readmission risk: <30 days / >30 days / NO from medication and utilisation data",
        license_type="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        requires_attribution=True,
        feature_names=[
            "age", "gender", "time_in_hospital", "num_lab_procedures",
            "num_procedures", "num_medications", "number_outpatient",
            "number_emergency", "number_inpatient", "number_diagnoses",
            "max_glu_serum", "A1Cresult", "metformin", "insulin", "change",
            "discharge_disposition_id", "admission_type_id",
            "admission_source_id", "diag_1",
        ],
        clinical_context=(
            "Hospital readmission within 30 days is a key quality indicator and financial "
            "penalty trigger under value-based care programmes. Diabetic patients have "
            "disproportionately high readmission rates due to complex medication regimens, "
            "comorbidities, and glycaemic instability. "
            "The UCI 130-US Hospitals dataset contains over 100,000 diabetic patient "
            "encounters from 130 US hospitals over 10 years. "
            "This model classifies patients into three readmission risk groups — "
            "within 30 days, after 30 days, or no readmission — using 15 clinical, "
            "medication, and utilisation variables to guide discharge planning."
        ),
    ),
}


def get_specialty(specialty_id: str) -> SpecialtyInfo | None:
    return SPECIALTIES.get(specialty_id)


def list_specialties() -> list[SpecialtyInfo]:
    return list(SPECIALTIES.values())
