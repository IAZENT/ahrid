"""
Step 2: Feature Engineering Skeleton
Objective: Aggregate raw attempt rows into user-level features.
"""

import pandas as pd
from step1_data_preparation import load_raw_data

def engineer_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw attempt data into user-level features.
    
    Args:
        raw_df (pd.DataFrame): The raw attempts dataframe.
        
    Returns:
        pd.DataFrame: A new dataframe where each row represents ONE USER 
                      and columns are engineered features.
    """
    print("Engineering features...")
    
    # We want to group the data by user_id
    grouped = raw_df.groupby('user_id')
    
    # Feature 1: Total Attempts
    total_attempts = grouped.size()
    
    # Feature 2: Overall Accuracy
    # is_correct is boolean (True=1, False=0), so the mean is the accuracy %
    overall_accuracy = grouped['is_correct'].mean()
    
    # Feature 3: Average Response Time
    avg_response_time = grouped['response_time_ms'].mean()
    
    # TODO: Add more features! 
    # For example: 
    # - fast_attempt_rate: What percentage of answers were under 2000ms?
    # - phishing_accuracy: Accuracy specifically on 'phishing' category questions.
    
    # Combine features into a single user-level dataframe
    features_df = pd.DataFrame({
        'total_attempts': total_attempts,
        'overall_accuracy': overall_accuracy,
        'avg_response_time': avg_response_time
        # TODO: Add your new features here
    }).reset_index()
    
    print(f"Engineered features for {len(features_df)} users.")
    return features_df

if __name__ == "__main__":
    # Test your function
    raw_df = load_raw_data()
    features_df = engineer_features(raw_df)
    print("Engineered Features:")
    print(features_df)
