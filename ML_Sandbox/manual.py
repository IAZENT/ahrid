import pandas as pd
import sqlite3
import os

def load_raw_data():
    # The database is located in the backend folder
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "ahrip_dev.sqlite3"))
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return pd.DataFrame()
        
    print(f"Connecting to database at {db_path}...")
    
    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Write a SQL query to fetch the attempts
    # We select only the columns that matter for Feature Engineering
    query = """
        SELECT * FROM attempts
    """
    
    # Use pandas to read the SQL query directly into a DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Let's also query the scenario count to prove this is the real database
    scenario_count = pd.read_sql_query("SELECT COUNT(*) as count FROM scenarios", conn).iloc[0]['count']
    
    # And let's query the users count!
    user_count = pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
    
    # Close the connection
    conn.close()
    
    print(f"Successfully connected to the real database!")
    print(f"- Found {user_count} users")
    print(f"- Found {scenario_count} scenarios")
    print(f"- Found {len(df)} user attempts")
    
    return df

if __name__ == "__main__":
    df = load_raw_data()
    if not df.empty:
        print("\n--- First 5 Rows of Database Data ---")
        print(df.head())
        print("\n--- Data Summary ---")
        print(df.info())