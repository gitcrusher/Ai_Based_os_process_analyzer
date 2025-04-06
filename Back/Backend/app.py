from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import psutil
import pandas as pd
import joblib

# Initialize Flask app with custom static and template folders
app = Flask(__name__,
            static_folder="../Frontend/static",  # Path to static files
            template_folder="../Frontend/templates")  # Path to templates
CORS(app)  # Enable CORS for all routes

# Load the trained model and scaler
try:
    model = joblib.load("models/anomaly_detection_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    print("Model and scaler loaded successfully.")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    exit()


# Load and preprocess the dataset
def load_and_preprocess_data(filepath):
    try:
        df = pd.read_csv(
            filepath,
            header=None,
            names=["timestamp", "process_name", "cpu_usage", "memory_usage", "disk_usage", "process_state", "label"]
        )
        # Convert numeric columns to appropriate types
        df["cpu_usage"] = pd.to_numeric(df["cpu_usage"], errors="coerce")
        df["memory_usage"] = pd.to_numeric(df["memory_usage"], errors="coerce")
        df["disk_usage"] = pd.to_numeric(df["disk_usage"], errors="coerce")
        df.dropna(inplace=True)  # Drop rows with missing values
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None


# Load dataset
dataset = load_and_preprocess_data("data/Pasted_Text_1743373145059.txt")


# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')


# API endpoint to fetch real-time system metrics
@app.route('/api/system-metrics', methods=['GET'])
def get_system_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        scaled_data = scaler.transform([[cpu_usage, memory_usage]])
        prediction = model.predict(scaled_data)
        status = "Normal" if prediction == 1 else "Anomaly"

        return jsonify({
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "status": status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to fetch anomalies
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        scaled_data = scaler.transform([[cpu_usage, memory_usage]])
        prediction = model.predict(scaled_data)
        status = "Anomaly" if prediction == -1 else "Normal"

        suggestions = []
        if status == "Anomaly":
            if cpu_usage > 90:
                suggestions.append("High CPU usage detected. Close unnecessary applications.")
            if memory_usage > 90:
                suggestions.append("High memory usage detected. Free up memory by closing unused apps.")

            # Check for zombie or orphan processes
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                if proc.info['status'] in ['zombie', 'orphan']:
                    suggestions.append(
                        f"Terminate zombie/orphan process: {proc.info['name']} (PID: {proc.info['pid']})")

        return jsonify({
            "status": status,
            "suggestions": suggestions
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to fetch process-level anomalies
@app.route('/api/process-anomalies', methods=['GET'])
def get_process_anomalies():
    try:
        if dataset is None:
            return jsonify({"error": "Dataset not loaded"}), 500

        # Filter anomalies from the dataset
        anomalies = dataset[dataset["label"] == -1].to_dict(orient="records")

        return jsonify({
            "status": "Anomaly",
            "anomalies": anomalies
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)