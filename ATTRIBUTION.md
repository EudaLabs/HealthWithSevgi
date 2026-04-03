# Attribution -- Bundled Datasets

This file lists the datasets bundled in the ML Visualization Tool Docker image and their
required attributions. For full licensing details, see [DATA_LICENSES.md](DATA_LICENSES.md).

This project is academic and non-commercial.

---

## 1. Heart Failure Clinical Records

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Chicco, D. and Jurman, G. (2020). *BMC Medical Informatics and Decision Making*, 20, 16.
- **DOI:** [10.24432/C5Z89R](https://doi.org/10.24432/C5Z89R)
- **Modifications:** Column names standardised to snake_case.

## 2. NIH Chest X-Ray Metadata

- **License:** [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (Public Domain)
- **Authors:** Wang, X., Peng, Y., Lu, L., Lu, Z., Bagheri, M., and Summers, R.M. (2017). NIH Clinical Center.
- **Modifications:** Downsampled to 5,000 records. Finding labels binarised. Images not included.

## 3. Chronic Kidney Disease

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Rubini, L., Soundarapandian, P., and Eswaran, P. (2015).
- **DOI:** [10.24432/C5G020](https://doi.org/10.24432/C5G020)
- **Modifications:** Column names expanded from abbreviations.

## 4. Breast Cancer Wisconsin (Diagnostic)

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Wolberg, W.H., Mangasarian, O.L., and Street, W.N. (1993).
- **DOI:** [10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B)
- **Modifications:** ID column removed. Diagnosis mapped to binary.

## 5. Parkinson's Disease

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Little, M. (2007). *IEEE Transactions on Biomedical Engineering*.
- **DOI:** [10.24432/C59C74](https://doi.org/10.24432/C59C74)
- **Modifications:** Patient name column removed.

## 6. Pima Indians Diabetes

- **License:** [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (Kaggle) / [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (UCI)
- **Authors:** Smith, J.W., Everhart, J.E., et al. (1988). NIDDK.
- **Modifications:** Zero values in physiological columns replaced with NaN.

## 7. Indian Liver Patient

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Ramana, B.V. and Venkateswarlu, N.B. (2012).
- **DOI:** [10.24432/C5D02C](https://doi.org/10.24432/C5D02C)
- **Modifications:** Target column renamed. Gender label-encoded.

## 8. Depression Dataset

- **License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Authors:** Anthony Therrien. Kaggle.
- **Modifications:** Severity classes consolidated. Column names standardised. Derivative distributed under CC BY-SA 4.0.

## 9. COPD Dataset

- **License:** [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (Public Domain)
- **Authors:** Prakhar Rathi. UCL Datasets Library / Kaggle.
- **Modifications:** Column names standardised. Exacerbation target binarised.

## 10. HAM10000 Metadata

- **License:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) -- Non-commercial use only
- **Authors:** Tschandl, P., Rosendahl, C., and Kittler, H. (2018). *Scientific Data*, 5, 180161.
- **DOI:** [10.1038/sdata.2018.161](https://doi.org/10.1038/sdata.2018.161)
- **Modifications:** Image data not included; tabular metadata only. Diagnosis binarised.

## 11. DR Debrecen (Diabetic Retinopathy)

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Antal, B. and Hajdu, A. (2014). *Knowledge-Based Systems*, 60, 20-27.
- **DOI:** [10.24432/C5XP4P](https://doi.org/10.24432/C5XP4P)
- **Modifications:** Column names expanded from numeric indices.

## 12. Vertebral Column

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Barreto, G.A. and Neto, A.R. (2005).
- **DOI:** [10.24432/C5K89B](https://doi.org/10.24432/C5K89B)
- **Modifications:** Used 2-class version. Column names expanded.

## 13. PhysioNet Sepsis 2019

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Reyna, M.A., Josef, C.S., Jeter, R., et al. (2020). *Critical Care Medicine*, 48(2), 210-217.
- **DOI:** [10.13026/v64v-d857](https://doi.org/10.13026/v64v-d857)
- **Modifications:** Downsampled to 5,000 records. Time-series aggregated to per-patient summaries.

## 14. Cardiotocography

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Campos, D. and Bernardes, J. (2000).
- **DOI:** [10.24432/C51S4N](https://doi.org/10.24432/C51S4N)
- **Modifications:** Used 3-class version. Column names expanded.

## 15. Arrhythmia

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Guvenir, H.A., Acar, B., et al. (1997).
- **DOI:** [10.24432/C5BS32](https://doi.org/10.24432/C5BS32)
- **Modifications:** Target binarised to arrhythmia/normal. High-missingness columns removed.

## 16. Cervical Cancer Risk Factors

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Fernandes, K., Cardoso, J.S., and Fernandes, J. (2017).
- **DOI:** [10.24432/C5Z310](https://doi.org/10.24432/C5Z310)
- **Modifications:** Placeholder values replaced with NaN.

## 17. New Thyroid

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Quinlan, R. (1986).
- **DOI:** [10.24432/C5D010](https://doi.org/10.24432/C5D010)
- **Modifications:** Column headers added. Class labels mapped to clinical names.

## 18. Diabetes 130-US Hospitals

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Authors:** Clore, J., Cios, K., DeShazo, J., and Strack, B. (2014). *BioMed Research International*.
- **DOI:** [10.24432/C5230J](https://doi.org/10.24432/C5230J)
- **Modifications:** Downsampled to 5,000 records. Readmission target binarised. ICD-9 codes mapped to readable names. ID columns removed.

---

## Datasets NOT Bundled (Auto-Downloaded at Runtime)

The following datasets are **not included** in the Docker image and are downloaded
automatically when the user selects the corresponding specialty:

- **Stroke Prediction Dataset** (Kaggle, fedesoriano) -- No formal license. Educational use only.
- **Anaemia Classification Dataset** (Kaggle, Biswa Ranjan Rao) -- License unknown.

---

*See [DATA_LICENSES.md](DATA_LICENSES.md) for complete licensing details, EU AI Act
compliance documentation, and source URLs.*
