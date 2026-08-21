"""
Step 4: Unsupervised Learning (KMeans Clustering) Skeleton
Objective: Group users into archetypes based on behavior.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from step2_feature_engineering import engineer_features
from step1_data_preparation import load_raw_data

def cluster_users(features_df: pd.DataFrame):
    """
    Run KMeans clustering to find user archetypes.
    """
    print("Preparing data for clustering...")
    
    # Define X (features). We don't need 'y' because this is unsupervised!
    X = features_df.drop(columns=['user_id'])
    
    # IMPORTANT: KMeans relies on distance (geometry). 
    # Response time is in thousands (ms), accuracy is 0-1. 
    # We MUST scale the data so all features are on the same scale!
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("Running KMeans Clustering...")
    # Let's try to find 3 behavioral archetypes (clusters)
    # TODO: Try changing n_clusters to 5 (which is what AHRID actually uses)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    
    # Fit the model and assign a cluster label to each user
    features_df['cluster_label'] = kmeans.fit_predict(X_scaled)
    
    print("\nCluster centers (the 'average' user in each cluster):")
    # We inverse transform to see the real numbers, not the scaled numbers
    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    
    centers_df = pd.DataFrame(centers, columns=X.columns)
    centers_df.index.name = 'Cluster'
    print(centers_df)
    
    # TODO: Look at the printed centers. Can you name the clusters?
    # e.g., "Fast and Wrong", "Slow and Accurate", etc.
    
    return kmeans, scaler, features_df

if __name__ == "__main__":
    raw_df = load_raw_data()
    features_df = engineer_features(raw_df)
    
    # Creating some varied dummy data so clustering actually works
    import numpy as np
    np.random.seed(42)
    fake_users = pd.DataFrame({
        'user_id': [f"u{i}" for i in range(50)],
        'total_attempts': np.random.randint(10, 50, 50),
        'overall_accuracy': np.random.uniform(0.2, 1.0, 50),
        'avg_response_time': np.random.randint(1000, 8000, 50)
    })
    
    model, scaler, clustered_df = cluster_users(fake_users)
    print("\nUsers with their assigned clusters:")
    print(clustered_df.head(10))
