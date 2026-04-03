# Dataset Licensing and Compliance

> **Project:** ML Visualization Tool for Healthcare Professionals
> **Course:** SENG 430 Software Quality Assurance -- Cankaya University, Spring 2025-2026
> **Last updated:** 2026-04-03
> **Maintainer:** Project Team (Efe Celik, Berat Mert, Batuhan Bayazit, Burak Aydogmus, Berfin Duru Alkan)

This document provides a complete inventory of the datasets used in the ML Visualization
Tool, their licenses, redistribution rights, and required attributions. It is intended to
satisfy ISO/IEC 25012 data quality documentation requirements and EU AI Act Articles 10
and 11 (data governance and technical documentation).

**This project is strictly academic and non-commercial.** All datasets are used solely for
educational demonstration within a university course. No dataset is used for clinical
decision-making, commercial products, or patient-facing systems.

---

## 1. Summary Table

| # | Specialty | Dataset | License | Bundled in Docker | Attribution Required |
|---|-----------|---------|---------|:-----------------:|:--------------------:|
| 1 | Cardiology (HF) | Heart Failure Clinical Records | CC BY 4.0 | YES | YES |
| 2 | Radiology | NIH Chest X-Ray Metadata | CC0 1.0 | YES | Courtesy |
| 3 | Nephrology | Chronic Kidney Disease | CC BY 4.0 | YES | YES |
| 4 | Oncology (Breast) | Breast Cancer Wisconsin | CC BY 4.0 | YES | YES |
| 5 | Neurology | Parkinson's Disease | CC BY 4.0 | YES | YES |
| 6 | Endocrinology | Pima Indians Diabetes | CC0 / CC BY 4.0 | YES | YES |
| 7 | Hepatology | Indian Liver Patient | CC BY 4.0 | YES | YES |
| 8 | Cardiology (Stroke) | Stroke Prediction | No formal license | NO | Educational only |
| 9 | Mental Health | Depression Dataset | CC BY-SA 4.0 | YES | YES |
| 10 | Pulmonology | COPD Dataset | CC0 1.0 | YES | Courtesy |
| 11 | Haematology | Anaemia Classification | Unknown | NO | Unknown |
| 12 | Dermatology | HAM10000 Metadata | CC BY-NC 4.0 | YES | YES |
| 13 | Ophthalmology | DR Debrecen | CC BY 4.0 | YES | YES |
| 14 | Orthopaedics | Vertebral Column | CC BY 4.0 | YES | YES |
| 15 | ICU / Sepsis | PhysioNet Sepsis 2019 | CC BY 4.0 | YES | YES |
| 16 | Obstetrics | Cardiotocography | CC BY 4.0 | YES | YES |
| 17 | Cardiology (Arrhythmia) | Arrhythmia | CC BY 4.0 | YES | YES |
| 18 | Oncology (Cervical) | Cervical Cancer Risk | CC BY 4.0 | YES | YES |
| 19 | Thyroid | New Thyroid | CC BY 4.0 | YES | YES |
| 20 | Pharmacy | Diabetes 130-US Hospitals | CC BY 4.0 | YES | YES |

**18 of 20 datasets are bundled** in the Docker image. The remaining 2 are downloaded
automatically at runtime because their licenses could not be verified for redistribution.

---

## 2. License Categories

### CC BY 4.0 -- Creative Commons Attribution 4.0 International (13 datasets)

**Datasets:** Heart Failure Clinical Records, Chronic Kidney Disease, Breast Cancer
Wisconsin, Parkinson's Disease, Indian Liver Patient, DR Debrecen, Vertebral Column,
PhysioNet Sepsis 2019, Cardiotocography, Arrhythmia, Cervical Cancer Risk, New Thyroid,
Diabetes 130-US Hospitals.

**Rights granted:** Copy, redistribute, remix, transform, and build upon the material for
any purpose, including commercially, provided that appropriate credit is given, a link to
the license is provided, and any changes are indicated.

**Our obligations:** Attribution in ATTRIBUTION.md and this document. Modifications noted
per dataset below.

**License text:** <https://creativecommons.org/licenses/by/4.0/legalcode>

### CC0 1.0 -- Creative Commons Public Domain Dedication (3 datasets)

**Datasets:** NIH Chest X-Ray Metadata, COPD Dataset, Pima Indians Diabetes (Kaggle
version).

**Rights granted:** The creator has waived all copyright and related rights. No conditions
apply. The work is in the public domain.

**Our obligations:** None legally required. We provide courtesy attribution as good
academic practice.

**License text:** <https://creativecommons.org/publicdomain/zero/1.0/legalcode>

### CC BY-SA 4.0 -- Creative Commons Attribution-ShareAlike 4.0 International (1 dataset)

**Dataset:** Depression Dataset.

**Rights granted:** Same as CC BY 4.0, with the additional requirement that any adapted
material must be distributed under the same or a compatible license.

**Our obligations:** Attribution required. Any modifications we distribute must remain
under CC BY-SA 4.0 or a compatible license. Our processed CSV derivative is distributed
under CC BY-SA 4.0.

**License text:** <https://creativecommons.org/licenses/by-sa/4.0/legalcode>

### CC BY-NC 4.0 -- Creative Commons Attribution-NonCommercial 4.0 International (1 dataset)

**Dataset:** HAM10000 Metadata.

**Rights granted:** Copy, redistribute, remix, and transform for non-commercial purposes
only, with attribution.

**Our obligations:** Attribution required. This project is strictly academic and
non-commercial, which satisfies the NC restriction. If the project is ever used
commercially, this dataset must be removed.

**License text:** <https://creativecommons.org/licenses/by-nc/4.0/legalcode>

### No Formal License (1 dataset)

**Dataset:** Stroke Prediction (Kaggle).

**Status:** Published on Kaggle by user "fedesoriano" without a machine-readable license.
Kaggle's Terms of Service allow downloading for personal and educational use, but do not
grant redistribution rights.

**Our approach:** NOT bundled in the Docker image. Downloaded automatically at runtime from
Kaggle when the user selects the Stroke specialty. Users must have network access.

### Unknown License (1 dataset)

**Dataset:** Anaemia Classification (Kaggle).

**Status:** Published on Kaggle by user "Biswa Ranjan Rao" without a stated license. No
license metadata found on the dataset page.

**Our approach:** NOT bundled in the Docker image. Downloaded automatically at runtime.
Same approach as the Stroke Prediction dataset.

---

## 3. Per-Dataset Details

### 3.1 Heart Failure Clinical Records

- **Specialty:** Cardiology (Heart Failure)
- **Authors:** Chicco, D. and Jurman, G.
- **Citation:** Chicco, D. and Jurman, G. (2020). "Machine learning can predict survival of patients with heart failure from serum creatinine and ejection fraction alone." *BMC Medical Informatics and Decision Making*, 20, 16.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5Z89R](https://doi.org/10.24432/C5Z89R)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records)
- **Records:** 299 patients
- **Modifications:** Column names standardised to snake_case. No rows removed.

### 3.2 NIH Chest X-Ray Metadata

- **Specialty:** Radiology
- **Authors:** Wang, X., Peng, Y., Lu, L., Lu, Z., Bagheri, M., and Summers, R.M.
- **Citation:** Wang, X. et al. (2017). "ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks." *CVPR 2017*.
- **License:** CC0 1.0 (Public Domain)
- **DOI:** None
- **Source:** [NIH Clinical Center](https://nihcc.app.box.com/v/ChestXray-NIHCC)
- **Records:** Metadata only (no images). Downsampled from approximately 112,000 to 5,000 records for educational use.
- **Modifications:** Downsampled to 5,000 records. Finding labels binarised to Normal vs. Abnormal. Image pixel data not included; only tabular metadata is used.

### 3.3 Chronic Kidney Disease

- **Specialty:** Nephrology
- **Authors:** Rubini, L., Soundarapandian, P., and Eswaran, P.
- **Citation:** Rubini, L., Soundarapandian, P., and Eswaran, P. (2015). "Chronic Kidney Disease." UCI Machine Learning Repository.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5G020](https://doi.org/10.24432/C5G020)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease)
- **Records:** 400 patients
- **Modifications:** Column names expanded from abbreviations to full clinical names. Missing value encoding standardised.

### 3.4 Breast Cancer Wisconsin (Diagnostic)

- **Specialty:** Oncology (Breast)
- **Authors:** Wolberg, W.H., Mangasarian, O.L., and Street, W.N.
- **Citation:** Wolberg, W.H., Mangasarian, O.L., and Street, W.N. (1993). "Breast Cancer Wisconsin (Diagnostic)." UCI Machine Learning Repository.
- **License:** CC BY 4.0 (UCI) / BSD (scikit-learn bundled copy)
- **DOI:** [10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic)
- **Records:** 569 patients
- **Modifications:** ID column removed. Diagnosis column mapped from M/B to 1/0.

### 3.5 Parkinson's Disease

- **Specialty:** Neurology
- **Authors:** Little, M.
- **Citation:** Little, M. (2007). "Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection." *IEEE Transactions on Biomedical Engineering*.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C59C74](https://doi.org/10.24432/C59C74)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/174/parkinsons)
- **Records:** 195 observations (31 subjects)
- **Modifications:** Patient name column removed. Column order rearranged for consistency.

### 3.6 Pima Indians Diabetes

- **Specialty:** Endocrinology
- **Authors:** Smith, J.W., Everhart, J.E., Dickson, W.C., Knowler, W.C., and Johannes, R.S.
- **Citation:** Smith, J.W. et al. (1988). "Using the ADAP Learning Algorithm to Forecast the Onset of Diabetes Mellitus." *Proceedings of the Annual Symposium on Computer Application in Medical Care*, 261-265. Original data from the National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK).
- **License:** CC0 1.0 (Kaggle version) / CC BY 4.0 (UCI version). We use the Kaggle CC0 version but provide full attribution as good practice.
- **DOI:** None
- **Source:** [Kaggle](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
- **Records:** 768 patients
- **Modifications:** Zero values in glucose, blood pressure, skin thickness, insulin, and BMI columns treated as missing (replaced with NaN) as documented in the original study notes.

### 3.7 Indian Liver Patient

- **Specialty:** Hepatology
- **Authors:** Ramana, B.V. and Venkateswarlu, N.B.
- **Citation:** Ramana, B.V. and Venkateswarlu, N.B. (2012). "Indian Liver Patient Dataset." UCI Machine Learning Repository.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5D02C](https://doi.org/10.24432/C5D02C)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset)
- **Records:** 583 patients
- **Modifications:** Target column renamed from "Dataset" to "liver_disease" for clarity. Gender column label-encoded.

### 3.8 Stroke Prediction

- **Specialty:** Cardiology (Stroke)
- **Authors:** fedesoriano (pseudonym)
- **Citation:** fedesoriano (2021). "Stroke Prediction Dataset." Kaggle.
- **License:** No formal license specified on Kaggle.
- **DOI:** None
- **Source:** [Kaggle](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)
- **Records:** Approximately 5,110 patients
- **Modifications:** N/A -- dataset is not bundled. Downloaded at runtime without modification.
- **Bundling status:** NOT BUNDLED. Auto-downloaded at runtime. Educational use only under Kaggle Terms of Service.

### 3.9 Depression Dataset

- **Specialty:** Mental Health
- **Authors:** Anthony Therrien
- **Citation:** Therrien, A. "Depression and Anxiety Data." Kaggle.
- **License:** CC BY-SA 4.0
- **DOI:** None
- **Source:** [Kaggle](https://www.kaggle.com/datasets/anthonytherrien/depression-dataset)
- **Records:** Variable (survey-based)
- **Modifications:** Severity classes consolidated from fine-grained scale to 3-level classification. Column names standardised. Distributed under CC BY-SA 4.0 per ShareAlike obligation.

### 3.10 COPD Dataset

- **Specialty:** Pulmonology
- **Authors:** Prakhar Rathi (compiled from UCL Datasets Library)
- **Citation:** Rathi, P. "COPD Dataset." Kaggle / UCL Datasets Library.
- **License:** CC0 1.0 (Public Domain)
- **DOI:** None
- **Source:** [Kaggle](https://www.kaggle.com/datasets/prakharrathi25/copd-student-dataset)
- **Records:** 101 patients
- **Modifications:** Column names standardised. Exacerbation target binarised.

### 3.11 Anaemia Classification

- **Specialty:** Haematology
- **Authors:** Biswa Ranjan Rao
- **Citation:** Rao, B.R. "Anaemia Types Classification." Kaggle.
- **License:** Unknown (no license specified on Kaggle)
- **DOI:** None
- **Source:** [Kaggle](https://www.kaggle.com/datasets/biswaranjanrao/anemia-dataset)
- **Records:** ~400 patients
- **Modifications:** N/A -- dataset is not bundled. Downloaded at runtime without modification.
- **Bundling status:** NOT BUNDLED. Auto-downloaded at runtime. License status could not be verified.

### 3.12 HAM10000 Metadata

- **Specialty:** Dermatology
- **Authors:** Tschandl, P., Rosendahl, C., and Kittler, H.
- **Citation:** Tschandl, P., Rosendahl, C., and Kittler, H. (2018). "The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions." *Scientific Data*, 5, 180161.
- **License:** CC BY-NC 4.0
- **DOI:** [10.1038/sdata.2018.161](https://doi.org/10.1038/sdata.2018.161)
- **Source:** [Harvard Dataverse / ISIC Archive](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T)
- **Records:** Metadata only (no images). 10,015 lesion records.
- **Modifications:** Image pixel data not included. Only tabular metadata (lesion type, location, age, sex, diagnosis) is used. Diagnosis binarised to benign vs. malignant.
- **Non-commercial note:** This dataset restricts use to non-commercial purposes. This project is academic and non-commercial. If the project scope changes to commercial use, this dataset must be removed.

### 3.13 DR Debrecen (Diabetic Retinopathy)

- **Specialty:** Ophthalmology
- **Authors:** Antal, B. and Hajdu, A.
- **Citation:** Antal, B. and Hajdu, A. (2014). "An Ensemble-based System for Automatic Screening of Diabetic Retinopathy." *Knowledge-Based Systems*, 60, 20-27.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5XP4P](https://doi.org/10.24432/C5XP4P)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/329/diabetic+retinopathy+debrecen)
- **Records:** 1,151 observations
- **Modifications:** Column names expanded from numeric indices to descriptive clinical names.

### 3.14 Vertebral Column

- **Specialty:** Orthopaedics
- **Authors:** Barreto, G.A. and Neto, A.R.
- **Citation:** Barreto, G.A. and Neto, A.R. (2005). "Vertebral Column." UCI Machine Learning Repository.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5K89B](https://doi.org/10.24432/C5K89B)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/212/vertebral+column)
- **Records:** 310 patients (2-class version)
- **Modifications:** Used the 2-class (Normal/Abnormal) version. Column names expanded to full biomechanical terms.

### 3.15 PhysioNet Sepsis 2019

- **Specialty:** ICU / Sepsis
- **Authors:** Reyna, M.A., Josef, C.S., Jeter, R., Shashikumar, S.P., Westover, M.B., Nemati, S., Clifford, G.D., and Sharma, A.
- **Citation:** Reyna, M.A. et al. (2020). "Early Prediction of Sepsis from Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019." *Critical Care Medicine*, 48(2), 210-217.
- **License:** CC BY 4.0
- **DOI:** [10.13026/v64v-d857](https://doi.org/10.13026/v64v-d857)
- **Source:** [PhysioNet](https://physionet.org/content/challenge-2019/1.0.0/)
- **Records:** Downsampled from approximately 40,000 to 5,000 patient-hours for educational use.
- **Modifications:** Downsampled to 5,000 records. Time-series data aggregated to per-patient summary statistics (mean, min, max of vital signs and lab values).

### 3.16 Cardiotocography

- **Specialty:** Obstetrics
- **Authors:** Campos, D. and Bernardes, J.
- **Citation:** Campos, D. and Bernardes, J. (2000). "Cardiotocography." UCI Machine Learning Repository.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C51S4N](https://doi.org/10.24432/C51S4N)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/193/cardiotocography)
- **Records:** 2,126 fetal cardiotocograms
- **Modifications:** Used the 3-class (Normal/Suspect/Pathological) classification. Column names expanded from abbreviations.

### 3.17 Arrhythmia

- **Specialty:** Cardiology (Arrhythmia)
- **Authors:** Guvenir, H.A., Acar, B., Demiroz, G., and Cekin, A.
- **Citation:** Guvenir, H.A. et al. (1997). "Arrhythmia." UCI Machine Learning Repository.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5BS32](https://doi.org/10.24432/C5BS32)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/5/arrhythmia)
- **Records:** 452 patients
- **Modifications:** Multi-class target binarised to arrhythmia present (1) vs. normal (0). High-missingness columns (>50% missing) removed.

### 3.18 Cervical Cancer Risk Factors

- **Specialty:** Oncology (Cervical)
- **Authors:** Fernandes, K., Cardoso, J.S., and Fernandes, J.
- **Citation:** Fernandes, K., Cardoso, J.S., and Fernandes, J. (2017). "Transfer Learning with Partial Observability Applied to Cervical Cancer Screening." *Iberian Conference on Pattern Recognition and Image Analysis*.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5Z310](https://doi.org/10.24432/C5Z310)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors)
- **Records:** 858 patients
- **Modifications:** "?" placeholders replaced with NaN. Biopsy column used as target variable.

### 3.19 New Thyroid

- **Specialty:** Thyroid / Endocrinology
- **Authors:** Quinlan, R.
- **Citation:** Quinlan, R. (1986). "Thyroid Disease." UCI Machine Learning Repository.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5D010](https://doi.org/10.24432/C5D010)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/102/thyroid+disease)
- **Records:** 215 patients
- **Modifications:** Column names added (original dataset has no header row). Class labels mapped to hypo/hyper/normal.

### 3.20 Diabetes 130-US Hospitals

- **Specialty:** Pharmacy / Readmission
- **Authors:** Clore, J., Cios, K., DeShazo, J., and Strack, B.
- **Citation:** Strack, B., DeShazo, J., Gennings, C., Olmo, J.L., Ventura, S., Cios, K., and Clore, J. (2014). "Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records." *BioMed Research International*, 2014.
- **License:** CC BY 4.0
- **DOI:** [10.24432/C5230J](https://doi.org/10.24432/C5230J)
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)
- **Records:** Downsampled from approximately 100,000 to 5,000 records for educational use.
- **Modifications:** Downsampled to 5,000 records. Readmission target simplified to binary (readmitted within 30 days vs. not). ICD-9 codes mapped to human-readable diagnosis groups. Encounter and patient ID columns removed.

---

## 4. EU AI Act Compliance -- Data Documentation

This section addresses the data governance and documentation requirements relevant to AI
systems under the EU AI Act (Regulation (EU) 2024/1689), specifically Articles 10 and 11.

While this project is an **educational tool** and not a deployed clinical AI system, we
document compliance as a learning exercise aligned with the course objectives (SENG 430
Software Quality Assurance).

### Article 10 -- Data and Data Governance

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Training data sources documented | DONE | Section 3 of this document lists every dataset with full provenance. |
| Data collection methodology described | DONE | Each dataset entry includes the original authors, publication, and source URL. |
| Data preparation processes documented | DONE | Modifications are listed per dataset (downsampling, encoding, column renaming). |
| Bias and representativeness examined | DONE | Step 7 of the tool performs subgroup fairness analysis. Training data demographics are compared against reference populations. |
| Data quality measures applied | DONE | Missing value handling and outlier treatment are documented in Step 3 of the tool pipeline. |

### Article 11 -- Technical Documentation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| General description of the AI system | DONE | ML_Tool_User_Guide.md provides a complete user-facing description. |
| Data used for training and testing documented | DONE | This document (DATA_LICENSES.md) and ATTRIBUTION.md. |
| Metrics used to measure performance | DONE | Step 5 of the tool reports accuracy, sensitivity, specificity, precision, F1, and AUC-ROC. |
| Known limitations documented | DONE | Each specialty's clinical context screen describes limitations. Step 7 surfaces bias findings. |

### Article 52 -- Transparency

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Users informed they are interacting with an AI system | DONE | The tool clearly labels all outputs as AI-generated predictions, not clinical diagnoses. |
| Explainability provided | DONE | Step 6 provides SHAP-based feature importance and per-patient explanations. |

---

## 5. Academic and Non-Commercial Use Disclaimer

All datasets in this project are used exclusively for educational purposes within the
SENG 430 Software Quality Assurance course at Cankaya University. No dataset is used in
any commercial product, clinical decision support system, or patient-facing application.

The CC BY-NC 4.0 licensed dataset (HAM10000 Metadata) is included on the basis that this
project qualifies as non-commercial academic use. Should the project scope change to
include any commercial application, this dataset must be removed from the distribution.

For questions about dataset licensing or to report a compliance concern, contact the
project team through the course repository.

---

*This document was created as part of the dataset licensing audit for the
feat/dataset-licensing-docker-bundling branch.*
