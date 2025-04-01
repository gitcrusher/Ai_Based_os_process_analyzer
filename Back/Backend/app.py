from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import psutil
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

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    """
    Fetch anomalies detected by the model.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        scaled_data = scaler.transform([[cpu_usage, memory_usage]])
        prediction = model.predict(scaled_data)
        status = "Anomaly" if prediction == -1 else "Normal"

        # Suggestions based on anomalies
        suggestions = []
        if status == "Anomaly":
            if cpu_usage > 90:
                suggestions.append("High CPU usage detected. Close unnecessary applications.")
            if memory_usage > 90:
                suggestions.append("High memory usage detected. Free up memory by closing unused apps.")
            suggestions.append("Check for zombie or orphan processes and terminate them.")

        return jsonify({
            "status": status,
            "suggestions": suggestions
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)