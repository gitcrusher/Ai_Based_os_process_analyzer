document.addEventListener("DOMContentLoaded", () => {
    const cpuUsageElement = document.getElementById("cpu-usage");
    const memoryUsageElement = document.getElementById("memory-usage");
    const diskUsageElement = document.getElementById("disk-usage");
    const statusElement = document.getElementById("status");

    async function fetchSystemMetrics() {
        try {
            const response = await fetch("/api/system-metrics");
            if (!response.ok) {
                throw new Error("Failed to fetch system metrics");
            }
            const data = await response.json();
            cpuUsageElement.textContent = `${data.cpu_usage}%`;
            memoryUsageElement.textContent = `${data.memory_usage}%`;
            diskUsageElement.textContent = `${data.disk_usage}%`;
            statusElement.textContent = data.status;

            // Add suggestions based on status
            const suggestionsList = document.getElementById("suggestions-list");
            suggestionsList.innerHTML = ""; // Clear previous suggestions
            if (data.status === "Anomaly") {
                suggestionsList.innerHTML += "<li>High resource usage detected. Close unnecessary applications.</li>";
            } else {
                suggestionsList.innerHTML += "<li>System is operating normally. No immediate action required.</li>";
            }
        } catch (error) {
            console.error(error);
            cpuUsageElement.textContent = "Error";
            memoryUsageElement.textContent = "Error";
            diskUsageElement.textContent = "Error";
            statusElement.textContent = "Error";
        }
    }

    // Fetch metrics every 5 seconds
    setInterval(fetchSystemMetrics, 5000);

    // Initial fetch
    fetchSystemMetrics();

    // Sidebar Navigation
    window.showSection = function (sectionId) {
        // Hide all sections
        document.querySelectorAll(".section").forEach(section => {
            section.style.display = "none";


        // Show the selected section
        document.getElementById(sectionId).style.display = "block";

        // Update active link in sidebar
        document.querySelectorAll(".sidebar ul li a").forEach(link => {
            link.classList.remove("active");
        });
        document.querySelector(`.sidebar ul li a[onclick="showSection('${sectionId}')"]`).classList.add("active");
    };
});