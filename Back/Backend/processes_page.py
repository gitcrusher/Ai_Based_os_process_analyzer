# Import required libraries
from flask import Flask, render_template_string
import psutil
import traceback

# Initialize Flask application
app = Flask(__name__)

@app.route('/')
def live_processes():
    """
    Main route that displays real-time system processes.
    Returns a webpage showing process information including:
    - Process ID (PID)
    - Process Name
    - CPU Usage with visual bar
    - Memory Usage with visual bar
    - Process Status
    """
    try:
        # List to store process information
        processes = []
        
        # Collect information for each running process
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes that can't be accessed, no longer exist, or are zombies
                continue
            except Exception as e:
                # Log other errors but continue processing
                print(f"Error processing process: {e}")
                continue

        # Sort processes by CPU usage (highest first)
        # Add error handling for sorting
        try:
            processes = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)
        except Exception as e:
            # If sorting fails, return unsorted list
            print(f"Error sorting processes: {e}")

        # HTML template with embedded CSS for styling
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="5">  <!-- Auto-refresh every 5 seconds -->
            <title>System Processes</title>
            <style>
                /* Dark theme styling */
                body {
                    background-color: #0a0a0a;
                    color: #ffffff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                }

                /* Header styling */
                header {
                    background-color: #1a1a1a;
                    padding: 20px;
                    text-align: center;
                    color: #ff3333;
                    font-size: 30px;
                    font-weight: bold;
                    border-bottom: 2px solid #ff0000;
                    box-shadow: 0 0 15px #ff0000;
                }

                /* Container styling */
                .container {
                    padding: 20px;
                }

                /* Table styling */
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    background-color: #111;
                    border: 2px solid #ff0000;
                    box-shadow: 0 0 10px #ff0000;
                }

                /* Table cell styling */
                th, td {
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #333;
                    color: #ffffff;
                }

                /* Table header styling */
                th {
                    background-color: #1f1f1f;
                    color: #ff6666;
                    border-bottom: 2px solid #ff0000;
                }

                /* Table row hover effect */
                tr:hover {
                    background-color: #1b1b1b;
                }

                /* Progress bar container styling */
                .bar-container {
                    background-color: #222;
                    border-radius: 6px;
                    overflow: hidden;
                    height: 16px;
                    border: 1px solid #ff0000;
                    box-shadow: 0 0 5px #ff0000;
                }

                /* CPU usage bar styling */
                .cpu-bar {
                    background: linear-gradient(to right, #ff0000, #ffcc00);
                    height: 100%;
                    box-shadow: 0 0 8px #ff0000;
                }

                /* Memory usage bar styling */
                .mem-bar {
                    background: linear-gradient(to right, #00ff99, #00ccff);
                    height: 100%;
                    box-shadow: 0 0 8px #00ffcc;
                }

                /* Refresh note styling */
                .refresh-note {
                    text-align: center;
                    margin-top: 10px;
                    font-size: 13px;
                    color: #888;
                }
            </style>
        </head>
        <body>
            <header>SYSTEM PROCESSES</header>
            <div class="container">
                <div class="refresh-note">Auto-refreshes every 5 seconds</div>
                <table>
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>CPU Usage</th>
                        <th>Memory Usage</th>
                        <th>Status</th>
                    </tr>
                    {% for proc in processes %}
                    <tr>
                        <td>{{ proc.pid }}</td>
                        <td>{{ proc.name }}</td>
                        <td>
                            <div class="bar-container">
                                <div class="cpu-bar" style="width: {{ proc.cpu_percent }}%;"></div>
                            </div>
                            {{ proc.cpu_percent }}%
                        </td>
                        <td>
                            <div class="bar-container">
                                <div class="mem-bar" style="width: {{ proc.memory_percent }}%;"></div>
                            </div>
                            {{ "%.2f"|format(proc.memory_percent) }}%
                        </td>
                        <td>{{ proc.status }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
        """

        return render_template_string(html, processes=processes)

    except Exception as e:
        # If something goes wrong, show an error page with a back button
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Error</title>
            <style>
                body {
                    background-color: #0a0a0a;
                    color: #ffffff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }
                .error-container {
                    text-align: center;
                    padding: 20px;
                    background: rgba(255, 0, 0, 0.1);
                    border: 2px solid #ff0000;
                    border-radius: 10px;
                    box-shadow: 0 0 15px rgba(255, 0, 0, 0.3);
                }
                .back-button {
                    display: inline-block;
                    margin-top: 20px;
                    text-decoration: none;
                    color: #ffffff;
                    background: linear-gradient(90deg, #ff0000, #8b0000);
                    padding: 10px 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
                    transition: all 0.3s ease;
                }
                .back-button:hover {
                    transform: scale(1.05);
                    box-shadow: 0 0 20px rgba(255, 0, 0, 1);
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Temporarily Unavailable</h1>
                <p>The process list is currently unavailable. Please try again in a few moments.</p>
                <a href="/" class="back-button">← Back to Dashboard</a>
            </div>
        </body>
        </html>
        """
        print(f"Error in live_processes: {e}")
        print(traceback.format_exc())  # This will print the full error traceback
        return render_template_string(error_html)

# Run the Flask application if script is executed directly
if __name__ == '__main__':
    app.run(port=5001, debug=True)
