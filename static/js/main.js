// BESS Simulation - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('BESS Simulation loaded successfully');
    
    // Initialize tooltips and interactive elements
    initializeTooltips();
    initializeCharts();
    initializeNotifications();
});

function initializeTooltips() {
    // Tooltip functionality
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = event.target.getAttribute('data-tooltip');
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - 30) + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

function initializeCharts() {
    // Chart.js initialization will be handled by individual pages
    console.log('Charts initialized');
}

function initializeNotifications() {
    // Notification system
    console.log('Notifications initialized');
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat('de-DE').format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}
