"""
Step 1: Data Preparation Skeleton
Objective: Fetch raw attempt data and convert it into a Pandas DataFrame.
"""

import pandas as pd
# TODO: Import your database models here if needed
# from app.models.attempt import Attempt

def load_raw_data() -> pd.DataFrame:
    """
    Load raw attempt data into a DataFrame.
    
    Returns:
        pd.DataFrame: A dataframe where each row is a single attempt.
    """
    print("Loading raw data...")
    
    # TODO: Connect to the database and query all attempts
    # For now, we will create a dummy dataframe to simulate raw data
    
    dummy_data = {
        'user_id': ['user1', 'user1', 'user2', 'user2', 'user3'],
        'category': ['phishing', 'vishing', 'phishing', 'smishing', 'phishing'],
        'is_correct': [True, False, True, True, False],
        'response_time_ms': [2500, 1200, 3400, 4500, 1500],
        'difficulty': [1, 2, 1, 3, 2]
    }
    
    df = pd.DataFrame(dummy_data)
    print(f"Loaded {len(df)} attempts.")
    return df

if __name__ == "__main__":
    # Test your function
    df = load_raw_data()
    print("Sample data:")
    print(df.head())
