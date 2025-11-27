// Finance Tracker - Main JavaScript

// Utility function to format currency
function formatCurrency(amount) {
    return 'Ksh ' + parseFloat(amount).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.style.display='none';">&times;</button>
    `;
    
    const container = document.querySelector('.main-content .container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 5000);
    }
}

// Load and display summary on dashboard
async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();
        
        // Update summary cards if they exist
        const incomeCard = document.querySelector('.card-primary .amount');
        const expenseCard = document.querySelector('.card-danger .amount');
        const balanceCard = document.querySelector('.card-success .amount');
        
        if (incomeCard) {
            incomeCard.textContent = formatCurrency(data.total_income);
        }
        if (expenseCard) {
            expenseCard.textContent = formatCurrency(data.total_expense);
        }
        if (balanceCard) {
            balanceCard.textContent = formatCurrency(data.balance);
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Charts
let monthlyChartInstance = null;
let categoryChartInstance = null;

async function loadMonthlyChart() {
    try {
        const resp = await fetch('/api/monthly-summary');
        const data = await resp.json();
        if (!Array.isArray(data) || data.length === 0) return;

        const labels = data.map(d => d.month);
        const income = data.map(d => d.income);
        const expense = data.map(d => d.expense);

        const ctx = document.getElementById('monthlyChart').getContext('2d');
        if (monthlyChartInstance) monthlyChartInstance.destroy();
        monthlyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Income', data: income, backgroundColor: 'rgba(16,185,129,0.8)' },
                    { label: 'Expense', data: expense, backgroundColor: 'rgba(239,68,68,0.8)' }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    } catch (error) {
        console.error('Error loading monthly chart:', error);
    }
}

async function loadCategoryChart() {
    try {
        const resp = await fetch('/api/category-distribution');
        const data = await resp.json();
        if (!Array.isArray(data) || data.length === 0) return;

        const labels = data.map(d => d.category);
        const amounts = data.map(d => d.amount);

        const ctx = document.getElementById('categoryChart').getContext('2d');
        if (categoryChartInstance) categoryChartInstance.destroy();
        categoryChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{ data: amounts, backgroundColor: ['#3B82F6','#10B981','#F59E0B','#EF4444','#A78BFA','#06B6D4'] }]
            },
            options: { responsive: true }
        });
    } catch (error) {
        console.error('Error loading category chart:', error);
    }
}

// Load transactions dynamically
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        
        // This would be used to populate a dynamic table
        console.log('Transactions loaded:', transactions);
        return transactions;
    } catch (error) {
        console.error('Error loading transactions:', error);
        return [];
    }
}

// Load expenses by category
async function loadExpensesByCategory() {
    try {
        const response = await fetch('/api/expenses-by-category');
        const expenses = await response.json();
        
        console.log('Expenses by category:', expenses);
        return expenses;
    } catch (error) {
        console.error('Error loading expenses:', error);
        return [];
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load summary on dashboard
    if (document.querySelector('.summary-cards')) {
        loadSummary();
        // Refresh summary every 30 seconds
        setInterval(loadSummary, 30000);
        // Load charts if on dashboard
        if (document.getElementById('monthlyChart')) {
            loadMonthlyChart();
            loadCategoryChart();
        }
    }
    
    // Add smooth scrolling for all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Export data to CSV
function exportToCSV(data, filename = 'finance_tracker.csv') {
    const csv = convertToCSV(data);
    downloadCSV(csv, filename);
}

function convertToCSV(data) {
    const array = [Object.keys(data[0])].concat(data);
    return array.map(it => Object.values(it).toString()).join('\n');
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(csvFile);
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}
