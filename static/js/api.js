/**
 * API Functions
 * Handle all API calls to backend
 */

const API_BASE = '/api';

/**
 * Run Email Validator
 */
async function runValidator() {
    const emailsText = document.getElementById('validatorEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const options = {
        check_mx: document.getElementById('checkMX').checked,
        check_smtp: document.getElementById('checkSMTP').checked,
        check_disposable: document.getElementById('checkDisposable').checked,
        check_fb_compat: document.getElementById('checkFBCompat').checked,
        max_workers: parseInt(document.getElementById('validatorWorkers').value),
        timeout: parseInt(document.getElementById('validatorTimeout').value)
    };
    
    toggleLoading(true, 'validatorResult', 'Đang kiểm tra emails...');
    document.getElementById('validatorProgress').style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, options })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update dashboard
            updateDashboardStats(data);
            
            // Update tables
            if (data.results) {
                updateLiveEmailsTable(data.results.live || []);
                updateDieEmailsTable(data.results.die || []);
            }
            
            // Display result
            displayResult('validatorResult', data, 'success');
            showNotification('Kiểm tra hoàn tất!', 'success');
        } else {
            displayResult('validatorResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        displayResult('validatorResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối', 'error');
    } finally {
        document.getElementById('validatorProgress').style.display = 'none';
    }
}

/**
 * Generate Emails
 */
async function generateEmails() {
    const params = {
        email_type: document.getElementById('emailType').value,
        text: document.getElementById('generatorText').value,
        total: parseInt(document.getElementById('generatorTotal').value),
        domain: document.getElementById('generatorDomain').value,
        char_type: document.getElementById('charType').value,
        number_type: document.getElementById('numberType').value
    };
    
    if (params.total < 1 || params.total > 10000) {
        showNotification('Số lượng phải từ 1 đến 10,000', 'warning');
        return;
    }
    
    toggleLoading(true, 'generatorOutput', 'Đang tạo emails...');
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success && data.emails) {
            // Display in output list
            const outputDiv = document.getElementById('generatorOutput');
            const countBadge = document.getElementById('generatorCount');
            
            countBadge.textContent = data.emails.length;
            outputDiv.innerHTML = data.emails.map((email, i) => 
                `<div class="email-item">${i + 1}. ${email}</div>`
            ).join('');
            
            showNotification(`Đã tạo ${data.emails.length} emails`, 'success');
        } else {
            document.getElementById('generatorOutput').innerHTML = 
                `<p class="empty-state error">Có lỗi: ${data.message || 'Unknown error'}</p>`;
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        document.getElementById('generatorOutput').innerHTML = 
            `<p class="empty-state error">Lỗi: ${error.message}</p>`;
        showNotification('Lỗi kết nối', 'error');
    }
}

/**
 * Copy generated list
 */
function copyGeneratedList() {
    const outputDiv = document.getElementById('generatorOutput');
    const emailItems = outputDiv.querySelectorAll('.email-item');
    
    if (emailItems.length === 0) {
        showNotification('Không có email để copy', 'warning');
        return;
    }
    
    const emails = Array.from(emailItems).map(item => {
        const text = item.textContent;
        return text.substring(text.indexOf('.') + 2);
    });
    
    navigator.clipboard.writeText(emails.join('\n')).then(() => {
        showNotification(`Đã copy ${emails.length} emails`, 'success');
    }).catch(err => {
        showNotification('Lỗi khi copy', 'error');
    });
}

/**
 * Extract Emails
 */
async function extractEmails() {
    const text = document.getElementById('extractorText').value;
    
    if (!text.trim()) {
        showNotification('Vui lòng nhập văn bản', 'warning');
        return;
    }
    
    const options = {
        remove_dups: document.getElementById('extractorRemoveDups').checked,
        case_insensitive: document.getElementById('extractorCaseInsensitive').checked
    };
    
    toggleLoading(true, 'extractorResult', 'Đang trích xuất...');
    
    try {
        const response = await fetch(`${API_BASE}/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, options })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('extractorResult', data, 'success');
            showNotification(`Trích xuất được ${data.emails.length} emails`, 'success');
        } else {
            displayResult('extractorResult', data, 'error');
        }
    } catch (error) {
        displayResult('extractorResult', { message: error.message }, 'error');
    }
}

/**
 * Format Emails
 */
async function formatEmails() {
    const emailsText = document.getElementById('formatterEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const params = {
        case_format: document.getElementById('formatterCase').value,
        sort_type: document.getElementById('formatterSort').value || null
    };
    
    toggleLoading(true, 'formatterResult', 'Đang định dạng...');
    
    try {
        const response = await fetch(`${API_BASE}/format`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, ...params })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('formatterResult', data, 'success');
            showNotification('Định dạng hoàn tất', 'success');
        } else {
            displayResult('formatterResult', data, 'error');
        }
    } catch (error) {
        displayResult('formatterResult', { message: error.message }, 'error');
    }
}

/**
 * Filter Emails
 */
async function filterEmails() {
    const emailsText = document.getElementById('filterEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const filters = {
        remove_invalid: document.getElementById('filterInvalid').checked,
        remove_duplicates: document.getElementById('filterDuplicates').checked,
        has_numbers: document.getElementById('filterNumbers').checked ? true : null,
        domains: document.getElementById('filterDomains').value.split(',')
            .map(d => d.trim()).filter(d => d.length > 0)
    };
    
    toggleLoading(true, 'filterResult', 'Đang lọc...');
    
    try {
        const response = await fetch(`${API_BASE}/filter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, filters })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('filterResult', data, 'success');
            showNotification('Lọc hoàn tất', 'success');
        } else {
            displayResult('filterResult', data, 'error');
        }
    } catch (error) {
        displayResult('filterResult', { message: error.message }, 'error');
    }
}

// Additional API functions for other tools...
// Split, Combine, Analyze, Deduplicate, Batch Process
// These follow similar patterns to the above functions
