import sqlite3
import pandas as pd

# 1. Read processed churn dataset output from ML model
try:
    df = pd.read_csv('processed_churn_risk.csv')
    print(" Found 'processed_churn_risk.csv'. Loading data...")
except FileNotFoundError:
    print(" 'processed_churn_risk.csv' not found. Make sure churn_model.py ran successfully first!")
    exit()

# 2. Connect to SQLite (Automatically creates 'churn_analysis.db' in your workspace)
conn = sqlite3.connect('churn_analysis.db')

# 3. Write DataFrame into SQLite table
df.to_sql('telco_churn', conn, if_exists='replace', index=False)
print(" Success: 'churn_analysis.db' file created in workspace!")

# 4. Run Cohort Analysis SQL Query
sql_query = """
SELECT 
    Contract,
    CASE 
        WHEN tenure <= 12 THEN '0-1 Year'
        WHEN tenure <= 24 THEN '1-2 Years'
        WHEN tenure <= 48 THEN '2-4 Years'
        ELSE '4+ Years'
    END AS tenure_cohort,
    COUNT(customerID) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(customerID), 
        2
    ) AS churn_rate_percentage
FROM telco_churn
GROUP BY Contract, tenure_cohort
ORDER BY Contract, tenure_cohort;
"""

cohort_results = pd.read_sql_query(sql_query, conn)
print("\n--- COHORT ANALYSIS PREVIEW ---")
print(cohort_results)

conn.close()