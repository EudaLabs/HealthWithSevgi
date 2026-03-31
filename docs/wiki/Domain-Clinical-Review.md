# Domain Clinical Review — 20 Medical Specialties

> **Project:** HealthWithSevgi — SENG 430
> **Purpose:** Clinical justification for the top predictive feature in each domain, demonstrating that model outputs align with established medical knowledge.

---

| # | Domain | Specialty | Target | Top Feature | Clinical Justification |
|---|--------|-----------|--------|-------------|----------------------|
| 1 | Cardiology | Heart Failure | 30-day mortality | Ejection Fraction (%) | EF is a well-established predictor of HF outcomes — values below 35% indicate severely reduced cardiac function and higher mortality risk. ESC guidelines use EF as a primary stratification variable. |
| 2 | Cardiology — Stroke | Stroke prediction | Stroke occurrence | Average Glucose Level (mg/dL) | Hyperglycaemia is an independent risk factor for stroke. Elevated glucose levels indicate insulin resistance and vascular damage that increase cerebrovascular event risk. |
| 3 | Cardiology — Arrhythmia | Arrhythmia detection | Arrhythmia presence | QRS Duration (ms) | Prolonged QRS duration reflects abnormal ventricular conduction and is a hallmark of bundle branch blocks and ventricular arrhythmias on 12-lead ECG. |
| 4 | Endocrinology — Diabetes | Diabetes onset | 5-year diabetes | Fasting Glucose (mg/dL) | Fasting glucose is the primary biochemical marker of diabetes. ADA diagnostic criteria define diabetes as fasting glucose ≥126 mg/dL. |
| 5 | Thyroid / Endocrinology | Thyroid function | Hypo/hyper/normal | TSH (mIU/L) | TSH is the most sensitive marker of thyroid dysfunction — elevated TSH indicates hypothyroidism, suppressed TSH indicates hyperthyroidism. First-line screening test per ATA guidelines. |
| 6 | Oncology — Breast | Breast biopsy | Malignant/benign | Mean Tumour Radius (mm) | Tumour size is closely correlated with malignancy. Larger tumours indicate more aggressive histology and higher risk of metastatic disease per TNM staging. |
| 7 | Oncology — Cervical | Cervical cancer | Biopsy result | Age | Cervical cancer risk increases with age due to cumulative HPV exposure and persistent infection. Screening guidelines recommend age-stratified protocols. |
| 8 | Neurology — Parkinson's | Parkinson's disease | Disease presence | Vocal Jitter (%) | Jitter measures cycle-to-cycle variation in vocal frequency. Pathological jitter values indicate laryngeal motor instability characteristic of Parkinson's-related dysarthria. |
| 9 | Nephrology | Chronic kidney disease | CKD classification | Serum Creatinine (mg/dL) | Creatinine is the standard biomarker for renal function. Elevated levels reflect impaired glomerular filtration — the basis of the eGFR equation used in CKD staging. |
| 10 | Hepatology — Liver | Liver disease | Disease presence | Alkaline Phosphatase (U/L) | ALP elevation indicates cholestatic liver disease or biliary obstruction. Combined with other LFTs, it differentiates hepatocellular from cholestatic injury patterns. |
| 11 | ICU / Sepsis | Sepsis onset | Sepsis label | Blood Lactate (mmol/L) | Elevated lactate is a hallmark of cellular hypoperfusion and a key diagnostic criterion for septic shock. Surviving Sepsis Campaign uses lactate >2 mmol/L as an activation trigger. |
| 12 | Pulmonology — COPD | COPD exacerbation | Exacerbation risk | FEV1 (L) | FEV1 is the gold standard for COPD severity staging (GOLD criteria). Lower FEV1 directly correlates with exacerbation frequency and mortality. |
| 13 | Haematology — Anaemia | Anaemia detection | Anaemic/non-anaemic | Haemoglobin (g/dL) | Haemoglobin is the defining biomarker for anaemia diagnosis. WHO defines anaemia as Hb <12 g/dL (women) or <13 g/dL (men). |
| 14 | Obstetrics — Fetal Health | Fetal CTG | Normal/suspect/pathological | Abnormal Short-Term Variability (%) | Reduced short-term variability on CTG is a key indicator of fetal compromise and possible hypoxia, prompting urgent clinical intervention per FIGO guidelines. |
| 15 | Orthopaedics — Spine | Spinal status | Normal/abnormal | Degree of Spondylolisthesis (mm) | Directly quantifies vertebral slip — the primary determinant of clinical severity in spinal disorders. Higher degrees correlate with neurological symptoms and surgical indication. |
| 16 | Dermatology | Skin lesion | Benign/malignant | Age | Melanoma incidence increases significantly with age due to cumulative UV exposure and immunosenescence. Screening guidelines prioritise older patients. |
| 17 | Ophthalmology | Diabetic retinopathy | DR present/absent | Microaneurysm Detection | Microaneurysms are the earliest clinical sign of diabetic retinopathy and the basis of automated DR screening algorithms. Their count and distribution predict disease progression. |
| 18 | Mental Health | Depression | Severity class | Sleep Quality Score | Sleep disturbance is both a risk factor and a core diagnostic criterion for depression (DSM-5). Insomnia and hypersomnia patterns correlate with depression severity. |
| 19 | Pharmacy — Readmission | Hospital readmission | Readmission risk | Number of Inpatient Visits | Prior hospitalisation frequency is the strongest predictor of future readmission. It reflects disease complexity, comorbidity burden, and healthcare utilisation patterns. |
| 20 | Radiology | Pneumonia | Normal/pneumonia | Patient Age (years) | Pneumonia incidence and mortality follow a U-shaped age distribution, disproportionately affecting young children and elderly adults due to immune system maturity and decline. |

---

## Notes

- Top features are determined by SHAP global importance analysis across the test set
- Clinical justifications are based on established medical literature and clinical practice guidelines
- The clinical sense-check banner in Step 6 dynamically displays domain-specific explanations for the top feature when switching between specialties
- All 20 domains use clinical display names (not raw column names) throughout the interface
