document.addEventListener("DOMContentLoaded", () => {
    // DOM elements
    const metricsElements = {
        cpu: document.querySelector("[data-type='cpu'] .meter-progress"),
        memory: document.querySelector("[data-type='memory'] .meter-progress"),
        disk: document.querySelector("[data-type='disk'] .meter-progress"),
        statusIndicator: document.getElementById("status"),
        cpuValue: document.querySelector("[data-type='cpu'] .meter-value"),
        memoryValue: document.querySelector("[data-type='memory'] .meter-value"),
        diskValue: document.querySelector("[data-type='disk'] .meter-value"),
        anomalyStatus: document.getElementById("anomaly-status"),
        anomaliesList: document.getElementById("anomalies-list"),
        suggestionsList: document.getElementById("suggestions-list"),
        problematicProcessesList: document.getElementById("problematic-processes-list") // New element for problematic processes
    };

    // Configuration
    const fetchInterval = 1000; // 10-second updates

    // Navigation function
    window.showSection = function (sectionId) {
        const sections = document.querySelectorAll(".section");
        sections.forEach(section => {
            section.style.display = "none";
        });
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = "block";
        }
        const links = document.querySelectorAll(".sidebar a");
        links.forEach(link => {
            link.classList.remove("active");
        });
        const activeLink = document.querySelector(`.sidebar a[onclick="showSection('${sectionId}')"]`);
        if (activeLink) {
            activeLink.classList.add("active");
        }
    };

    // Fetch system metrics from backend
    async function fetchSystemMetrics() {
        try {
            const response = await fetch("/api/system-metrics"); // Replace with your backend endpoint
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            updateMetrics(data);
        } catch (error) {
            handleFetchError(error.message, "metrics");
        } finally {
            setTimeout(fetchSystemMetrics, fetchInterval); // Delay reloading by 10 seconds
        }
    }

    // Fetch anomalies and problematic processes from backend
    async function fetchAnomalies() {
    try {
        const response = await fetch("/api/anomalies"); // Replace with your backend endpoint
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        updateAnomalies(data);
    } catch (error) {
        handleFetchError(error.message, "anomalies");
    } finally {
        setTimeout(fetchAnomalies, fetchInterval); // Delay reloading by 10 seconds
    }
}

    // Update metrics
    function updateMetrics(data) {
        updateMeter("cpu", data.cpu_usage, metricsElements.cpu, metricsElements.cpuValue, data.status);
        updateMeter("memory", data.memory_usage, metricsElements.memory, metricsElements.memoryValue, "Normal");
        updateMeter("disk", data.disk_usage, metricsElements.disk, metricsElements.diskValue, "Normal");
        metricsElements.statusIndicator.textContent = data.status || "N/A";
        metricsElements.statusIndicator.className = `status-indicator ${data.status?.toLowerCase() || "normal"}`;
        updateSuggestions(data.status);
    }

    // Generic meter updater
    function updateMeter(type, value, progressCircle, textElement, status) {
        const circumference = 2 * Math.PI * 45;
        const offset = circumference - ((value || 0) / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
        textElement.textContent = `${value || 0}%`;
        if (type === "cpu" && status === "Anomaly") {
            progressCircle.style.stroke = "#ff0000"; // Red for anomalies
        } else {
            progressCircle.style.stroke = "#00ff00"; // Green for normal
        }
    }

    // Update anomalies
    function updateAnomalies(data) {
        metricsElements.anomalyStatus.textContent = data.status || "N/A";
        metricsElements.anomaliesList.innerHTML = "";
        if (data.status === "Anomaly" && Array.isArray(data.suggestions)) {
            data.suggestions.forEach(suggestion => {
                const li = document.createElement("li");
                li.textContent = suggestion;
                metricsElements.anomaliesList.appendChild(li);
            });
        } else {
            metricsElements.anomaliesList.innerHTML = "<li>No anomalies detected.</li>";
        }
    }

    // Update problematic processes
    function updateProblematicProcesses(processes) {
        metricsElements.problematicProcessesList.innerHTML = ""; // Clear previous entries
        if (Array.isArray(processes) && processes.length > 0) {
            processes.forEach(process => {
                const li = document.createElement("li");
                li.textContent = process;
                metricsElements.problematicProcessesList.appendChild(li);
            });
        } else {
            metricsElements.problematicProcessesList.innerHTML = "<li>No problematic processes detected.</li>";
        }
    }

    // Update suggestions based on status
    function updateSuggestions(status) {
        const suggestions = metricsElements.suggestionsList;
        suggestions.innerHTML = "";
        if (status === "Anomaly") {
            suggestions.innerHTML = `
                <li>High resource usage detected. Close unnecessary applications.</li>
                <li>Check for background processes.</li>
                <li>Monitor CPU temperature to prevent overheating.</li>
            `;
        } else {
            suggestions.innerHTML = "<li>System is operating normally.</li>";
        }
    }

    // Handle fetch errors
    function handleFetchError(message, section) {
        if (section === "metrics") {
            metricsElements.cpu.style.strokeDashoffset = 283;
            metricsElements.cpuValue.textContent = "Error";
            metricsElements.memory.style.strokeDashoffset = 283;
            metricsElements.memoryValue.textContent = "Error";
            metricsElements.disk.style.strokeDashoffset = 283;
            metricsElements.diskValue.textContent = "Error";
            metricsElements.statusIndicator.textContent = "Connection Failed";
        } else if (section === "anomalies") {
            metricsElements.anomalyStatus.textContent = "Error";
            metricsElements.anomaliesList.innerHTML = "<li>Connection failed</li>";
            metricsElements.problematicProcessesList.innerHTML = "<li>Connection failed</li>";
        }
        console.error(`Error fetching ${section}:`, message);
    }

    // Initialize monitoring
    function startMonitoring() {
        clearTimeout(metricsTimeout);
        clearTimeout(anomaliesTimeout);
        fetchSystemMetrics();
        fetchAnomalies();
        metricsTimeout = setTimeout(fetchSystemMetrics, fetchInterval);
        anomaliesTimeout = setTimeout(fetchAnomalies, fetchInterval);
    }

    let metricsTimeout, anomaliesTimeout;
    startMonitoring();

    window.addEventListener("beforeunload", () => {
        clearTimeout(metricsTimeout);
        clearTimeout(anomaliesTimeout);
    });
});