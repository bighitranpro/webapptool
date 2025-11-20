// Utility function to make API calls with loading indicator
async function apiCall(endpoint, data, buttonElement = null) {
    try {
        // Show loading state
        if (buttonElement) {
            buttonElement.disabled = true;
            buttonElement.innerHTML = '<span class="loading"></span> Đang xử lý...';
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        // Restore button state
        if (buttonElement) {
            buttonElement.disabled = false;
            const icon = buttonElement.getAttribute('data-icon') || '✓';
            const text = buttonElement.getAttribute('data-text') || 'Xử lý';
            buttonElement.innerHTML = `<i class="fas fa-check"></i> ${text}`;
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        if (buttonElement) {
            buttonElement.disabled = false;
            const text = buttonElement.getAttribute('data-text') || 'Xử lý';
            buttonElement.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${text}`;
        }
        return { error: 'Lỗi kết nối API' };
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('✅ Đã sao chép vào clipboard!', 'success');
    }).catch(() => {
        showNotification('❌ Không thể sao chép!', 'error');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Display result helper
function displayResult(elementId, content) {
    const element = document.getElementById(elementId);
    element.innerHTML = content;
    element.classList.add('show');
    
    // Auto scroll to result
    element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 1. Extract Facebook Email
async function extractFacebookEmail() {
    const text = document.getElementById('fbExtractInput').value;
    if (!text.trim()) {
        displayResult('fbExtractResult', '<p class="error">⚠️ Vui lòng nhập văn bản!</p>');
        return;
    }

    const result = await apiCall('/api/extract-facebook-email', { text });
    
    let html = `<h4>📧 Kết quả trích xuất Email Facebook</h4>`;
    html += `<p><strong>Tổng số email tìm thấy:</strong> <span class="badge badge-primary">${result.count}</span></p>`;
    
    if (result.emails.length > 0) {
        html += '<div class="email-list">';
        result.emails.forEach((email, index) => {
            html += `<div class="email-item">${index + 1}. ${email}</div>`;
        });
        html += '</div>';
    } else {
        html += '<p class="warning">⚠️ Không tìm thấy email Facebook nào!</p>';
    }
    
    displayResult('fbExtractResult', html);
}

// 2. Check Facebook Code (Enhanced)
async function checkFacebookCode() {
    const email = document.getElementById('fbCodeInput').value;
    if (!email.trim()) {
        displayResult('fbCodeResult', '<p class="error">⚠️ Vui lòng nhập email!</p>');
        return;
    }

    const result = await apiCall('/api/check-facebook-code', { email });
    
    let html = `<h4>🔍 Kết quả kiểm tra nâng cao</h4>`;
    html += `<p><strong>Email:</strong> ${result.email}</p>`;
    
    if (result.can_receive) {
        html += '<p class="success">✅ Email này CÓ THỂ nhận được mã xác minh Facebook</p>';
        html += '<span class="badge badge-success">Hợp lệ</span>';
    } else {
        html += '<p class="error">❌ Email này KHÔNG THỂ nhận được mã xác minh Facebook</p>';
        html += '<span class="badge badge-danger">Không hợp lệ</span>';
    }
    
    // Advanced details
    if (result.domain) {
        html += `<div style="margin-top: 15px;"><strong>Chi tiết:</strong></div>`;
        html += `<p>📧 Domain: <code>${result.domain}</code></p>`;
        html += `<p>🔒 MX Record: ${result.has_mx_record ? '✅ Có' : '❌ Không'}</p>`;
        html += `<p>⭐ Nhà cung cấp tin cậy: ${result.is_trusted_provider ? '✅ Có' : '⚠️ Không'}</p>`;
        html += `<p><em>${result.details}</em></p>`;
    }
    
    displayResult('fbCodeResult', html);
}

// 3. Validate Email
async function validateEmail() {
    const email = document.getElementById('validateInput').value;
    if (!email.trim()) {
        displayResult('validateResult', '<p class="error">⚠️ Vui lòng nhập email!</p>');
        return;
    }

    const result = await apiCall('/api/validate-email', { email });
    
    let html = `<h4>🛡️ Kết quả Validation</h4>`;
    html += `<p><strong>Email:</strong> ${result.email || email}</p>`;
    
    if (result.valid) {
        html += '<p class="success">✅ Email hợp lệ!</p>';
        html += '<span class="badge badge-success">Valid</span>';
    } else {
        html += '<p class="error">❌ Email không hợp lệ!</p>';
        html += '<span class="badge badge-danger">Invalid</span>';
    }
    
    if (result.checks) {
        html += '<div style="margin-top: 15px;"><strong>Chi tiết kiểm tra:</strong></div>';
        for (let [key, value] of Object.entries(result.checks)) {
            const icon = value ? '✅' : '❌';
            const status = value ? 'success' : 'error';
            html += `<p class="${status}">${icon} ${key}: ${value ? 'Passed' : 'Failed'}</p>`;
        }
    }
    
    // Strength score
    if (result.strength_score !== undefined) {
        html += `<div style="margin-top: 15px;">`;
        html += `<strong>Điểm mạnh:</strong> ${result.strength_score}/100`;
        html += `<div class="progress-bar"><div class="progress-fill" style="width: ${result.strength_score}%"></div></div>`;
        html += `</div>`;
    }
    
    // Recommendation
    if (result.recommendation) {
        html += `<p style="margin-top: 10px; padding: 10px; background: #f0f8ff; border-left: 4px solid #3498db; border-radius: 4px;">`;
        html += `<strong>Khuyến nghị:</strong> ${result.recommendation}`;
        html += `</p>`;
    }
    
    displayResult('validateResult', html);
}

// 4. Extract Account Info
async function extractAccountInfo() {
    const email = document.getElementById('accountInfoInput').value;
    if (!email.trim()) {
        displayResult('accountInfoResult', '<p class="error">⚠️ Vui lòng nhập email!</p>');
        return;
    }

    const result = await apiCall('/api/extract-account-info', { email });
    
    if (result.error) {
        displayResult('accountInfoResult', `<p class="error">❌ ${result.error}</p>`);
        return;
    }
    
    let html = `<h4>👤 Thông tin tài khoản</h4>`;
    html += `<p><strong>Email:</strong> ${result.email}</p>`;
    html += `<p><strong>Username:</strong> ${result.username}</p>`;
    html += `<p><strong>Domain:</strong> ${result.domain}</p>`;
    html += `<p><strong>Tên gợi ý:</strong> ${result.potential_name}</p>`;
    
    if (result.is_facebook) {
        html += '<span class="badge badge-primary">✓ Facebook Email</span>';
    }
    
    displayResult('accountInfoResult', html);
}

// 5. Check Valid Facebook
async function checkValidFacebook() {
    const email = document.getElementById('validFbInput').value;
    if (!email.trim()) {
        displayResult('validFbResult', '<p class="error">⚠️ Vui lòng nhập email!</p>');
        return;
    }

    const result = await apiCall('/api/check-valid-facebook', { email });
    
    let html = `<h4>✅ Kiểm tra tính hợp lệ</h4>`;
    
    if (result.valid) {
        html += '<p class="success">✅ Email hợp lệ để đăng ký Facebook!</p>';
        html += `<p><strong>Domain:</strong> ${result.domain}</p>`;
        
        if (result.recommended) {
            html += '<span class="badge badge-success">Được khuyến nghị</span>';
        } else {
            html += '<span class="badge badge-warning">Có thể sử dụng</span>';
        }
    } else {
        html += '<p class="error">❌ Email không hợp lệ!</p>';
        html += `<p><strong>Lý do:</strong> ${result.reason}</p>`;
        html += '<span class="badge badge-danger">Không hợp lệ</span>';
    }
    
    displayResult('validFbResult', html);
}

// 6. Filter Emails
async function filterEmails() {
    const text = document.getElementById('filterInput').value;
    const removeDuplicates = document.getElementById('removeDuplicates').checked;
    
    if (!text.trim()) {
        displayResult('filterResult', '<p class="error">⚠️ Vui lòng nhập văn bản!</p>');
        return;
    }

    const result = await apiCall('/api/filter-emails', { text, remove_duplicates: removeDuplicates });
    
    let html = `<h4>🔍 Kết quả lọc Email</h4>`;
    
    html += '<div class="stats">';
    html += `<div class="stat-item">
                <div class="stat-value">${result.total_found}</div>
                <div class="stat-label">Tổng tìm thấy</div>
             </div>`;
    html += `<div class="stat-item">
                <div class="stat-value">${result.valid_emails.length}</div>
                <div class="stat-label">Email hợp lệ</div>
             </div>`;
    html += '</div>';
    
    if (result.emails.length > 0) {
        html += '<div class="email-list">';
        result.emails.forEach((email, index) => {
            const isValid = result.valid_emails.includes(email);
            const badge = isValid ? 'badge-success' : 'badge-danger';
            html += `<div class="email-item">
                        ${index + 1}. ${email} 
                        <span class="badge ${badge}">${isValid ? '✓' : '✗'}</span>
                     </div>`;
        });
        html += '</div>';
    } else {
        html += '<p class="warning">⚠️ Không tìm thấy email nào!</p>';
    }
    
    displayResult('filterResult', html);
}

// 7. Classify Email
async function classifyEmail() {
    const email = document.getElementById('classifyInput').value;
    if (!email.trim()) {
        displayResult('classifyResult', '<p class="error">⚠️ Vui lòng nhập email!</p>');
        return;
    }

    const result = await apiCall('/api/classify-email', { email });
    
    if (result.error) {
        displayResult('classifyResult', `<p class="error">❌ ${result.error}</p>`);
        return;
    }
    
    let html = `<h4>🏷️ Phân loại Email</h4>`;
    html += `<p><strong>Email:</strong> ${result.email}</p>`;
    html += `<p><strong>Loại:</strong> <span class="badge badge-primary">${result.type}</span></p>`;
    html += `<p><strong>Domain:</strong> ${result.domain}</p>`;
    html += `<p><strong>Nhà cung cấp:</strong> ${result.provider}</p>`;
    
    displayResult('classifyResult', html);
}

// 8. Generate Random Email
async function generateRandomEmail() {
    const count = parseInt(document.getElementById('randomCount').value) || 5;
    const includeNumbers = document.getElementById('includeNumbers').checked;
    
    if (count < 1 || count > 50) {
        displayResult('randomResult', '<p class="error">⚠️ Số lượng phải từ 1 đến 50!</p>');
        return;
    }

    const result = await apiCall('/api/generate-random-email', { count, include_numbers: includeNumbers });
    
    let html = `<h4>🎲 Email ngẫu nhiên</h4>`;
    html += `<p><strong>Số lượng:</strong> <span class="badge badge-info">${result.count}</span></p>`;
    
    if (result.emails.length > 0) {
        html += '<div class="email-list">';
        result.emails.forEach((email, index) => {
            html += `<div class="email-item">${index + 1}. ${email}</div>`;
        });
        html += '</div>';
    }
    
    displayResult('randomResult', html);
}

// 9. Scan Email Info
async function scanEmailInfo() {
    const email = document.getElementById('scanInput').value;
    if (!email.trim()) {
        displayResult('scanResult', '<p class="error">⚠️ Vui lòng nhập email!</p>');
        return;
    }

    const result = await apiCall('/api/scan-email', { email });
    
    if (result.error) {
        displayResult('scanResult', `<p class="error">❌ ${result.error}</p>`);
        return;
    }
    
    let html = `<h4>🔎 Thông tin chi tiết Email</h4>`;
    html += `<p><strong>Email:</strong> ${result.email}</p>`;
    html += `<p><strong>Email Hash (MD5):</strong> <code>${result.email_hash}</code></p>`;
    html += `<p><strong>Username:</strong> ${result.username}</p>`;
    html += `<p><strong>Domain:</strong> ${result.domain}</p>`;
    html += `<p><strong>TLD:</strong> ${result.tld}</p>`;
    
    if (result.potential_name) {
        html += `<p><strong>Tên gợi ý:</strong> ${result.potential_name}</p>`;
    }
    
    html += '<div style="margin-top: 15px;"><strong>Đặc điểm:</strong></div>';
    html += `<p>• Chứa số: ${result.has_numbers ? '✅ Có' : '❌ Không'}</p>`;
    html += `<p>• Chứa dấu chấm: ${result.has_dots ? '✅ Có' : '❌ Không'}</p>`;
    html += `<p>• Chứa gạch dưới: ${result.has_underscores ? '✅ Có' : '❌ Không'}</p>`;
    html += `<p>• Độ dài username: ${result.username_length} ký tự</p>`;
    
    html += `<p style="margin-top: 15px;"><strong>Scan ID:</strong> <code>${result.scan_id}</code></p>`;
    html += `<p><strong>Ngày scan:</strong> ${new Date(result.scan_date).toLocaleString('vi-VN')}</p>`;
    
    displayResult('scanResult', html);
}

// 10. Extract Providers
async function extractProviders() {
    const text = document.getElementById('providerInput').value;
    if (!text.trim()) {
        displayResult('providerResult', '<p class="error">⚠️ Vui lòng nhập văn bản!</p>');
        return;
    }

    const result = await apiCall('/api/extract-providers', { text });
    
    let html = `<h4>📊 Lọc theo nhà cung cấp</h4>`;
    html += `<p><strong>Tổng email:</strong> <span class="badge badge-primary">${result.total}</span></p>`;
    
    const categories = result.categorized;
    
    html += '<div class="category-section">';
    
    // Gmail
    if (categories.gmail.length > 0) {
        html += '<h5>📧 Gmail (' + categories.gmail.length + ')</h5>';
        html += '<div class="email-list">';
        categories.gmail.forEach((email, index) => {
            html += `<div class="email-item">${index + 1}. ${email}</div>`;
        });
        html += '</div>';
    }
    
    // Yahoo
    if (categories.yahoo.length > 0) {
        html += '<h5>📧 Yahoo (' + categories.yahoo.length + ')</h5>';
        html += '<div class="email-list">';
        categories.yahoo.forEach((email, index) => {
            html += `<div class="email-item">${index + 1}. ${email}</div>`;
        });
        html += '</div>';
    }
    
    // Hotmail
    if (categories.hotmail.length > 0) {
        html += '<h5>📧 Hotmail (' + categories.hotmail.length + ')</h5>';
        html += '<div class="email-list">';
        categories.hotmail.forEach((email, index) => {
            html += `<div class="email-item">${index + 1}. ${email}</div>`;
        });
        html += '</div>';
    }
    
    // Outlook
    if (categories.outlook.length > 0) {
        html += '<h5>📧 Outlook (' + categories.outlook.length + ')</h5>';
        html += '<div class="email-list">';
        categories.outlook.forEach((email, index) => {
            html += `<div class="email-item">${index + 1}. ${email}</div>`;
        });
        html += '</div>';
    }
    
    html += '</div>';
    
    if (result.total === 0) {
        html += '<p class="warning">⚠️ Không tìm thấy email từ các nhà cung cấp!</p>';
    }
    
    displayResult('providerResult', html);
}

// Clear result when input changes
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const card = this.closest('.tool-card');
            if (card) {
                const result = card.querySelector('.result');
                if (result) {
                    result.classList.remove('show');
                }
            }
        });
    });
});
