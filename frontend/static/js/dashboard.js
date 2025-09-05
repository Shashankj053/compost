// Dashboard specific JavaScript
let experimentsData = [];
let analyticsData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) {
        return;
    }
    
    loadDashboardData();
});

// Load all dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadExperiments(),
            loadAnalytics()
        ]);
        
        updateStatistics();
        createCharts();
        populateDataTable();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error loading dashboard data', 'error');
    }
}

// Load experiments data
async function loadExperiments() {
    try {
        const response = await fetch(`${API_BASE_URL}/experiments`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            experimentsData = await response.json();
        } else {
            const result = await response.json();
            throw new Error(result.error || 'Failed to load experiments');
        }
    } catch (error) {
        console.error('Error loading experiments:', error);
        showToast('Error loading experiments data', 'error');
        experimentsData = [];
    }
}

// Load analytics data
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            analyticsData = await response.json();
        } else {
            const result = await response.json();
            // Don't show error if no experiments exist yet
            if (result.error !== 'No experiments found') {
                throw new Error(result.error || 'Failed to load analytics');
            }
            analyticsData = {};
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        if (!error.message.includes('No experiments found')) {
            showToast('Error loading analytics data', 'error');
        }
        analyticsData = {};
    }
}

// Update statistics cards
function updateStatistics() {
    const totalElement = document.getElementById('totalExperiments');
    const avgEfficiencyElement = document.getElementById('avgEfficiency');
    const avgDaysElement = document.getElementById('avgDays');
    const bestBinElement = document.getElementById('bestBin');
    
    if (analyticsData.summary_stats) {
        const stats = analyticsData.summary_stats;
        
        if (totalElement) totalElement.textContent = stats.total_experiments || 0;
        if (avgEfficiencyElement) avgEfficiencyElement.textContent = stats.avg_efficiency_score || '0';
        if (avgDaysElement) avgDaysElement.textContent = stats.avg_decomposition_days || '0';
        if (bestBinElement) bestBinElement.textContent = stats.best_bin || '-';
    } else {
        // No data available
        if (totalElement) totalElement.textContent = '0';
        if (avgEfficiencyElement) avgEfficiencyElement.textContent = '0';
        if (avgDaysElement) avgDaysElement.textContent = '0';
        if (bestBinElement) bestBinElement.textContent = '-';
    }
}

// Create all charts
function createCharts() {
    if (!analyticsData.chart_data) {
        // Show "No data" message in chart containers
        const chartContainers = ['efficiencyChart', 'tempChart', 'npkChart', 'paramChart'];
        chartContainers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = '<div style="text-align: center; padding: 50px; color: #666;">No data available. Add some experiments first!</div>';
            }
        });
        return;
    }
    
    createEfficiencyChart();
    createTemperatureChart();
    createNPKChart();
    createParameterChart();
}

// Efficiency scores by bin chart
function createEfficiencyChart() {
    const data = analyticsData.chart_data?.efficiency_by_bin || {};
    
    const trace = {
        x: Object.keys(data),
        y: Object.values(data),
        type: 'bar',
        marker: {
            color: 'rgba(45, 90, 39, 0.8)',
            line: {
                color: 'rgba(45, 90, 39, 1.0)',
                width: 2
            }
        }
    };
    
    const layout = {
        title: false,
        xaxis: { title: 'Bin ID' },
        yaxis: { title: 'Efficiency Score' },
        margin: { t: 30, r: 30, b: 60, l: 60 },
        font: { family: 'Segoe UI, sans-serif' }
    };
    
    Plotly.newPlot('efficiencyChart', [trace], layout, {responsive: true});
}

// Temperature vs decomposition time scatter plot
function createTemperatureChart() {
    const data = analyticsData.chart_data?.decomposition_vs_temperature || [];
    
    const trace = {
        x: data.map(d => d.daily_temperature),
        y: data.map(d => d.decomposition_days),
        mode: 'markers',
        type: 'scatter',
        marker: {
            color: 'rgba(45, 90, 39, 0.8)',
            size: 10,
            line: {
                color: 'rgba(45, 90, 39, 1.0)',
                width: 2
            }
        }
    };
    
    const layout = {
        title: false,
        xaxis: { title: 'Temperature (°C)' },
        yaxis: { title: 'Decomposition Days' },
        margin: { t: 30, r: 30, b: 60, l: 60 },
        font: { family: 'Segoe UI, sans-serif' }
    };
    
    Plotly.newPlot('tempChart', [trace], layout, {responsive: true});
}

// NPK values chart
function createNPKChart() {
    const data = analyticsData.chart_data?.npk_values || [];
    
    const binIds = data.map(d => d.bin_id);
    const nValues = data.map(d => d.final_n);
    const pValues = data.map(d => d.final_p);
    const kValues = data.map(d => d.final_k);
    
    const traces = [
        {
            x: binIds,
            y: nValues,
            name: 'Nitrogen (N)',
            type: 'bar',
            marker: { color: 'rgba(255, 99, 132, 0.8)' }
        },
        {
            x: binIds,
            y: pValues,
            name: 'Phosphorus (P)',
            type: 'bar',
            marker: { color: 'rgba(54, 162, 235, 0.8)' }
        },
        {
            x: binIds,
            y: kValues,
            name: 'Potassium (K)',
            type: 'bar',
            marker: { color: 'rgba(255, 205, 86, 0.8)' }
        }
    ];
    
    const layout = {
        title: false,
        xaxis: { title: 'Bin ID' },
        yaxis: { title: 'NPK Values' },
        barmode: 'group',
        margin: { t: 30, r: 30, b: 60, l: 60 },
        font: { family: 'Segoe UI, sans-serif' }
    };
    
    Plotly.newPlot('npkChart', traces, layout, {responsive: true});
}

// Parameter distribution box plot
function createParameterChart() {
    const data = analyticsData.chart_data?.parameter_distribution || {};
    
    const traces = [
        {
            y: data.cn_ratio || [],
            name: 'C/N Ratio',
            type: 'box',
            marker: { color: 'rgba(45, 90, 39, 0.8)' }
        },
        {
            y: data.moisture_level || [],
            name: 'Moisture %',
            type: 'box',
            marker: { color: 'rgba(54, 162, 235, 0.8)' }
        },
        {
            y: data.aeration_frequency || [],
            name: 'Aeration/Week',
            type: 'box',
            marker: { color: 'rgba(255, 205, 86, 0.8)' }
        },
        {
            y: data.daily_temperature || [],
            name: 'Temperature °C',
            type: 'box',
            marker: { color: 'rgba(255, 99, 132, 0.8)' }
        }
    ];
    
    const layout = {
        title: false,
        yaxis: { title: 'Parameter Values' },
        margin: { t: 30, r: 30, b: 60, l: 60 },
        font: { family: 'Segoe UI, sans-serif' }
    };
    
    Plotly.newPlot('paramChart', traces, layout, {responsive: true});
}

// Populate data table
function populateDataTable() {
    const tableBody = document.querySelector('#experimentsTable tbody');
    
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (experimentsData.length === 0) {
        const row = tableBody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 10;
        cell.textContent = 'No experiments found. Add some data first!';
        cell.style.textAlign = 'center';
        cell.style.padding = '20px';
        cell.style.color = '#666';
        return;
    }
    
    experimentsData.forEach(experiment => {
        const row = tableBody.insertRow();
        
        // Add cells
        row.insertCell().textContent = experiment.bin_id;
        row.insertCell().textContent = formatNumber(experiment.cn_ratio, 1);
        row.insertCell().textContent = formatNumber(experiment.moisture_level, 1) + '%';
        row.insertCell().textContent = formatNumber(experiment.daily_temperature, 1) + '°C';
        row.insertCell().textContent = experiment.aeration_frequency;
        row.insertCell().textContent = experiment.odor_level;
        row.insertCell().textContent = experiment.decomposition_days;
        row.insertCell().textContent = `${formatNumber(experiment.final_n, 1)}-${formatNumber(experiment.final_p, 1)}-${formatNumber(experiment.final_k, 1)}`;
        row.insertCell().textContent = formatNumber(experiment.efficiency_score, 1);
        
        // Actions cell with delete button
        const actionsCell = row.insertCell();
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.onclick = () => deleteExperiment(experiment.id);
        actionsCell.appendChild(deleteBtn);
    });
}

// Delete experiment
async function deleteExperiment(experimentId) {
    if (!confirm('Are you sure you want to delete this experiment?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/experiments/${experimentId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            showToast('Experiment deleted successfully!', 'success');
            loadDashboardData(); // Reload data
        } else {
            const result = await response.json();
            showToast(result.error || 'Failed to delete experiment', 'error');
        }
    } catch (error) {
        console.error('Error deleting experiment:', error);
        showToast('Delete failed. Please try again.', 'error');
    }
}

// Show best practices modal
async function showBestPractices() {
    try {
        const response = await fetch(`${API_BASE_URL}/best-practices`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            displayBestPractices(data);
        } else {
            const result = await response.json();
            showToast(result.error || 'Failed to load best practices', 'error');
        }
    } catch (error) {
        console.error('Error loading best practices:', error);
        showToast('Failed to load best practices', 'error');
    }
}

// Display best practices in modal
function displayBestPractices(data) {
    const modal = document.getElementById('bestPracticesModal');
    const content = document.getElementById('bestPracticesContent');
    
    if (!modal || !content) return;
    
    content.innerHTML = `
        <div class="best-practices-content">
            <h3><i class="fas fa-trophy"></i> Optimal Configuration</h3>
            <div class="optimal-config">
                <div class="config-item">
                    <strong>C/N Ratio:</strong> ${data.optimal_cn_ratio}
                </div>
                <div class="config-item">
                    <strong>Moisture Level:</strong> ${data.optimal_moisture}%
                </div>
                <div class="config-item">
                    <strong>Aeration Frequency:</strong> ${data.optimal_aeration} times/week
                </div>
                <div class="config-item">
                    <strong>Temperature:</strong> ${data.optimal_temperature}°C
                </div>
            </div>
            
            <h3><i class="fas fa-medal"></i> Top Performing Bins</h3>
            <div class="top-bins">
                ${data.top_bins.map(bin => `
                    <div class="bin-item">
                        <strong>${bin.bin_id}</strong> - Score: ${bin.efficiency_score.toFixed(1)} 
                        (${bin.decomposition_days} days)
                    </div>
                `).join('')}
            </div>
            
            <h3><i class="fas fa-lightbulb"></i> Recommendations</h3>
            <ul class="recommendations">
                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Close best practices modal
function closeBestPractices() {
    const modal = document.getElementById('bestPracticesModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('bestPracticesModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
