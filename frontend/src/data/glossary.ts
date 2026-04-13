export interface GlossaryEntry {
  title: string
  description: string
  learnMoreUrl?: string
}

export const GLOSSARY: Record<string, GlossaryEntry> = {
  // ── General ML Concepts ──
  machine_learning: {
    title: 'Machine Learning (ML)',
    description:
      'A branch of artificial intelligence where computers learn patterns from data instead of being explicitly programmed. In healthcare, ML can help identify patterns in patient data that may be difficult for humans to detect manually.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/intro-to-ml',
  },
  classification: {
    title: 'Classification',
    description:
      'A type of ML task where the model predicts which category a patient belongs to (e.g. "at risk" vs "not at risk"). The model learns from labelled examples and then predicts the category for new, unseen patients.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification',
  },
  binary_classification: {
    title: 'Binary Classification',
    description:
      'A classification task with exactly two possible outcomes — for example, "disease present" vs "disease absent". The model outputs a probability between 0 and 1, and a threshold (usually 0.5) determines the final prediction.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification',
  },
  multiclass: {
    title: 'Multi-class Classification',
    description:
      'A classification task with three or more possible categories — for example, classifying a tumour as "benign", "malignant", or "uncertain". The model predicts a probability for each category.',
  },
  target_variable: {
    title: 'Target Variable',
    description:
      'The outcome column that the ML model is trying to predict. In clinical terms, this is the diagnosis or condition you want the model to learn to identify — e.g. "diabetes_positive" or "readmission_30d".',
  },
  features: {
    title: 'Features',
    description:
      'The input measurements or characteristics used by the model to make predictions. In clinical terms, these are the patient attributes — lab values, vital signs, demographics — that the model examines.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/framing/ml-terminology',
  },

  // ── Data Preparation ──
  train_test_split: {
    title: 'Train / Test Split',
    description:
      'Dividing the dataset into two parts: a training set (used to teach the model) and a test set (used to evaluate it on unseen data). This simulates how the model would perform on new patients it has never encountered.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/training-and-test-sets',
  },
  missing_values: {
    title: 'Missing Values',
    description:
      'Data points that are absent in the dataset — for example, a lab test that was not performed for certain patients. Missing values must be handled before training because most ML models cannot process incomplete data.',
  },
  median_imputation: {
    title: 'Median Imputation',
    description:
      'Replacing missing numeric values with the median (middle value) of that column. The median is preferred over the mean because it is not affected by extreme outlier values — making it more robust for clinical data.',
  },
  mode_imputation: {
    title: 'Mode Imputation',
    description:
      'Replacing missing values with the most frequently occurring value in that column. This is typically used for categorical data (e.g. filling in the most common blood type when that field is missing).',
  },
  normalization: {
    title: 'Normalisation / Feature Scaling',
    description:
      'Transforming numeric features to a common scale so that no single measurement dominates the model simply because of its unit or range. For example, age (20–90) and blood glucose (70–400) are on very different scales.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/data-prep/transform/normalization',
  },
  zscore: {
    title: 'Z-Score Standardisation',
    description:
      'Transforms each value to show how many standard deviations it is from the mean. After transformation, the data has a mean of 0 and standard deviation of 1. This is the most commonly recommended scaling method.',
  },
  minmax: {
    title: 'Min-Max Scaling',
    description:
      'Rescales all values to the 0–1 range using the formula: (value − min) / (max − min). Simple and intuitive, but can be sensitive to extreme outliers that stretch the range.',
  },
  smote: {
    title: 'SMOTE (Synthetic Minority Oversampling)',
    description:
      'A technique that creates new synthetic examples of the under-represented class by interpolating between existing similar patients. This helps the model learn both outcomes equally, rather than being biased toward the majority class. Applied only to training data.',
    learnMoreUrl: 'https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html',
  },
  class_imbalance: {
    title: 'Class Imbalance',
    description:
      'When one outcome is much more common than another in the dataset — e.g. 90% of patients are healthy, only 10% have the condition. An imbalanced dataset can cause the model to always predict the majority class and miss rare but important cases.',
  },
  class_distribution: {
    title: 'Class Distribution',
    description:
      'The proportion of each outcome category in the dataset. For example, "60% negative, 40% positive". Understanding this distribution is important because severe imbalance can bias the model toward the more common class.',
  },
  outlier_handling: {
    title: 'Outlier Handling',
    description:
      'Methods for dealing with extreme values that differ significantly from other observations. Outliers can occur due to measurement errors or genuinely unusual patients, and they can disproportionately influence certain ML models.',
  },
  iqr_clipping: {
    title: 'IQR Clipping',
    description:
      'Limits extreme values using the Interquartile Range (IQR = Q3 − Q1). Any value below Q1 − 1.5×IQR or above Q3 + 1.5×IQR is clipped to the boundary. This is the same method used in box-plot whiskers.',
  },
  zscore_clipping: {
    title: 'Z-Score Clipping',
    description:
      'Clips values that are more than 3 standard deviations from the mean. In a normal distribution, 99.7% of values fall within this range, so values beyond it are typically considered extreme outliers.',
  },

  // ── Models ──
  knn: {
    title: 'K-Nearest Neighbours (KNN)',
    description:
      'Classifies a new patient by finding the K most similar past patients in the training data and taking a majority vote. Like consulting the most similar past cases to make a prediction. Simple, transparent, and requires no training phase.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/neighbors.html',
  },
  svm: {
    title: 'Support Vector Machine (SVM)',
    description:
      'Finds the optimal boundary (hyperplane) that best separates different patient groups. Imagine drawing the clearest possible dividing line between two clusters of patients on a graph. Effective for complex, non-linear patterns.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/svm.html',
  },
  decision_tree: {
    title: 'Decision Tree',
    description:
      'Makes predictions by asking a series of yes/no questions about patient measurements — similar to a clinical decision pathway. Very interpretable: you can follow the exact path from data to prediction. Can overfit if the tree is too deep.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/tree.html',
  },
  random_forest: {
    title: 'Random Forest',
    description:
      'Trains many decision trees simultaneously, each on a slightly different subset of data, and takes the majority vote. This "wisdom of crowds" approach produces more stable and accurate predictions than a single tree.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees',
  },
  logistic_regression: {
    title: 'Logistic Regression',
    description:
      'Calculates the probability of each outcome using a weighted sum of patient measurements. Despite its name, it is used for classification, not regression. One of the most interpretable models — each feature gets a clear weight showing its contribution.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression',
  },
  naive_bayes: {
    title: 'Naive Bayes',
    description:
      'Uses Bayes\' probability theorem to estimate how likely each outcome is given the patient\'s measurements. Called "naive" because it assumes all features are independent. Very fast and works well with small datasets.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/naive_bayes.html',
  },
  xgboost: {
    title: 'XGBoost (Extreme Gradient Boosting)',
    description:
      'A powerful ensemble method that builds decision trees sequentially — each new tree corrects the mistakes of the previous ones. Widely used in healthcare research and ML competitions for its high accuracy and speed.',
    learnMoreUrl: 'https://xgboost.readthedocs.io/en/stable/',
  },
  lightgbm: {
    title: 'LightGBM (Light Gradient Boosting)',
    description:
      'Similar to XGBoost but optimised for speed and memory efficiency. Uses a histogram-based approach to handle large datasets faster. A good choice when dealing with many features or large patient cohorts.',
    learnMoreUrl: 'https://lightgbm.readthedocs.io/en/stable/',
  },

  // ── Model Parameters ──
  n_neighbors: {
    title: 'K (Number of Neighbours)',
    description:
      'In KNN, K determines how many similar past patients are consulted. A small K (e.g. 3) is more flexible but may be noisy. A large K (e.g. 15) gives smoother predictions but may miss subtle patterns. There is no universally "correct" K — it depends on the data.',
  },
  kernel: {
    title: 'Kernel Function',
    description:
      'In SVM, the kernel transforms data into a higher-dimensional space to find better separation boundaries. "RBF" (radial basis function) is the most common choice and works well for non-linear patterns. "Linear" is simpler and faster.',
  },
  regularization_c: {
    title: 'C (Regularisation Strength)',
    description:
      'Controls how strictly the model fits the training data. A high C forces the model to fit training data closely (risk of overfitting). A low C allows more generalisation errors in training, which often leads to better performance on new patients.',
  },
  max_depth: {
    title: 'Maximum Depth',
    description:
      'The maximum number of sequential questions a decision tree can ask. A deeper tree can capture more complex patterns but is more likely to overfit. Shallower trees are simpler and generalise better. Think of it as limiting how detailed the clinical pathway is.',
  },
  n_estimators: {
    title: 'Number of Trees',
    description:
      'How many decision trees are built in an ensemble model (Random Forest, XGBoost, LightGBM). More trees generally improve stability and accuracy, but increase computation time. Typically 100–300 trees is a good starting point.',
  },
  learning_rate: {
    title: 'Learning Rate',
    description:
      'Controls how much each new tree contributes to the ensemble in gradient boosting (XGBoost, LightGBM). A lower learning rate (e.g. 0.01) makes the model learn more slowly but often achieves better generalisation — especially with more trees.',
  },
  criterion_gini_entropy: {
    title: 'Split Criterion (Gini / Entropy)',
    description:
      'The mathematical rule used to decide the best yes/no question at each node of a decision tree. "Gini" measures impurity; "Entropy" measures information gain. In practice, both produce very similar results.',
  },
  distance_metric: {
    title: 'Distance Metric',
    description:
      'The formula used by KNN to measure similarity between patients. "Euclidean" is straight-line distance (Pythagorean theorem). "Manhattan" sums the absolute differences along each axis. Euclidean is the default and works well for most clinical data.',
  },
  hyperparameter_tuning: {
    title: 'Hyperparameter Tuning',
    description:
      'The process of systematically trying different parameter combinations to find the settings that produce the best model performance. Like adjusting the settings on medical equipment until you get the optimal reading.',
  },
  feature_selection: {
    title: 'Feature Selection',
    description:
      'Automatically identifying which patient measurements are most relevant and removing the rest. This can improve model performance by reducing noise, make the model faster, and produce more interpretable results.',
  },
  auto_retrain: {
    title: 'Auto-Retrain',
    description:
      'When enabled, the model automatically retrains itself every time you adjust a parameter. This gives instant feedback on how each change affects performance, making it easier to find the best settings.',
  },

  // ── Performance Metrics ──
  accuracy: {
    title: 'Accuracy',
    description:
      'The percentage of all test patients that the model classified correctly. Simple and intuitive, but can be misleading with imbalanced data — a model that always predicts "healthy" could have 95% accuracy if only 5% of patients are sick.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification/accuracy',
  },
  sensitivity: {
    title: 'Sensitivity (Recall / True Positive Rate)',
    description:
      'Of all patients who actually HAD the condition, what percentage did the model correctly identify? The most critical metric for clinical screening — a low sensitivity means the model is missing real cases, which can delay diagnosis.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall',
  },
  specificity: {
    title: 'Specificity (True Negative Rate)',
    description:
      'Of all patients who did NOT have the condition, what percentage did the model correctly identify as safe? High specificity means fewer false alarms, reducing unnecessary follow-up tests and patient anxiety.',
  },
  precision: {
    title: 'Precision (Positive Predictive Value)',
    description:
      'Of all patients the model flagged as positive, what percentage actually had the condition? High precision means fewer false alarms. In clinical settings, low precision leads to unnecessary procedures, costs, and patient stress.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall',
  },
  f1_score: {
    title: 'F1 Score',
    description:
      'The harmonic mean of Sensitivity and Precision — a single number that balances both. F1 is particularly useful when you need a model that both catches most positive cases AND does not generate too many false alarms.',
  },
  auc_roc: {
    title: 'AUC-ROC',
    description:
      'Area Under the ROC Curve — measures how well the model distinguishes between positive and negative patients across all possible thresholds. 0.5 = random guessing, 1.0 = perfect separation. AUC above 0.8 is generally considered good.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc',
  },
  mcc: {
    title: 'MCC (Matthews Correlation Coefficient)',
    description:
      'A balanced metric that considers all four confusion matrix categories (TP, TN, FP, FN). Ranges from −1 (total disagreement) to +1 (perfect prediction). Unlike accuracy, MCC is informative even with imbalanced classes.',
  },

  // ── Confusion Matrix ──
  confusion_matrix: {
    title: 'Confusion Matrix',
    description:
      'A table showing how many patients the model classified correctly and incorrectly. Each cell represents a combination of the actual condition and the model\'s prediction. It gives a complete picture of where the model succeeds and fails.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification/true-false-positive-negative',
  },
  true_positive: {
    title: 'True Positive (TP)',
    description:
      'A patient who actually had the condition AND the model correctly identified them as positive. This is the ideal outcome for sick patients — the model caught the real case.',
  },
  true_negative: {
    title: 'True Negative (TN)',
    description:
      'A patient who did NOT have the condition AND the model correctly identified them as safe. This is the ideal outcome for healthy patients — no unnecessary alarm.',
  },
  false_positive: {
    title: 'False Positive (FP)',
    description:
      'A patient who did NOT have the condition but was incorrectly flagged as positive by the model. Also called a "false alarm". Leads to unnecessary follow-up tests, procedures, and patient anxiety.',
  },
  false_negative: {
    title: 'False Negative (FN)',
    description:
      'A patient who actually HAD the condition but was missed by the model — predicted as negative. This is the most dangerous error in clinical screening because it can delay diagnosis and treatment.',
  },

  // ── Curves ──
  roc_curve: {
    title: 'ROC Curve',
    description:
      'A graph plotting Sensitivity (True Positive Rate) against 1-Specificity (False Positive Rate) at every possible threshold. The further the curve bows toward the top-left corner, the better the model. The diagonal line represents random guessing.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc',
  },
  pr_curve: {
    title: 'Precision-Recall Curve',
    description:
      'A graph plotting Precision against Recall (Sensitivity) at every threshold. Especially useful with imbalanced datasets where the ROC curve can be overly optimistic. A higher area under the PR curve indicates better performance.',
  },

  // ── Validation ──
  cross_validation: {
    title: 'Cross-Validation',
    description:
      'A technique that splits the data into K "folds" and trains the model K times — each time using a different fold as the test set. This gives a more reliable estimate of model performance than a single train/test split, reducing the influence of which patients happen to be in the test set.',
    learnMoreUrl: 'https://scikit-learn.org/stable/modules/cross_validation.html',
  },
  overfitting: {
    title: 'Overfitting',
    description:
      'When a model learns the training data too well — memorising noise and peculiarities rather than genuine patterns. An overfit model performs excellently on training data but poorly on new, unseen patients. Detected by a large gap between training and test accuracy.',
    learnMoreUrl: 'https://developers.google.com/machine-learning/crash-course/generalization',
  },

  // ── Explainability ──
  feature_importance: {
    title: 'Feature Importance (Global)',
    description:
      'A ranking of which patient measurements had the most influence on the model\'s predictions overall. Helps clinicians verify that the model is using medically sensible features — if irrelevant features rank high, the model may be unreliable.',
  },
  shap_values: {
    title: 'SHAP Values',
    description:
      'SHapley Additive exPlanations — a method from game theory that explains how much each feature contributed to a specific prediction. Positive SHAP values push the prediction toward risk; negative values push it away. Provides transparent, per-patient explanations.',
    learnMoreUrl: 'https://shap.readthedocs.io/en/latest/',
  },
  shap_waterfall: {
    title: 'SHAP Waterfall Chart',
    description:
      'A visualisation showing how each feature\'s SHAP value pushed the prediction from the base probability to the final prediction. Bars going right (positive) increase risk; bars going left (negative) decrease risk.',
  },
  base_value: {
    title: 'Base Value',
    description:
      'The average model prediction across all training patients — the starting probability before any individual patient\'s features are considered. Each feature\'s SHAP value then adds or subtracts from this base to arrive at the final prediction.',
  },
  what_if_analysis: {
    title: 'What-If Analysis',
    description:
      'A simulation that shows how changing a single clinical measurement would affect the model\'s prediction. For example: "If this patient\'s blood glucose were 150 instead of 200, would the predicted risk change?" Useful for understanding feature sensitivity.',
  },

  // ── Ethics & Fairness ──
  bias: {
    title: 'Bias in AI',
    description:
      'Systematic errors in a model\'s predictions that unfairly disadvantage certain patient groups. Bias can originate from historical data (e.g. underrepresentation of certain demographics), feature selection, or the learning algorithm itself. Detecting and mitigating bias is essential for fair clinical use.',
  },
  subgroup_fairness: {
    title: 'Subgroup Fairness',
    description:
      'Evaluating whether the model performs equally well across different patient groups (e.g. age, gender, ethnicity). A fair model should not have significantly lower sensitivity or accuracy for any particular demographic group.',
  },
  sensitivity_gap: {
    title: 'Sensitivity Gap',
    description:
      'The difference in sensitivity (recall) between patient subgroups. For example, if sensitivity is 85% for males but only 60% for females, there is a 25 percentage point gap — indicating potential bias that could lead to missed diagnoses in one group.',
  },
  training_representation: {
    title: 'Training Data Representation',
    description:
      'How well the distribution of patient demographics in the training data reflects the real-world population. Under-representation of certain groups (e.g. only 5% elderly patients when they are 20% of the target population) can cause the model to perform poorly for those groups.',
  },
  eu_ai_act: {
    title: 'EU AI Act',
    description:
      'The European Union\'s regulatory framework for artificial intelligence (effective from 2024). It classifies AI systems by risk level and imposes strict requirements on "high-risk" applications, including healthcare. Requirements include transparency, human oversight, data governance, and bias testing.',
    learnMoreUrl: 'https://artificialintelligenceact.eu/',
  },

  // ── Fairness Status Labels ──
  status_ok: {
    title: 'Status: OK (Acceptable)',
    description:
      'The model\'s performance for this patient group meets all fairness thresholds: all metrics are above 65% and the sensitivity gap compared to other groups is 10 percentage points or less. No immediate action required.',
  },
  status_review: {
    title: 'Status: Review Needed',
    description:
      'The model\'s performance for this patient group shows some concern: at least one metric is below 65% or the sensitivity gap exceeds 10 percentage points. A clinician should review whether this level of performance is acceptable for the intended use case.',
  },
  status_action_needed: {
    title: 'Status: Action Needed',
    description:
      'The model\'s performance for this patient group is significantly below acceptable thresholds: sensitivity is below 50% or the gap exceeds 20 percentage points. This means the model may miss more than half the positive cases in this group. Do not use this model for this patient population without improvement.',
  },

  // ── Data Exploration ──
  class_balance: {
    title: 'Class Balance',
    description:
      'The ratio of different outcome categories in the dataset. A balanced dataset (e.g. 50:50) gives the model equal opportunity to learn both outcomes. An imbalanced dataset (e.g. 95:5) can cause the model to ignore the rare class.',
  },
  missing_percentage: {
    title: 'Missing Percentage',
    description:
      'The proportion of values that are absent across the dataset. A high missing percentage (>20%) may affect model reliability. Columns with many missing values might need imputation or removal before training.',
  },
}
