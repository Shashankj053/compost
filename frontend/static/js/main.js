// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Authentication check
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// API Headers with authentication
function getHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'login.html';
}

// Form validation
function validateForm(formData) {
    const required = ['bin_id', 'cn_ratio', 'moisture_level', 'aeration_frequency', 
                     'daily_temperature', 'odor_level', 'decomposition_days', 
                     'final_n', 'final_p', 'final_k'];
    
    for (let field of required) {
        if (!formData[field] || formData[field] === '') {
            return `${field.replace('_', ' ')} is required`;
        }
    }
    
    // Validate ranges
    if (formData.moisture_level < 0 || formData.moisture_level > 100) {
        return 'Moisture level must be between 0-100%';
    }
    
    if (formData.odor_level < 1 || formData.odor_level > 5) {
        return 'Odor level must be between 1-5';
    }
    
    if (formData.decomposition_days < 1) {
        return 'Decomposition days must be at least 1';
    }
    
    return null;
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication for protected pages
    if (window.location.pathname !== '/login.html' && window.location.pathname !== '/login') {
        if (!checkAuth()) {
            return;
        }
    }
    
    // Handle experiment form submission
    const experimentForm = document.getElementById('experimentForm');
    if (experimentForm) {
        experimentForm.addEventListener('submit', handleExperimentSubmit);
    }
    
    // Display username if available
    const username = localStorage.getItem('username');
    if (username) {
        // Could display username in nav or elsewhere
        console.log('Logged in as:', username);
    }
});

// Handle experiment form submission
async function handleExperimentSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {};
    
    // Convert FormData to regular object
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Validate form
    const validationError = validateForm(data);
    if (validationError) {
        showToast(validationError, 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/experiments`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Experiment added successfully!', 'success');
            form.reset();
            
            // Redirect to dashboard after 2 seconds
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 2000);
        } else {
            showToast(result.error || 'Failed to add experiment', 'error');
        }
    } catch (error) {
        console.error('Error adding experiment:', error);
        showToast('Connection error. Please try again.', 'error');
    }
}

// Utility functions for data formatting
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Export function for data download
async function exportData() {
    try {
        const response = await fetch
