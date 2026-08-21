"""
Step 3: Supervised Learning (Random Forest) Skeleton
Objective: Train a model to predict user Risk Levels based on features.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
# TODO: pip install imbalanced-learn if you want to use SMOTE
# from imblearn.over_sampling import SMOTE 

from step2_feature_engineering import engineer_features
from step1_data_preparation import load_raw_data

def train_risk_model(features_df: pd.DataFrame):
    """
    Train a Random Forest to predict risk levels.
    """
    print("Preparing data for training...")
    
    # For supervised learning, we need 'X' (features) and 'y' (target labels)
    # Since we are using dummy data, we will create fake 'y' labels for testing
    
    # TODO: In real life, 'y' comes from the rule-based risk_scorer.py
    # For the sandbox, let's assign a fake risk label (0=Low, 1=Medium, 2=High, 3=Critical)
    import numpy as np
    np.random.seed(42)
    features_df['risk_label'] = np.random.choice([0, 1, 2, 3], size=len(features_df))
    
    # Define X (drop user_id and the label)
    X = features_df.drop(columns=['user_id', 'risk_label'])
    y = features_df['risk_label']
    
    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # TODO: Optional - apply SMOTE to X_train and y_train here to balance classes
    
    print("Training Random Forest Classifier...")
    # Initialize the model
    # n_estimators is the number of trees in the forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Train (fit) the model
    model.fit(X_train, y_train)
    
    # Evaluate the model
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    return model

if __name__ == "__main__":
    raw_df = load_raw_data()
    features_df = engineer_features(raw_df)
    
    # Need more fake data for train_test_split to work without errors
    # Duplicating our small dummy dataframe
    large_features = pd.concat([features_df]*20, ignore_index=True)
    large_features['user_id'] = [f"user_{i}" for i in range(len(large_features))]
    
    model = train_risk_model(large_features)
    print("Model training complete!")
