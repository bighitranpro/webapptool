/**
 * Complete API Functions
 * Handle all API calls to backend - 100% functional
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
    const progressDiv = document.getElementById('validatorProgress');
    if (progressDiv) progressDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, options })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update dashboard stats
            if (data.stats) {
                updateDashboardStats(data);
            }
            
            // Update tables
            if (data.results) {
                updateLiveEmailsTable(data.results.live || []);
                updateDieEmailsTable(data.results.die || []);
            }
            
            // Display detailed result
            displayValidationResult('validatorResult', data);
            showNotification(`Kiểm tra hoàn tất! LIVE: ${data.stats.live}, DIE: ${data.stats.die}`, 'success');
        } else {
            displayResult('validatorResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Validation error:', error);
        displayResult('validatorResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    } finally {
        if (progressDiv) progressDiv.style.display = 'none';
    }
}

/**
 * Display validation result with detailed stats
 */
function displayValidationResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const stats = data.stats || {};
    const results = data.results || {};
    
    const html = `
        <div class="validation-summary">
            <h4><i class="fas fa-check-circle"></i> Kết quả kiểm tra</h4>
            <div class="stats-grid-small">
                <div class="stat-item">
                    <span class="stat-label">Tổng:</span>
                    <span class="stat-value">${stats.total || 0}</span>
                </div>
                <div class="stat-item stat-live">
                    <span class="stat-label">LIVE:</span>
                    <span class="stat-value">${stats.live || 0}</span>
                </div>
                <div class="stat-item stat-die">
                    <span class="stat-label">DIE:</span>
                    <span class="stat-value">${stats.die || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Unknown:</span>
                    <span class="stat-value">${stats.unknown || 0}</span>
                </div>
                <div class="stat-item stat-code">
                    <span class="stat-label">Nhận code:</span>
                    <span class="stat-value">${stats.can_receive_code || 0}</span>
                </div>
            </div>
            <p class="processing-time">Thời gian xử lý: ${stats.processing_time || 0}s</p>
        </div>
    `;
    
    container.innerHTML = html;
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
    
    if (!params.domain || params.domain.trim() === '') {
        params.domain = 'gmail.com';
    }
    
    const outputDiv = document.getElementById('generatorOutput');
    outputDiv.innerHTML = '<div class="loading-indicator"><div class="spinner"></div><p>Đang tạo emails...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success && data.emails) {
            const countBadge = document.getElementById('generatorCount');
            if (countBadge) {
                countBadge.textContent = data.emails.length;
            }
            
            outputDiv.innerHTML = data.emails.map((email, i) => 
                `<div class="email-item">${i + 1}. ${email}</div>`
            ).join('');
            
            showNotification(`Đã tạo ${data.emails.length} emails`, 'success');
        } else {
            outputDiv.innerHTML = `<p class="empty-state error">Có lỗi: ${data.message || 'Unknown error'}</p>`;
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Generation error:', error);
        outputDiv.innerHTML = `<p class="empty-state error">Lỗi: ${error.message}</p>`;
        showNotification('Lỗi kết nối API', 'error');
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
        console.error('Copy error:', err);
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
            showNotification(`Trích xuất được ${data.total_emails} emails`, 'success');
        } else {
            displayResult('extractorResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Extract error:', error);
        displayResult('extractorResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
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
        emails: emails,
        case_format: document.getElementById('formatterCase').value,
        sort_type: document.getElementById('formatterSort').value || null
    };
    
    toggleLoading(true, 'formatterResult', 'Đang định dạng...');
    
    try {
        const response = await fetch(`${API_BASE}/format`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('formatterResult', data, 'success');
            showNotification('Định dạng hoàn tất', 'success');
        } else {
            displayResult('formatterResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Format error:', error);
        displayResult('formatterResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
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
    
    const domainsText = document.getElementById('filterDomains').value;
    const domains = domainsText ? domainsText.split(',').map(d => d.trim()).filter(d => d.length > 0) : [];
    
    const filters = {
        remove_invalid: document.getElementById('filterInvalid').checked,
        remove_duplicates: document.getElementById('filterDuplicates').checked,
        has_numbers: document.getElementById('filterNumbers').checked ? true : null,
        domains: domains.length > 0 ? domains : null
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
            const filtered = data.stats.filtered_out || 0;
            showNotification(`Lọc hoàn tất. Đã loại bỏ ${filtered} emails`, 'success');
        } else {
            displayResult('filterResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Filter error:', error);
        displayResult('filterResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Split Emails
 */
async function splitEmails() {
    const emailsText = document.getElementById('splitterEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const method = document.getElementById('splitterMethod').value;
    const count = parseInt(document.getElementById('splitterCount').value);
    
    const params = {
        emails: emails,
        method: method,
        count: method === 'count' ? count : null,
        chunks: method === 'chunks' ? count : null
    };
    
    toggleLoading(true, 'splitterResult', 'Đang chia...');
    
    try {
        const response = await fetch(`${API_BASE}/split`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySplitResult('splitterResult', data);
            showNotification('Chia hoàn tất', 'success');
        } else {
            displayResult('splitterResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Split error:', error);
        displayResult('splitterResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Display split result
 */
function displaySplitResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = `
        <div class="result-summary">
            <h4><i class="fas fa-cut"></i> Kết quả chia</h4>
            <p>Tổng emails: <strong>${data.total_emails}</strong></p>
    `;
    
    if (data.chunks) {
        html += `<p>Số phần: <strong>${data.num_chunks}</strong></p>`;
        html += '<div class="chunks-container">';
        data.chunks.forEach((chunk, index) => {
            html += `
                <div class="chunk-item">
                    <h5>Phần ${index + 1} (${chunk.length} emails)</h5>
                    <textarea readonly rows="5">${chunk.join('\n')}</textarea>
                </div>
            `;
        });
        html += '</div>';
    } else if (data.domain_groups) {
        html += `<p>Số domains: <strong>${data.num_domains}</strong></p>`;
        html += '<div class="chunks-container">';
        for (const [domain, emails] of Object.entries(data.domain_groups)) {
            html += `
                <div class="chunk-item">
                    <h5>${domain} (${emails.length} emails)</h5>
                    <textarea readonly rows="5">${emails.join('\n')}</textarea>
                </div>
            `;
        }
        html += '</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Combine Emails
 */
async function combineEmails() {
    const list1Text = document.getElementById('combinerList1').value;
    const list2Text = document.getElementById('combinerList2').value;
    
    const list1 = parseEmails(list1Text);
    const list2 = parseEmails(list2Text);
    
    if (list1.length === 0 || list2.length === 0) {
        showNotification('Vui lòng nhập cả 2 danh sách', 'warning');
        return;
    }
    
    const method = document.getElementById('combinerMethod').value;
    
    const params = {
        email_lists: [list1, list2],
        method: method,
        case_sensitive: false
    };
    
    toggleLoading(true, 'combinerResult', 'Đang gộp...');
    
    try {
        const response = await fetch(`${API_BASE}/combine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('combinerResult', data, 'success');
            showNotification(`Gộp hoàn tất. Kết quả: ${data.total_output} emails`, 'success');
        } else {
            displayResult('combinerResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Combine error:', error);
        displayResult('combinerResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Analyze Emails
 */
async function analyzeEmails() {
    const emailsText = document.getElementById('analyzerEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    toggleLoading(true, 'analyzerResult', 'Đang phân tích...');
    
    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAnalysisResult('analyzerResult', data);
            showNotification('Phân tích hoàn tất', 'success');
        } else {
            displayResult('analyzerResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        displayResult('analyzerResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Display analysis result
 */
function displayAnalysisResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const domains = data.domains || {};
    const patterns = data.patterns || {};
    const length = data.length || {};
    const providers = data.providers || {};
    
    const html = `
        <div class="analysis-result">
            <h4><i class="fas fa-chart-bar"></i> Kết quả phân tích</h4>
            
            <div class="analysis-section">
                <h5>Domains (Top 5)</h5>
                <ul>
                    ${(domains.top_domains || []).slice(0, 5).map(([domain, count]) => 
                        `<li>${domain}: <strong>${count}</strong> emails</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div class="analysis-section">
                <h5>Mẫu (Patterns)</h5>
                <ul>
                    <li>Có số: ${patterns.patterns?.has_numbers || 0} (${patterns.percentages?.has_numbers || 0}%)</li>
                    <li>Có dấu chấm: ${patterns.patterns?.has_dots || 0} (${patterns.percentages?.has_dots || 0}%)</li>
                    <li>Toàn chữ thường: ${patterns.patterns?.all_lowercase || 0} (${patterns.percentages?.all_lowercase || 0}%)</li>
                </ul>
            </div>
            
            <div class="analysis-section">
                <h5>Độ dài</h5>
                <p>Min: ${length.min || 0} | Max: ${length.max || 0} | Trung bình: ${length.avg || 0}</p>
            </div>
            
            <div class="analysis-section">
                <h5>Nhà cung cấp</h5>
                <ul>
                    ${Object.entries(providers.distribution || {}).map(([provider, count]) => 
                        `<li>${provider}: <strong>${count}</strong> (${providers.percentages?.[provider] || 0}%)</li>`
                    ).join('')}
                </ul>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

/**
 * Deduplicate Emails
 */
async function deduplicateEmails() {
    const emailsText = document.getElementById('deduplicatorEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const params = {
        emails: emails,
        method: document.getElementById('deduplicatorMethod').value,
        keep_strategy: document.getElementById('deduplicatorKeep').value
    };
    
    toggleLoading(true, 'deduplicatorResult', 'Đang loại trùng...');
    
    try {
        const response = await fetch(`${API_BASE}/deduplicate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('deduplicatorResult', data, 'success');
            const removed = data.stats.duplicates_removed || 0;
            showNotification(`Loại trùng hoàn tất. Đã loại bỏ ${removed} emails`, 'success');
        } else {
            displayResult('deduplicatorResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Deduplicate error:', error);
        displayResult('deduplicatorResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Process Batch
 */
async function processBatch() {
    const emailsText = document.getElementById('batchEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const params = {
        emails: emails,
        batch_size: parseInt(document.getElementById('batchSize').value),
        operation: document.getElementById('batchOperation').value,
        max_workers: parseInt(document.getElementById('batchWorkers').value)
    };
    
    const progressDiv = document.getElementById('batchProgress');
    if (progressDiv) progressDiv.style.display = 'block';
    toggleLoading(true, 'batchResult', 'Đang xử lý hàng loạt...');
    
    try {
        const response = await fetch(`${API_BASE}/batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBatchResult('batchResult', data);
            showNotification('Xử lý hàng loạt hoàn tất', 'success');
        } else {
            displayResult('batchResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Batch error:', error);
        displayResult('batchResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    } finally {
        if (progressDiv) progressDiv.style.display = 'none';
    }
}

/**
 * Display batch result
 */
function displayBatchResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const stats = data.stats || {};
    
    const html = `
        <div class="batch-result">
            <h4><i class="fas fa-layer-group"></i> Kết quả xử lý hàng loạt</h4>
            <div class="stats-grid-small">
                <div class="stat-item">
                    <span class="stat-label">Tổng emails:</span>
                    <span class="stat-value">${stats.total_emails || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Batches:</span>
                    <span class="stat-value">${stats.batches_processed || 0}</span>
                </div>
                <div class="stat-item stat-live">
                    <span class="stat-label">Thành công:</span>
                    <span class="stat-value">${stats.successful || 0}</span>
                </div>
                <div class="stat-item stat-die">
                    <span class="stat-label">Thất bại:</span>
                    <span class="stat-value">${stats.failed || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Thời gian:</span>
                    <span class="stat-value">${stats.processing_time || 0}s</span>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Add CSS for new styles
const analysisStyle = document.createElement('style');
analysisStyle.textContent = `
    .stats-grid-small {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin: 15px 0;
    }
    
    .stat-item {
        background: white;
        padding: 10px;
        border-radius: 8px;
        border-left: 3px solid #3498db;
    }
    
    .stat-item.stat-live {
        border-left-color: #2ecc71;
    }
    
    .stat-item.stat-die {
        border-left-color: #e74c3c;
    }
    
    .stat-item.stat-code {
        border-left-color: #f39c12;
    }
    
    .stat-label {
        display: block;
        font-size: 0.85rem;
        color: #7f8c8d;
        margin-bottom: 5px;
    }
    
    .stat-value {
        display: block;
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .validation-summary,
    .analysis-result,
    .batch-result {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
    }
    
    .analysis-section {
        margin: 15px 0;
        padding: 15px;
        background: white;
        border-radius: 8px;
    }
    
    .analysis-section h5 {
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .analysis-section ul {
        list-style: none;
        padding: 0;
    }
    
    .analysis-section li {
        padding: 5px 0;
        border-bottom: 1px solid #ecf0f1;
    }
    
    .chunks-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    
    .chunk-item {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ecf0f1;
    }
    
    .chunk-item h5 {
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .chunk-item textarea {
        width: 100%;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        border: 1px solid #ecf0f1;
        border-radius: 4px;
        padding: 10px;
    }
    
    .email-item {
        padding: 8px;
        border-bottom: 1px solid #ecf0f1;
        transition: background 0.2s;
    }
    
    .email-item:hover {
        background: #f8f9fa;
    }
    
    .processing-time {
        margin-top: 15px;
        font-style: italic;
        color: #7f8c8d;
    }
`;
document.head.appendChild(analysisStyle);

console.log('Complete API functions loaded successfully');
