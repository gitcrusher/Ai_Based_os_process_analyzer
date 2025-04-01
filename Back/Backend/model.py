import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# Step 1: Load the Dataset
def load_data(file_path):
    """
    Load dataset from a CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        print("Dataset loaded successfully.")
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None


# Step 2: Preprocess the Data
def preprocess_data(df):
    """
    Preprocess the dataset by handling missing values, normalizing features, and encoding labels.
    """
    print("Preprocessing data...")

    # Drop non-numeric columns that are irrelevant for anomaly detection
    non_numeric_columns = df.select_dtypes(exclude=['number']).columns
    print(f"Dropping non-numeric columns: {list(non_numeric_columns)}")
    df.drop(columns=non_numeric_columns, inplace=True)

    # Convert relevant columns to numeric
    for col in ['CPU_Usage', 'Memory_Usage']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, coerce errors to NaN

    # Handle missing values
    print("Handling missing values...")
    df.fillna(df.mean(numeric_only=True), inplace=True)  # Use mean for numeric columns only

    # Normalize features
    scaler = MinMaxScaler()
    numeric_columns = df.select_dtypes(include=['number']).columns
    df[numeric_columns] = scaler.fit_transform(df[numeric_columns])

    # Create synthetic process states (if applicable)
    if 'process_state' in df.columns:
        df['process_state'] = df['process_state'].apply(lambda x: 1 if x == 'Running' else 0)

    # Create a synthetic label column for anomalies
    print("Creating synthetic label column...")
    df['label'] = df.apply(
        lambda row: -1 if (
            row['CPU_Usage'] > 0.9 or
            row['Memory_Usage'] > 0.9 or
            'process_state_Zombie' in row or
            'process_state_Orphan' in row
        ) else 1,
        axis=1
    )

    print("Data preprocessing completed.")
    return df, scaler


# Step 3: Split the Data into Training and Testing Sets
def split_data(df):
    """
    Split the dataset into training and testing sets.
    """
    X = df.drop(columns=['label'])
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    print("Data split into training and testing sets.")
    return X_train, X_test, y_train, y_test


# Step 4: Train the Model
def train_model(X_train):
    """
    Train an anomaly detection model using Isolation Forest.
    """
    print("Training model...")
    model = IsolationForest(contamination=0.1, random_state=42)  # Adjust contamination for anomalies
    model.fit(X_train)
    print("Model training completed.")
    return model


# Step 5: Evaluate the Model
def evaluate_model(model, X_test, y_test):
    """
    Evaluate the model's performance using metrics like precision, recall, and F1-score.
    """
    y_pred = model.predict(X_test)
    y_pred = [1 if x == 1 else -1 for x in y_pred]  # Convert predictions to binary labels

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))


# Step 6: Save the Model
def save_model(model, scaler, model_path, scaler_path):
    """
    Save the trained model and scaler for future use.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Save the model and scaler
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Model saved to {model_path} and scaler saved to {scaler_path}.")


# Step 7: Inject Synthetic Anomalies
def inject_anomalies(df):
    """
    Inject synthetic anomalies into the dataset for testing purposes.
    """
    print("Injecting synthetic anomalies...")

    # High CPU usage anomalies
    anomaly_indices = np.random.choice(df.index, size=50, replace=False)  # Simulate 50 anomalies
    df.loc[anomaly_indices, 'CPU_Usage'] = np.random.uniform(0.9, 1.5, size=len(anomaly_indices))  # Simulate spikes

    # High memory usage anomalies
    memory_anomaly_indices = np.random.choice(df.index, size=30, replace=False)
    df.loc[memory_anomaly_indices, 'Memory_Usage'] = np.random.uniform(0.9, 1.5, size=len(memory_anomaly_indices))

    # Zombie and Orphan process anomalies
    zombie_indices = np.random.choice(df.index, size=20, replace=False)
    df.loc[zombie_indices, 'process_state_Zombie'] = 1
    df.loc[zombie_indices, 'process_state_Running'] = 0

    orphan_indices = np.random.choice(df.index, size=20, replace=False)
    df.loc[orphan_indices, 'process_state_Orphan'] = 1
    df.loc[orphan_indices, 'process_state_Running'] = 0

    print("Synthetic anomalies injected.")
    return df


# Main Function
if __name__ == "__main__":
    # Define file paths
    dataset_path = "data/os_processes_data.csv"  # Path to your dataset
    model_path = "models/anomaly_detection_model.pkl"
    scaler_path = "models/scaler.pkl"

    # Step 1: Load the dataset
    df = load_data(dataset_path)
    if df is None:
        exit()

    # Step 2: Preprocess the data
    df, scaler = preprocess_data(df)

    # Step 3: Inject synthetic anomalies
    df = inject_anomalies(df)

    # Step 4: Split the data
    X_train, X_test, y_train, y_test = split_data(df)

    # Step 5: Train the model
    model = train_model(X_train)

    # Step 6: Evaluate the model
    evaluate_model(model, X_test, y_test)

    # Step 7: Save the model and scaler
    save_model(model, scaler, model_path, scaler_path)