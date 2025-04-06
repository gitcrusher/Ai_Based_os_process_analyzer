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
        suggestionsList: document.getElementById("suggestions-list")
    };

    // Configuration
    const fetchInterval = 5000; // 5-second updates

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

    // Fetch system metrics (mocked data)
    async function fetchSystemMetrics() {
        try {
            showLoadingState("metrics");
            await new Promise(resolve => setTimeout(resolve, 500));
            const mockData = {
                cpu_usage: Math.floor(Math.random() * 100),
                memory_usage: Math.floor(Math.random() * 100),
                disk_usage: Math.floor(Math.random() * 100),
                status: Math.random() > 0.7 ? "Anomaly" : "Normal"
            };
            updateMetrics(mockData);
        } catch (error) {
            handleFetchError(error.message, "metrics");
        } finally {
            setTimeout(fetchSystemMetrics, fetchInterval);
        }
    }

    // Fetch anomalies (mocked data)
    async function fetchAnomalies() {
        try {
            showLoadingState("anomalies");
            await new Promise(resolve => setTimeout(resolve, 500));
            const mockData = {
                status: Math.random() > 0.7 ? "Anomaly" : "Normal",
                suggestions: [
                    "High resource usage detected. Close unnecessary applications.",
                    "Check for background processes.",
                    "Monitor CPU temperature to prevent overheating."
                ]
            };
            updateAnomalies(mockData);
        } catch (error) {
            handleFetchError(error.message, "anomalies");
        } finally {
            setTimeout(fetchAnomalies, fetchInterval);
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

    // Show loading state
    function showLoadingState(section) {
        if (section === "metrics") {
            metricsElements.cpu.style.strokeDashoffset = 283;
            metricsElements.cpuValue.textContent = "Loading...";
            metricsElements.memory.style.strokeDashoffset = 283;
            metricsElements.memoryValue.textContent = "Loading...";
            metricsElements.disk.style.strokeDashoffset = 283;
            metricsElements.diskValue.textContent = "Loading...";
            metricsElements.statusIndicator.textContent = "Loading...";
        } else if (section === "anomalies") {
            metricsElements.anomalyStatus.textContent = "Loading...";
            metricsElements.anomaliesList.innerHTML = "<li>Loading...</li>";
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