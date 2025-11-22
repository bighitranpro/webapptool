/**
 * Email Checker - Frontend JavaScript
 * Integrated with BI Tool backend API
 */

// Global variables
let generatedEmails = [];
let checkResults = [];
let checkingInterval = null;
let charts = { smtp: null, facebook: null, country: null };

// DOM elements
const emailCountInput = document.getElementById('emailCount');
const mixRatioInput = document.getElementById('mixRatio');
const mixRatioValue = document.getElementById('mixRatioValue');
const generateBtn = document.getElementById('generateBtn');
const checkBtn = document.getElementById('checkBtn');
const exportBtn = document.getElementById('exportBtn');
const resultsBody = document.getElementById('resultsBody');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const statsContainer = document.getElementById('statsContainer');
const resultsInfo = document.getElementById('resultsInfo');

// Update mix ratio display
mixRatioInput.addEventListener('input', (e) => {
    mixRatioValue.textContent = `${e.target.value}%`;
});

// Generate emails
generateBtn.addEventListener('click', async () => {
    const count = parseInt(emailCountInput.value);
    const mixRatio = parseInt(mixRatioInput.value) / 100;

    if (count < 1 || count > 1000) {
        showNotification('Số lượng email phải từ 1 đến 1000', 'error');
        return;
    }

    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang tạo...';

    try {
        const response = await fetch('/api/checker/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count, mix_ratio: mixRatio })
        });

        const data = await response.json();

        if (data.success) {
            generatedEmails = data.emails;
            checkResults = [];
            displayEmails(generatedEmails);
            checkBtn.disabled = false;
            exportBtn.disabled = true;
            statsContainer.style.display = 'none';
            showNotification(`✅ Đã tạo ${data.count} email`, 'success');
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        showNotification(`❌ Lỗi: ${error.message}`, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-dice"></i> Tạo Email';
    }
});

// Check emails
checkBtn.addEventListener('click', async () => {
    if (generatedEmails.length === 0) {
        showNotification('Vui lòng tạo email trước', 'error');
        return;
    }

    checkBtn.disabled = true;
    checkBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang kiểm tra...';
    progressContainer.style.display = 'block';
    checkResults = [];

    try {
        const response = await fetch('/api/checker/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails: generatedEmails })
        });

        const data = await response.json();

        if (data.success) {
            // Start polling for progress
            startProgressPolling();
        } else {
            throw new Error(data.message || 'Unknown error');
        }
    } catch (error) {
        showNotification(`❌ Lỗi: ${error.message}`, 'error');
        checkBtn.disabled = false;
        checkBtn.innerHTML = '<i class="fas fa-check"></i> Kiểm Tra';
        progressContainer.style.display = 'none';
    }
});

// Start polling for progress
function startProgressPolling() {
    checkingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/checker/progress');
            const data = await response.json();

            updateProgress(data);

            if (!data.is_running) {
                stopProgressPolling();
                
                if (data.status === 'completed') {
                    checkResults = data.results;
                    displayResults(checkResults);
                    updateCharts(checkResults);
                    exportBtn.disabled = false;
                    showNotification('✅ Kiểm tra hoàn tất!', 'success');
                } else if (data.status.startsWith('error')) {
                    showNotification(`❌ Lỗi: ${data.status}`, 'error');
                }

                checkBtn.disabled = false;
                checkBtn.innerHTML = '<i class="fas fa-check"></i> Kiểm Tra';
            }
        } catch (error) {
            console.error('Progress polling error:', error);
        }
    }, 1000);
}

// Stop progress polling
function stopProgressPolling() {
    if (checkingInterval) {
        clearInterval(checkingInterval);
        checkingInterval = null;
    }
}

// Update progress bar
function updateProgress(data) {
    const percent = data.total > 0 ? (data.current / data.total * 100) : 0;
    progressBar.style.width = `${percent}%`;
    progressBar.textContent = `${percent.toFixed(0)}%`;
    progressText.textContent = `Đang xử lý: ${data.current} / ${data.total}`;

    // Update partial results
    if (data.results && data.results.length > 0) {
        displayResults(data.results);
    }
}

// Display generated emails
function displayEmails(emails) {
    resultsBody.innerHTML = '';
    emails.forEach((email, index) => {
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td class="email-cell">${email}</td>
                <td><span class="badge badge-pending">Chờ kiểm tra</span></td>
                <td><span class="badge badge-pending">Chờ kiểm tra</span></td>
                <td><span class="badge badge-pending">Chờ kiểm tra</span></td>
                <td>-</td>
            </tr>
        `;
        resultsBody.innerHTML += row;
    });
    updateResultsInfo(emails.length, 0);
}

// Display results
function displayResults(results) {
    resultsBody.innerHTML = '';
    results.forEach((result, index) => {
        const smtpBadge = getStatusBadge(result.smtp_status);
        const fbBadge = result.has_facebook ? 
            '<span class="badge badge-yes">✓ Yes</span>' : 
            '<span class="badge badge-no">✗ No</span>';
        const scoreBadge = getScoreBadge(result.score);

        const row = `
            <tr>
                <td>${index + 1}</td>
                <td class="email-cell" title="${result.email}">${result.email}</td>
                <td>${smtpBadge}</td>
                <td>${fbBadge}</td>
                <td>${result.country}</td>
                <td>${scoreBadge}</td>
            </tr>
        `;
        resultsBody.innerHTML += row;
    });
    updateResultsInfo(results.length, results.length);
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'LIVE': '<span class="badge badge-live">✓ LIVE</span>',
        'DIE': '<span class="badge badge-die">✗ DIE</span>',
        'UNKNOWN': '<span class="badge badge-unknown">? UNKNOWN</span>'
    };
    return badges[status] || '<span class="badge badge-pending">-</span>';
}

// Get score badge HTML
function getScoreBadge(score) {
    const value = (score * 100).toFixed(0);
    let className = 'badge-low';
    if (score >= 0.7) className = 'badge-high';
    else if (score >= 0.4) className = 'badge-medium';
    
    return `<span class="badge ${className}">${value}%</span>`;
}

// Update results info
function updateResultsInfo(total, checked) {
    resultsInfo.innerHTML = `
        <p>
            <i class="fas fa-info-circle"></i> 
            Tổng số email: <strong>${total}</strong> | 
            Đã kiểm tra: <strong>${checked}</strong>
        </p>
    `;
}

// Update charts
function updateCharts(results) {
    statsContainer.style.display = 'flex';

    // SMTP Chart
    const smtpData = {
        live: results.filter(r => r.smtp_status === 'LIVE').length,
        die: results.filter(r => r.smtp_status === 'DIE').length,
        unknown: results.filter(r => r.smtp_status === 'UNKNOWN').length
    };

    updateOrCreateChart('smtpChart', 'smtp', 'SMTP Status', 
        ['LIVE', 'DIE', 'UNKNOWN'],
        [smtpData.live, smtpData.die, smtpData.unknown],
        ['#4CAF50', '#f44336', '#FF9800']
    );

    // Facebook Chart
    const fbData = {
        yes: results.filter(r => r.has_facebook).length,
        no: results.filter(r => !r.has_facebook).length
    };

    updateOrCreateChart('facebookChart', 'facebook', 'Facebook Account',
        ['Có Facebook', 'Không có'],
        [fbData.yes, fbData.no],
        ['#2196F3', '#9E9E9E']
    );

    // Country Chart
    const countries = {};
    results.forEach(r => {
        countries[r.country] = (countries[r.country] || 0) + 1;
    });
    
    const topCountries = Object.entries(countries)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    updateOrCreateChart('countryChart', 'country', 'Top 5 Quốc Gia',
        topCountries.map(c => c[0]),
        topCountries.map(c => c[1]),
        ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    );
}

// Create or update chart
function updateOrCreateChart(canvasId, chartKey, title, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    
    if (charts[chartKey]) {
        charts[chartKey].data.labels = labels;
        charts[chartKey].data.datasets[0].data = data;
        charts[chartKey].update();
    } else {
        charts[chartKey] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: '#333', 
                            font: { size: 12 },
                            padding: 15
                        }
                    },
                    title: {
                        display: true,
                        text: title,
                        color: '#333',
                        font: { size: 16, weight: 'bold' },
                        padding: { top: 10, bottom: 20 }
                    }
                }
            }
        });
    }
}

// Export to CSV
exportBtn.addEventListener('click', async () => {
    if (checkResults.length === 0) {
        showNotification('Không có dữ liệu để xuất', 'error');
        return;
    }

    exportBtn.disabled = true;
    exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xuất...';

    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        const filename = `email_check_${timestamp}.csv`;

        const response = await fetch('/api/checker/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ results: checkResults, filename })
        });

        const data = await response.json();

        if (data.success) {
            // Trigger download
            window.location.href = `/api/checker/download/${data.filename}`;
            showNotification(`✅ Đã xuất file: ${data.filename}`, 'success');
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        showNotification(`❌ Lỗi: ${error.message}`, 'error');
    } finally {
        exportBtn.disabled = false;
        exportBtn.innerHTML = '<i class="fas fa-download"></i> Xuất CSV';
    }
});

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Email Checker loaded successfully');
    updateResultsInfo(0, 0);
});
