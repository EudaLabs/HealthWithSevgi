# Domain Clinical Review — 20 Medical Specialties

> **Project:** HealthWithSevgi — SENG 430  
> **Purpose:** Clinical justification for the top predictive feature in each domain, showing that Step 6 explanations remain aligned with established medical knowledge.

---

| # | Domain | Specialty | Target | Top Feature | Clinical Justification |
|---|--------|-----------|--------|-------------|----------------------|
| 1 | Cardiology | Heart Failure | 30-day mortality | Ejection Fraction (%) | Ejection fraction is one of the strongest prognostic markers in heart failure. Values below 35% indicate severely reduced systolic function and higher mortality risk; ESC guidance uses EF as a primary risk stratifier. |
| 2 | Cardiology — Stroke | Stroke prediction | Stroke occurrence | Average Glucose Level (mg/dL) | Hyperglycaemia contributes to vascular injury and is a recognised stroke risk factor. Persistently elevated glucose is associated with endothelial damage and worse cerebrovascular outcomes. |
| 3 | Cardiology — Arrhythmia | Arrhythmia detection | Arrhythmia presence | QRS Duration (ms) | Prolonged QRS duration reflects abnormal ventricular conduction and is commonly associated with bundle branch block patterns and ventricular rhythm abnormalities on ECG. |
| 4 | Endocrinology — Diabetes | Diabetes onset | 5-year diabetes | Fasting Glucose (mg/dL) | Fasting glucose is the core laboratory marker used to diagnose diabetes. ADA criteria define diabetes at fasting glucose ≥126 mg/dL, making it clinically expected as a top predictor. |
| 5 | Thyroid / Endocrinology | Thyroid function | Hypo / hyper / normal | TSH (mIU/L) | TSH is the most sensitive first-line screening marker for thyroid dysfunction. Elevated TSH points toward hypothyroidism, while suppressed TSH suggests hyperthyroidism. |
| 6 | Oncology — Breast | Breast biopsy | Malignant / benign | Mean Tumour Radius (mm) | Tumour size is strongly associated with malignant potential. Larger lesions are more likely to represent aggressive disease and correlate with TNM staging severity. |
| 7 | Oncology — Cervical | Cervical cancer | Biopsy result | Age | Cervical cancer risk increases with age because of cumulative HPV exposure and greater likelihood of persistent infection over time. Screening guidelines also use age-stratified recommendations. |
| 8 | Neurology — Parkinson's | Parkinson's disease | Disease presence | Vocal Jitter (%) | Jitter measures instability in vocal frequency. Parkinsonian dysarthria often produces abnormal jitter values due to impaired fine motor control of the laryngeal muscles. |
| 9 | Nephrology | Chronic kidney disease | CKD classification | Serum Creatinine (mg/dL) | Creatinine is the standard biochemical marker of renal filtration. Elevated creatinine reflects impaired kidney function and directly feeds into CKD staging through eGFR calculations. |
| 10 | Hepatology — Liver | Liver disease | Disease presence | Alkaline Phosphatase (U/L) | ALP is a key marker for cholestatic liver injury and biliary obstruction. In liver disease workups it helps distinguish cholestatic patterns from hepatocellular injury. |
| 11 | ICU / Sepsis | Sepsis onset | Sepsis label | Blood Lactate (mmol/L) | Lactate rises in tissue hypoperfusion and is one of the most clinically important markers in sepsis and septic shock assessment. It is used directly in sepsis escalation criteria. |
| 12 | Pulmonology — COPD | COPD exacerbation | Exacerbation risk | FEV1 (L) | FEV1 is the principal spirometric measure used in COPD staging. Lower FEV1 values correlate with more severe airflow limitation, higher exacerbation risk, and increased mortality. |
| 13 | Haematology — Anaemia | Anaemia detection | Anaemic / non-anaemic | Haemoglobin (g/dL) | Haemoglobin is the defining biomarker for anaemia diagnosis. WHO thresholds are based directly on Hb levels, so it is clinically appropriate as the top feature. |
| 14 | Obstetrics — Fetal Health | Fetal CTG | Normal / suspect / pathological | Abnormal Short-Term Variability (%) | Reduced short-term variability on CTG is a major warning sign of fetal compromise and possible hypoxia, making it highly relevant in fetal monitoring decisions. |
| 15 | Orthopaedics — Spine | Spinal status | Normal / abnormal | Degree of Spondylolisthesis (mm) | The measured degree of vertebral slip directly captures disease severity in spondylolisthesis and correlates with neurological symptoms, pain burden, and surgical indication. |
| 16 | Dermatology | Skin lesion | Benign / malignant | Age | Skin cancer incidence rises with age because of cumulative UV exposure and age-related biological risk. In dermatology triage, age is therefore a clinically plausible high-importance feature. |
| 17 | Ophthalmology | Diabetic retinopathy | DR present / absent | Microaneurysm Detection | Microaneurysms are the earliest classic retinal sign of diabetic retinopathy and are widely used in both manual grading and automated screening workflows. |
| 18 | Mental Health | Depression | Severity class | Sleep Quality Score | Sleep disturbance is a core clinical feature of depression and appears directly in psychiatric assessment frameworks. Poor sleep quality is strongly associated with symptom severity. |
| 19 | Pharmacy — Readmission | Hospital readmission | Readmission risk | Number of Inpatient Visits | Prior hospital use is one of the strongest predictors of future readmission because it captures disease complexity, instability, and recurrent healthcare utilisation. |
| 20 | Radiology | Pneumonia | Normal / pneumonia | Patient Age (years) | Pneumonia risk and severity rise substantially at the extremes of age, especially in elderly patients. Age therefore remains clinically meaningful even alongside imaging features. |

---

## Notes

- Top features are derived from **SHAP global importance** analysis on the trained model output.
- Clinical justifications are written to support the **Step 6 clinical sense-check banner** and to explain why the model’s leading feature is medically reasonable.
- All 20 domains use **clinical display names**, not raw dataset column names.
- This page is intended as a **GitHub Wiki reference artifact** for Sprint 4, not as a formal report PDF.
