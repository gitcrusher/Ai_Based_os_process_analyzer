import pandas as pd
import numpy as np
import os  # Import the os module

# Step 1: Define Parameters
num_rows = 1000  # Number of rows in the dataset
anomaly_ratio = 0.9  # 90% anomalies, 10% normal data
process_names = [
    "chrome.exe", "antivirus.exe", "explorer.exe", "game.exe", "backup.exe",
    "firefox.exe", "notepad.exe", "vlc.exe", "spotify.exe", "discord.exe",
    "zoom.exe", "steam.exe", "word.exe", "excel.exe", "powerpoint.exe",
    "unknown_process.exe"
]
states = ["Running", "Sleeping", "Zombie", "Orphan", "Stopped", "Idle"]

# Step 2: Generate Normal Data
def generate_normal_data(num_rows):
    timestamps = pd.date_range(start="2023-01-01", periods=num_rows, freq="s")  # One row per second
    process_name = np.random.choice(process_names, size=num_rows)
    cpu_usage = np.random.uniform(0, 50, size=num_rows)  # Normal CPU usage (0–50%)
    memory_usage = np.random.uniform(0, 50, size=num_rows)  # Normal memory usage (0–50%)
    disk_usage = np.random.uniform(0, 50, size=num_rows)  # Normal disk usage (0–50%)
    process_state = np.random.choice(states, p=[0.7, 0.2, 0.02, 0.02, 0.03, 0.03], size=num_rows)  # Mostly "Running"
    label = np.ones(num_rows)  # Normal data labeled as 1
    return pd.DataFrame({
        "timestamp": timestamps,
        "process_name": process_name,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "process_state": process_state,
        "label": label
    })

# Step 3: Inject Frequent and Adjacent Anomalies
def inject_frequent_adjacent_anomalies(df, anomaly_ratio):
    num_anomalies = int(len(df) * anomaly_ratio)  # Calculate the number of anomalies
    anomaly_indices = np.random.choice(df.index, size=num_anomalies, replace=False)

    # Ensure anomalies are consecutive or adjacent
    anomaly_blocks = []
    block_size = max(1, len(anomaly_indices) // np.random.randint(1, len(anomaly_indices) // 50 + 1))
    for i in range(0, len(anomaly_indices), block_size):
        block = sorted(anomaly_indices[i:i + block_size])  # Create a block of consecutive indices
        anomaly_blocks.append(block)

    # Apply anomalies to each block
    for block in anomaly_blocks:
        df.loc[block, "label"] = -1  # Mark as anomaly

        # High CPU usage anomalies
        cpu_slice = block[:len(block) // 4]
        df.loc[cpu_slice, "cpu_usage"] = np.random.uniform(90, 150, size=len(cpu_slice))

        # High memory usage anomalies
        memory_slice = block[len(block) // 4:len(block) // 2]
        df.loc[memory_slice, "memory_usage"] = np.random.uniform(90, 150, size=len(memory_slice))

        # Zombie processes
        zombie_slice = block[len(block) // 2:3 * len(block) // 4]
        df.loc[zombie_slice, "process_state"] = "Zombie"

        # Orphan processes
        orphan_slice = block[3 * len(block) // 4:]
        df.loc[orphan_slice, "process_state"] = "Orphan"

        # Unknown processes
        unknown_indices = np.random.choice(block, size=min(len(block) // 10, len(block)), replace=False)
        df.loc[unknown_indices, "process_name"] = "unknown_process.exe"

        # Stopped or Idle processes
        stopped_indices = np.random.choice(block, size=min(len(block) // 10, len(block)), replace=False)
        df.loc[stopped_indices, "process_state"] = np.random.choice(["Stopped", "Idle"])

    return df

# Step 4: Generate the Dataset
normal_data = generate_normal_data(num_rows)
dataset = inject_frequent_adjacent_anomalies(normal_data, anomaly_ratio)

# Step 5: Save the Dataset to CSV
# Ensure the 'data' directory exists
os.makedirs("data", exist_ok=True)

# Save the dataset to CSV
dataset.to_csv("data/os_processes_data.csv", index=False)
print("Dataset with frequent and adjacent anomalies saved to 'data/os_processes_data.csv'.")