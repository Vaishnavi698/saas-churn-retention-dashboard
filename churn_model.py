import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression

# 1. READ RAW DATASET
df = pd.read_csv('WA_Fn-Simulated_-Telco-Customer-Churn.csv')

# Clean TotalCharges column & handle missing values cleanly
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].astype(str).str.strip(), errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())

# Fill any remaining numerical NaNs
df['MonthlyCharges'] = df['MonthlyCharges'].fillna(df['MonthlyCharges'].median())
df['tenure'] = df['tenure'].fillna(df['tenure'].median())

# 2. DEFINE FEATURES AND TARGET
X = df.drop(columns=['customerID', 'Churn'])
y = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)

num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
cat_cols = [c for c in X.columns if c not in num_cols]

# 3. PREPROCESSING PIPELINE
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), cat_cols)
    ]
)

# 4. TRAIN LOGISTIC REGRESSION MODEL
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

X_train_prep = preprocessor.fit_transform(X_train)
model = LogisticRegression(max_iter=1000)
model.fit(X_train_prep, y_train)

# 5. PREDICT CHURN PROBABILITIES FOR ALL CUSTOMERS
X_all_prep = preprocessor.transform(X)
df['Churn_Probability'] = model.predict_proba(X_all_prep)[:, 1]

# Categorize risk levels into actionable segments
df['Risk_Segment'] = pd.cut(
    df['Churn_Probability'], 
    bins=[0, 0.3, 0.7, 1.0], 
    labels=['Low Risk', 'Medium Risk', 'High Risk'],
    include_lowest=True
)

# Save output to CSV
df.to_csv('processed_churn_risk.csv', index=False)
print(" Success: Generated 'processed_churn_risk.csv'!")