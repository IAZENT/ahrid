# 🧠 ML Learning Roadmap

> A structured learning path for the ML techniques used in AHRID.
> Check off items as you complete them.

---

## Week 1: Foundations + Random Forest

### Videos
- [x] StatQuest: [Decision Trees](https://www.youtube.com/watch?v=7VeUPuFGJHk)
- [x] StatQuest: [Random Forest Part 1](https://www.youtube.com/watch?v=J4Wdy0Wc_xQ)
- [x] StatQuest: [Random Forest Part 2](https://www.youtube.com/watch?v=sQ870ber_rg)
- [x] StatQuest: [Cross Validation](https://www.youtube.com/watch?v=fSytzGwwBVw)

### Hands-On
- [x] [Kaggle: Intro to ML Course](https://www.kaggle.com/learn/intro-to-machine-learning)
- [ ] [Kaggle Titanic Competition](https://www.kaggle.com/c/titanic) - build a Random Forest classifier
- [ ] Run your own `ML_Sandbox/step3_train_model.py` and understand every line

### Reading
- [ ] Scikit-learn: [Random Forest docs](https://scikit-learn.org/stable/modules/ensemble.html#random-forests)

---

## Week 2: K-Means Clustering

### Videos
- [x] StatQuest: [K-Means Clustering](https://www.youtube.com/watch?v=4b5d3muPQmA)
- [ ] StatQuest: [Silhouette Score](https://www.youtube.com/watch?v=RAa0sByNMPk)
- [ ] StatQuest: [Hierarchical Clustering](https://www.youtube.com/watch?v=7xHsRkOdVwo) (for comparison)

### Hands-On
- [ ] Cluster the Iris dataset yourself in a Jupyter notebook
- [ ] Try different K values and plot the elbow curve
- [ ] Run your own `ML_Sandbox/step4_clustering.py` and understand every line
- [ ] [Kaggle: Customer Segmentation dataset](https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial)

### Reading
- [ ] Scikit-learn: [K-Means docs](https://scikit-learn.org/stable/modules/clustering.html#k-means)

---

## Week 3: SMOTE & Imbalanced Data

### Videos
- [ ] [SMOTE Explained Simply](https://www.youtube.com/watch?v=FheTHaQIo_o)
- [ ] StatQuest: [Sensitivity and Specificity](https://www.youtube.com/watch?v=vP06aMoz4v8)
- [ ] StatQuest: [ROC and AUC](https://www.youtube.com/watch?v=4jRBRDbJemM)

### Hands-On
- [ ] [Kaggle: Credit Card Fraud Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) - apply SMOTE
- [ ] Compare model performance with and without SMOTE
- [ ] Try different SMOTE variants (BorderlineSMOTE, ADASYN)

### Reading
- [ ] [imbalanced-learn SMOTE docs](https://imbalanced-learn.org/stable/over_sampling.html)
- [ ] Chawla et al. (2002) - original SMOTE paper

---

## Week 4: SHAP & Explainability

### Videos
- [ ] [SHAP Explained in 5 Minutes](https://www.youtube.com/watch?v=VB9uV-x0gtg)
- [ ] StatQuest: [Shapley Values](https://www.youtube.com/watch?v=NBg7YirBMwg)

### Hands-On
- [ ] Install shap: `pip install shap`
- [ ] Generate SHAP summary plot for your trained RF model
- [ ] Generate SHAP force plot for a single prediction
- [ ] Generate SHAP dependence plot for top 3 features

### Reading
- [ ] [SHAP official docs](https://shap.readthedocs.io/)
- [ ] [Interpretable ML Book - Chapter 5 & 6](https://christophm.github.io/interpretable-ml-book/)

---

## Week 5: Feature Engineering + Putting It All Together

### Videos
- [ ] [Kaggle: Feature Engineering Course](https://www.kaggle.com/learn/feature-engineering)

### Hands-On
- [ ] Revisit `ML_Sandbox/step2_feature_engineering.py` with fresh eyes
- [ ] Try adding/removing features and see how RF accuracy changes
- [ ] Create a full pipeline notebook: data → features → SMOTE → train → cluster → SHAP

### Reading
- [ ] Scikit-learn: [Pipelines](https://scikit-learn.org/stable/modules/compose.html#pipeline)

---

## 🔗 Bookmark These

| Resource | URL |
|----------|-----|
| StatQuest YouTube | https://www.youtube.com/@statquest |
| Kaggle Learn | https://www.kaggle.com/learn |
| Scikit-learn User Guide | https://scikit-learn.org/stable/user_guide.html |
| Google ML Crash Course | https://developers.google.com/machine-learning/crash-course |
| Interpretable ML Book | https://christophm.github.io/interpretable-ml-book/ |
| Google Colab | https://colab.research.google.com/ |
| Connected Papers | https://connectedpapers.com/ |
| Semantic Scholar | https://www.semanticscholar.org/ |
