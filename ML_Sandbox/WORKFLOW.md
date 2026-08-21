# AHRID ML Sandbox Workflow

Welcome to the ML Sandbox! This directory contains the **skeleton code** for the entire Machine Learning pipeline used in AHRID. 

The goal here is for you to learn and implement the pieces step-by-step from scratch.

## 🔄 The Machine Learning Workflow

Building an ML model is not just about calling `model.fit()`. It is a multi-step pipeline. In this sandbox, you will build the 4 major components:

### Step 1: Data Preparation (`step1_data_preparation.py`)
- **Objective:** Get your raw data (attempts) out of the database and into a structured format (like a Pandas DataFrame).
- **Why it matters:** ML models only understand numbers in matrices/tables.
- **Your Task:** Write the SQL query or SQLAlchemy code to fetch user attempts, correctness, response times, and difficulty.

### Step 2: Feature Engineering (`step2_feature_engineering.py`)
- **Objective:** Transform raw rows into intelligent "features" that describe a user's behavior.
- **Why it matters:** This is the most important step. A Random Forest cannot learn from raw clicks. It learns from features like `overall_accuracy`, `fast_attempt_rate`, and `phishing_accuracy`.
- **Your Task:** Write functions to calculate these aggregates for each user.

### Step 3: Supervised Learning - Random Forest (`step3_train_model.py`)
- **Objective:** Train an algorithm to predict a user's overall **Risk Level** (Critical, High, Medium, Low) based on the features you built in Step 2.
- **Why it matters:** This allows AHRID to automatically score users based on historical patterns, not just simple math.
- **Your Task:** Split the data into train/test sets, handle class imbalance (using SMOTE), train the `RandomForestClassifier`, and evaluate it (using F1 Score or Confusion Matrix).

### Step 4: Unsupervised Learning - KMeans Clustering (`step4_clustering.py`)
- **Objective:** Discover hidden patterns in user behavior without pre-defined labels. Group users into "archetypes" (e.g., *The Overconfident Clicker*, *The Cautious Learner*).
- **Why it matters:** This helps the Adaptive Engine know *how* to teach a user, not just *what* their risk score is.
- **Your Task:** Scale the feature data, choose the number of clusters (K=5), run KMeans, and analyze the center of each cluster to give them human-readable names.

---

## 🛠️ How to use this folder

1. **Start with Step 1**: Open `step1_data_preparation.py` and read the comments. Try to implement the missing code (`# TODO`).
2. **Move sequentially**: Don't jump to Step 3 until Step 2 is working, because Step 3 requires the output of Step 2!
3. **Run often**: Test your scripts by running them in the terminal: `python ML_Sandbox/step1_data_preparation.py`.
4. **Use your ML Guide**: When you get stuck, look at the `ML_Learning_Guide` chapters (e.g., `04_FEATURE_ENGINEERING.md`, `05_RANDOM_FOREST.md`) for the theoretical background and answers.

Happy coding! You can expand these scripts as you learn more.
