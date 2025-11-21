/**
 * Admin Tools Control JavaScript
 * Handle all tool operations from admin panel
 */

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function updateInputCount(textareaId, countId, label = 'items') {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(countId);
    if (!textarea || !counter) return;
    
    textarea.addEventListener('input', function() {
        const lines = this.value.split('\n').filter(line => line.trim().length > 0);
        counter.textContent = `${lines.length} ${label}`;
    });
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const button = event.currentTarget;
    const icon = button.querySelector('.fa-chevron-down');
    
    section.classList.toggle('active');
    icon.style.transform = section.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0)';
}

function downloadTextFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showNotification('Failed to copy', 'error');
    });
}

// =============================================================================
// EMAIL VALIDATOR
// =============================================================================

let validatorResults = { live: [], die: [], unknown: [] };

async function runValidator() {
    const input = document.getElementById('validatorInput').value.trim();
    if (!input) {
        showNotification('Please enter emails to validate', 'error');
        return;
    }

    const emails = input.split('\n').filter(e => e.trim().length > 0);
    
    const options = {
        check_mx: document.getElementById('checkMX').checked,
        check_smtp: document.getElementById('checkSMTP').checked,
        check_disposable: document.getElementById('checkDisposable').checked,
        check_fb_compat: document.getElementById('checkFBCompat').checked,
        use_cache: document.getElementById('useCache').checked,
        max_workers: parseInt(document.getElementById('validatorWorkers').value)
    };

    // Show progress
    document.getElementById('validatorProgress').style.display = 'block';
    document.getElementById('validatorResults').style.display = 'none';
    
    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, options })
        });

        const data = await response.json();
        
        if (data.success) {
            validatorResults = data.results;
            displayValidatorResults(data);
            showNotification(`Validation complete! ${data.stats.live} LIVE, ${data.stats.die} DIE`, 'success');
        } else {
            showNotification(data.message || 'Validation failed', 'error');
        }
    } catch (error) {
        console.error('Validator error:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        document.getElementById('validatorProgress').style.display = 'none';
    }
}

function displayValidatorResults(data) {
    document.getElementById('validatorResults').style.display = 'block';
    
    // Update counts
    document.getElementById('validatorLiveCount').textContent = data.stats.live;
    document.getElementById('validatorDieCount').textContent = data.stats.die;
    document.getElementById('validatorUnknownCount').textContent = data.stats.unknown;
    
    // Show LIVE tab by default
    showValidatorTab('live');
}

function showValidatorTab(tab) {
    const tabs = document.querySelectorAll('#validatorResults .tab-btn');
    tabs.forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    const list = document.getElementById('validatorResultsList');
    const results = validatorResults[tab] || [];
    
    list.innerHTML = results.map(email => `
        <div class="result-item">
            <span class="result-email">${typeof email === 'string' ? email : email.email}</span>
            ${email.can_receive_code ? '<span class="badge badge-success">Can Receive Code</span>' : ''}
        </div>
    `).join('');
}

function exportValidatorResults(type) {
    let content = '';
    let filename = '';
    
    if (type === 'live') {
        content = validatorResults.live.map(e => typeof e === 'string' ? e : e.email).join('\n');
        filename = 'live_emails.txt';
    } else if (type === 'die') {
        content = validatorResults.die.map(e => typeof e === 'string' ? e : e.email).join('\n');
        filename = 'die_emails.txt';
    } else {
        content = [...validatorResults.live, ...validatorResults.die, ...validatorResults.unknown]
            .map(e => typeof e === 'string' ? e : e.email).join('\n');
        filename = 'all_emails.txt';
    }
    
    downloadTextFile(content, filename);
    showNotification(`Exported ${type.toUpperCase()} emails`, 'success');
}

function copyValidatorResults() {
    const activeTab = document.querySelector('#validatorResults .tab-btn.active').textContent.toLowerCase();
    const results = validatorResults[activeTab] || [];
    const text = results.map(e => typeof e === 'string' ? e : e.email).join('\n');
    copyToClipboard(text);
}

function clearValidatorInput() {
    document.getElementById('validatorInput').value = '';
    document.getElementById('validatorInputCount').textContent = '0 emails';
    document.getElementById('validatorResults').style.display = 'none';
}

function loadSampleEmails(type) {
    const samples = [
        'test1@gmail.com',
        'test2@yahoo.com',
        'test3@hotmail.com',
        'test4@outlook.com',
        'test5@gmail.com'
    ];
    
    if (type === 'validator') {
        document.getElementById('validatorInput').value = samples.join('\n');
        document.getElementById('validatorInputCount').textContent = `${samples.length} emails`;
    } else if (type === 'fb') {
        document.getElementById('fbCheckerInput').value = samples.join('\n');
        document.getElementById('fbCheckerInputCount').textContent = `${samples.length} emails`;
    }
}

async function loadValidatorStats() {
    try {
        const response = await fetch('/api/db/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('validatorTotalStat').textContent = data.stats.total || 0;
            document.getElementById('validatorSuccessRate').textContent = 
                (data.stats.live_rate || 0).toFixed(2) + '%';
            document.getElementById('validatorCachedCount').textContent = data.stats.total || 0;
        }
    } catch (error) {
        console.error('Failed to load validator stats:', error);
    }
}

// =============================================================================
// EMAIL GENERATOR
// =============================================================================

let generatorResults = [];

async function runGenerator() {
    const emailType = document.getElementById('emailType').value;
    const total = parseInt(document.getElementById('emailTotal').value);
    const charType = document.getElementById('charType').value;
    const baseText = document.getElementById('baseText').value.trim();
    const numberType = document.getElementById('numberType').value;
    const domainsInput = document.getElementById('emailDomains').value.trim();
    
    if (total < 1 || total > 10000) {
        showNotification('Total must be between 1 and 10,000', 'error');
        return;
    }
    
    const domains = domainsInput.split(',').map(d => d.trim()).filter(d => d.length > 0);
    if (domains.length === 0) {
        showNotification('Please enter at least one domain', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_type: emailType,
                text: baseText,
                total: total,
                domains: domains,
                char_type: charType,
                number_type: numberType
            })
        });

        const data = await response.json();
        
        if (data.success && data.emails) {
            generatorResults = data.emails;
            displayGeneratorResults(data);
            showNotification(`Generated ${data.emails.length} emails successfully!`, 'success');
        } else {
            showNotification(data.message || 'Generation failed', 'error');
        }
    } catch (error) {
        console.error('Generator error:', error);
        showNotification('Network error. Please try again.', 'error');
    }
}

function displayGeneratorResults(data) {
    document.getElementById('generatorResults').style.display = 'block';
    document.getElementById('generatorCount').textContent = data.emails.length;
    
    const list = document.getElementById('generatorResultsList');
    list.innerHTML = data.emails.map(email => `
        <div class="result-item">
            <span class="result-email">${email}</span>
        </div>
    `).join('');
}

function exportGeneratorResults() {
    const content = generatorResults.join('\n');
    downloadTextFile(content, 'generated_emails.txt');
    showNotification('Exported generated emails', 'success');
}

function copyGeneratorResults() {
    const text = generatorResults.join('\n');
    copyToClipboard(text);
}

function sendToValidator() {
    const text = generatorResults.join('\n');
    
    // Switch to validator page
    const validatorNav = document.querySelector('[data-page="validator"]');
    if (validatorNav) {
        validatorNav.click();
        
        // Set input
        setTimeout(() => {
            document.getElementById('validatorInput').value = text;
            document.getElementById('validatorInputCount').textContent = `${generatorResults.length} emails`;
            showNotification('Emails sent to validator', 'success');
        }, 100);
    }
}

function clearGeneratorResults() {
    document.getElementById('baseText').value = '';
    document.getElementById('generatorResults').style.display = 'none';
    generatorResults = [];
}

// =============================================================================
// FACEBOOK CHECKER
// =============================================================================

let fbResults = { linked: [], hidden_linked: [], not_linked: [], error: [] };

async function runFBChecker() {
    const input = document.getElementById('fbCheckerInput').value.trim();
    if (!input) {
        showNotification('Please enter emails to check', 'error');
        return;
    }

    const emails = input.split('\n').filter(e => e.trim().length > 0);
    
    const options = {
        api_type: document.getElementById('fbApiType').value,
        max_workers: parseInt(document.getElementById('fbMaxWorkers').value),
        start_from: parseInt(document.getElementById('fbStartFrom').value),
        check_code_68: document.getElementById('checkCode68').checked
    };
    
    // Add proxy config if enabled
    const proxyType = document.getElementById('fbProxyType').value;
    if (proxyType) {
        options.proxy_config = {
            enabled: true,
            type: proxyType,
            host: document.getElementById('fbProxyHost').value,
            port: parseInt(document.getElementById('fbProxyPort').value),
            auth: {
                username: document.getElementById('fbProxyUser').value,
                password: document.getElementById('fbProxyPass').value
            }
        };
    }

    document.getElementById('fbProgress').style.display = 'block';
    document.getElementById('fbResults').style.display = 'none';
    
    try {
        const response = await fetch('/api/fb-check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, options })
        });

        const data = await response.json();
        
        if (data.success) {
            fbResults = data.results;
            displayFBResults(data);
            showNotification(`FB check complete! ${data.stats.linked} linked`, 'success');
        } else {
            showNotification(data.message || 'FB check failed', 'error');
        }
    } catch (error) {
        console.error('FB checker error:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        document.getElementById('fbProgress').style.display = 'none';
    }
}

function displayFBResults(data) {
    document.getElementById('fbResults').style.display = 'block';
    
    document.getElementById('fbLinkedCount').textContent = data.stats.linked || 0;
    document.getElementById('fbHiddenCount').textContent = data.stats.hidden_linked || 0;
    document.getElementById('fbNotLinkedCount').textContent = data.stats.not_linked || 0;
    document.getElementById('fbErrorCount').textContent = data.stats.error || 0;
    
    showFBTab('linked');
}

function showFBTab(tab) {
    const tabs = document.querySelectorAll('#fbResults .tab-btn');
    tabs.forEach(t => t.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    
    const list = document.getElementById('fbResultsList');
    const results = fbResults[tab.replace('-', '_')] || [];
    
    list.innerHTML = results.map(item => `
        <div class="result-item">
            <span class="result-email">${item.email || item}</span>
            ${item.code_length ? `<span class="badge badge-info">Code ${item.code_length}</span>` : ''}
        </div>
    `).join('');
}

function exportFBResults(type) {
    let content = '';
    let filename = '';
    
    if (type === 'linked') {
        content = fbResults.linked.map(e => e.email || e).join('\n');
        filename = 'fb_linked.txt';
    } else {
        content = [...fbResults.linked, ...fbResults.hidden_linked, ...fbResults.not_linked, ...fbResults.error]
            .map(e => e.email || e).join('\n');
        filename = 'fb_all_results.txt';
    }
    
    downloadTextFile(content, filename);
    showNotification(`Exported ${type} results`, 'success');
}

function clearFBResults() {
    document.getElementById('fbCheckerInput').value = '';
    document.getElementById('fbResults').style.display = 'none';
}

// =============================================================================
// 2FA CHECKER
// =============================================================================

let twoFAResults = { hit_2fa: [], has_page: [], not_hit: [], error: [] };

async function run2FAChecker() {
    const input = document.getElementById('twoFAInput').value.trim();
    if (!input) {
        showNotification('Please enter email:password accounts', 'error');
        return;
    }

    const accounts = input.split('\n').filter(a => a.trim().length > 0);
    
    const options = {
        api_type: document.getElementById('twoFAApiType').value,
        max_workers: parseInt(document.getElementById('twoFAMaxWorkers').value),
        start_from: parseInt(document.getElementById('twoFAStartFrom').value),
        password_pattern: document.getElementById('passwordPattern').value.trim(),
        validate_pattern: document.getElementById('validatePattern').checked
    };

    document.getElementById('twoFAProgress').style.display = 'block';
    document.getElementById('twoFAResults').style.display = 'none';
    
    try {
        const response = await fetch('/api/check-2fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ accounts, options })
        });

        const data = await response.json();
        
        if (data.success) {
            twoFAResults = data.results;
            display2FAResults(data);
            showNotification(`2FA check complete! ${data.stats.hit_2fa} hit 2FA`, 'success');
        } else {
            showNotification(data.message || '2FA check failed', 'error');
        }
    } catch (error) {
        console.error('2FA checker error:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        document.getElementById('twoFAProgress').style.display = 'none';
    }
}

function display2FAResults(data) {
    document.getElementById('twoFAResults').style.display = 'block';
    
    document.getElementById('twoFAHitCount').textContent = data.stats.hit_2fa || 0;
    document.getElementById('twoFAPageCount').textContent = data.stats.has_page || 0;
    document.getElementById('twoFANotHitCount').textContent = data.stats.not_hit || 0;
    document.getElementById('twoFAErrorCount').textContent = data.stats.error || 0;
    
    show2FATab('hit');
}

function show2FATab(tab) {
    const tabs = document.querySelectorAll('#twoFAResults .tab-btn');
    tabs.forEach(t => t.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    
    const list = document.getElementById('twoFAResultsList');
    const key = tab === 'hit' ? 'hit_2fa' : tab === 'page' ? 'has_page' : tab === 'not-hit' ? 'not_hit' : 'error';
    const results = twoFAResults[key] || [];
    
    list.innerHTML = results.map(item => `
        <div class="result-item">
            <span class="result-email">${item.account || item}</span>
            ${item.pages_count ? `<span class="badge badge-info">${item.pages_count} pages</span>` : ''}
        </div>
    `).join('');
}

function export2FAResults(type) {
    let content = '';
    let filename = '';
    
    if (type === 'hit') {
        content = twoFAResults.hit_2fa.map(e => e.account || e).join('\n');
        filename = '2fa_hit.txt';
    } else if (type === 'page') {
        content = twoFAResults.has_page.map(e => e.account || e).join('\n');
        filename = '2fa_has_page.txt';
    } else {
        content = [...twoFAResults.hit_2fa, ...twoFAResults.has_page, ...twoFAResults.not_hit, ...twoFAResults.error]
            .map(e => e.account || e).join('\n');
        filename = '2fa_all_results.txt';
    }
    
    downloadTextFile(content, filename);
    showNotification(`Exported ${type} results`, 'success');
}

function clear2FAResults() {
    document.getElementById('twoFAInput').value = '';
    document.getElementById('twoFAResults').style.display = 'none';
}

function loadSampleAccounts() {
    const samples = [
        'test1@gmail.com:password123',
        'test2@yahoo.com:mypass456',
        'test3@hotmail.com:testpass789'
    ];
    document.getElementById('twoFAInput').value = samples.join('\n');
    document.getElementById('twoFAInputCount').textContent = `${samples.length} accounts`;
}

// =============================================================================
// PAGE MINING
// =============================================================================

let miningResults = { pages: [], emails: [] };

async function runPageMining() {
    const input = document.getElementById('miningInput').value.trim();
    if (!input) {
        showNotification('Please enter UIDs to mine', 'error');
        return;
    }

    const uids = input.split('\n').filter(u => u.trim().length > 0);
    
    const options = {
        max_workers: parseInt(document.getElementById('miningMaxWorkers').value),
        start_from: parseInt(document.getElementById('miningStartFrom').value),
        filter_has_ads: document.getElementById('filterHasAds').checked,
        filter_verified: document.getElementById('filterVerified').checked
    };
    
    const country = document.getElementById('filterCountry').value.trim();
    if (country) {
        options.filter_country = country;
    }

    document.getElementById('miningProgress').style.display = 'block';
    document.getElementById('miningResults').style.display = 'none';
    
    try {
        const response = await fetch('/api/page-mining', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uids, options })
        });

        const data = await response.json();
        
        if (data.success) {
            miningResults = data.results;
            displayMiningResults(data);
            showNotification(`Mining complete! Found ${data.stats.total_pages_found} pages`, 'success');
        } else {
            showNotification(data.message || 'Mining failed', 'error');
        }
    } catch (error) {
        console.error('Mining error:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        document.getElementById('miningProgress').style.display = 'none';
    }
}

function displayMiningResults(data) {
    document.getElementById('miningResults').style.display = 'block';
    
    document.getElementById('miningPagesCount').textContent = data.stats.total_pages_found || 0;
    document.getElementById('miningEmailsCount').textContent = data.stats.emails_collected || 0;
    document.getElementById('miningAdsCount').textContent = data.stats.pages_with_ads || 0;
    document.getElementById('miningVerifiedCount').textContent = data.stats.pages_verified || 0;
    
    showMiningTab('pages');
}

function showMiningTab(tab) {
    const tabs = document.querySelectorAll('#miningResults .tab-btn');
    tabs.forEach(t => t.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    
    const list = document.getElementById('miningResultsList');
    const results = miningResults[tab] || [];
    
    if (tab === 'pages') {
        list.innerHTML = results.map(page => `
            <div class="result-item">
                <span class="result-email">${page.page_name || page.page_id}</span>
                ${page.has_ads ? '<span class="badge badge-warning">Ads</span>' : ''}
                ${page.verified ? '<span class="badge badge-success">Verified</span>' : ''}
            </div>
        `).join('');
    } else {
        list.innerHTML = results.map(email => `
            <div class="result-item">
                <span class="result-email">${email}</span>
            </div>
        `).join('');
    }
}

function exportMiningResults(type) {
    let content = '';
    let filename = '';
    
    if (type === 'pages') {
        content = miningResults.pages.map(p => `${p.page_id}|${p.page_name}`).join('\n');
        filename = 'mined_pages.txt';
    } else if (type === 'emails') {
        content = miningResults.emails.join('\n');
        filename = 'mined_emails.txt';
    } else {
        content = `PAGES:\n${miningResults.pages.map(p => `${p.page_id}|${p.page_name}`).join('\n')}\n\nEMAILS:\n${miningResults.emails.join('\n')}`;
        filename = 'mining_all_results.txt';
    }
    
    downloadTextFile(content, filename);
    showNotification(`Exported ${type} results`, 'success');
}

function clearMiningResults() {
    document.getElementById('miningInput').value = '';
    document.getElementById('miningResults').style.display = 'none';
}

function loadSampleUIDs() {
    const samples = [
        '100001234567890',
        '100009876543210',
        '100012345678901'
    ];
    document.getElementById('miningInput').value = samples.join('\n');
    document.getElementById('miningInputCount').textContent = `${samples.length} UIDs`;
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Setup input counters
    updateInputCount('validatorInput', 'validatorInputCount', 'emails');
    updateInputCount('fbCheckerInput', 'fbCheckerInputCount', 'emails');
    updateInputCount('twoFAInput', 'twoFAInputCount', 'accounts');
    updateInputCount('miningInput', 'miningInputCount', 'UIDs');
    
    // Load validator stats on page load
    loadValidatorStats();
    
    console.log('Admin Tools Control initialized');
});
