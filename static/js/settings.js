// Settings Dashboard JavaScript

let allowedDomains = [];
let customDomains = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    loadSettings();
    setupFileUploads();
    setupForms();
});

// Tab Navigation
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');

            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked
            btn.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// Load Settings
async function loadSettings() {
    try {
        const response = await fetch('/settings/api/settings');
        const data = await response.json();

        if (data.success) {
            populateGeneralForm(data.settings);
            populateGeneratorForm(data.settings);
            loadDomains();
            loadGeneratorConfig();
            loadSmtpSettings();
            loadNotificationSettings();

            // Load logo and favicon previews
            if (data.settings.logo_url) {
                document.getElementById('logo-preview').src = data.settings.logo_url;
                document.getElementById('logo-preview').style.display = 'block';
            }
            if (data.settings.favicon_url) {
                document.getElementById('favicon-preview').src = data.settings.favicon_url;
                document.getElementById('favicon-preview').style.display = 'block';
            }
        }
    } catch (error) {
        showToast('Failed to load settings', 'error');
        console.error('Error loading settings:', error);
    }
}

// Populate Forms
function populateGeneralForm(settings) {
    const form = document.getElementById('general-form');
    const fields = ['tool_name', 'tool_description', 'company_name', 'company_website', 'support_email', 'support_phone'];

    fields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input && settings[field]) {
            input.value = settings[field];
        }
    });
}

function populateGeneratorForm(settings) {
    const form = document.getElementById('generator-form');
    const fields = ['default_email_count', 'max_email_count', 'default_locale', 'default_persona'];

    fields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input && settings[field]) {
            input.value = settings[field];
        }
    });
}

// Load Generator Config
async function loadGeneratorConfig() {
    try {
        const response = await fetch('/settings/api/settings/generator');
        const data = await response.json();

        if (data.success) {
            const form = document.getElementById('generator-form');
            const config = data.config;

            form.querySelector('[name="number_probability"]').value = config.number_probability || 0.6;
            form.querySelector('[name="year_probability"]').value = config.year_probability || 0.3;
            form.querySelector('[name="year_range_start"]').value = config.year_range_start || 1980;
            form.querySelector('[name="year_range_end"]').value = config.year_range_end || 2005;
            form.querySelector('[name="dedup"]').checked = config.dedup !== false;
        }
    } catch (error) {
        console.error('Error loading generator config:', error);
    }
}

// Load Domains
async function loadDomains() {
    try {
        const response = await fetch('/settings/api/settings/domains');
        const data = await response.json();

        if (data.success) {
            allowedDomains = data.allowed_domains || [];
            customDomains = data.custom_domains || [];

            renderDomains('allowed', allowedDomains);
            renderDomains('custom', customDomains);
        }
    } catch (error) {
        console.error('Error loading domains:', error);
    }
}

function renderDomains(type, domains) {
    const listId = type === 'allowed' ? 'allowed-domains-list' : 'custom-domains-list';
    const list = document.getElementById(listId);

    list.innerHTML = domains.map(domain => `
        <div class="domain-item">
            <span>${domain}</span>
            <button onclick="removeDomain('${type}', '${domain}')">×</button>
        </div>
    `).join('');
}

async function addDomain(type) {
    const inputId = type === 'allowed' ? 'new-allowed-domain' : 'new-custom-domain';
    const input = document.getElementById(inputId);
    const domain = input.value.trim();

    if (!domain) {
        showToast('Please enter a domain name', 'error');
        return;
    }

    if (type === 'allowed') {
        if (!allowedDomains.includes(domain)) {
            allowedDomains.push(domain);
        }
    } else {
        if (!customDomains.includes(domain)) {
            customDomains.push(domain);
        }
    }

    await saveDomains();
    input.value = '';
}

async function removeDomain(type, domain) {
    if (type === 'allowed') {
        allowedDomains = allowedDomains.filter(d => d !== domain);
    } else {
        customDomains = customDomains.filter(d => d !== domain);
    }

    await saveDomains();
}

async function saveDomains() {
    try {
        const response = await fetch('/settings/api/settings/domains', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                allowed_domains: allowedDomains,
                custom_domains: customDomains
            })
        });

        const data = await response.json();

        if (data.success) {
            renderDomains('allowed', allowedDomains);
            renderDomains('custom', customDomains);
            showToast('Domains updated successfully', 'success');
        } else {
            showToast('Failed to update domains', 'error');
        }
    } catch (error) {
        showToast('Error updating domains', 'error');
        console.error('Error:', error);
    }
}

// Load SMTP Settings
async function loadSmtpSettings() {
    try {
        const response = await fetch('/settings/api/settings/smtp');
        const data = await response.json();

        if (data.success) {
            const form = document.getElementById('smtp-form');
            const smtp = data.smtp;

            form.querySelector('[name="smtp_host"]').value = smtp.smtp_host || '';
            form.querySelector('[name="smtp_port"]').value = smtp.smtp_port || 587;
            form.querySelector('[name="smtp_user"]').value = smtp.smtp_user || '';
            form.querySelector('[name="smtp_use_tls"]').checked = smtp.smtp_use_tls !== false;
        }
    } catch (error) {
        console.error('Error loading SMTP settings:', error);
    }
}

// Load Notification Settings
async function loadNotificationSettings() {
    try {
        const response = await fetch('/settings/api/settings/notifications');
        const data = await response.json();

        if (data.success) {
            const form = document.getElementById('notifications-form');
            form.querySelector('[name="enable_email_notifications"]').checked = data.enable_email_notifications !== false;
        }
    } catch (error) {
        console.error('Error loading notification settings:', error);
    }
}

// File Uploads
function setupFileUploads() {
    const logoFile = document.getElementById('logo-file');
    const faviconFile = document.getElementById('favicon-file');

    logoFile.addEventListener('change', (e) => handleFileUpload(e, 'logo'));
    faviconFile.addEventListener('change', (e) => handleFileUpload(e, 'favicon'));
}

async function handleFileUpload(event, type) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const endpoint = type === 'logo' ? '/settings/api/settings/upload-logo' : '/settings/api/settings/upload-favicon';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const previewId = type === 'logo' ? 'logo-preview' : 'favicon-preview';
            const preview = document.getElementById(previewId);
            preview.src = type === 'logo' ? data.logo_url : data.favicon_url;
            preview.style.display = 'block';

            showToast(data.message, 'success');
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast(`Failed to upload ${type}`, 'error');
        console.error('Error:', error);
    }
}

// Form Submissions
function setupForms() {
    // General Form
    document.getElementById('general-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch('/settings/api/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showToast('General settings saved successfully', 'success');
            } else {
                showToast('Failed to save settings', 'error');
            }
        } catch (error) {
            showToast('Error saving settings', 'error');
            console.error('Error:', error);
        }
    });

    // Generator Form
    document.getElementById('generator-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        // Convert checkbox to boolean
        data.dedup = formData.get('dedup') === 'on';

        // Convert numeric strings to numbers
        ['number_probability', 'year_probability', 'year_range_start', 'year_range_end'].forEach(field => {
            if (data[field]) data[field] = parseFloat(data[field]);
        });

        try {
            // Save general settings
            const generalData = {
                default_email_count: parseInt(data.default_email_count),
                max_email_count: parseInt(data.max_email_count),
                default_locale: data.default_locale,
                default_persona: data.default_persona
            };

            await fetch('/settings/api/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(generalData)
            });

            // Save generator config
            const configData = {
                number_probability: data.number_probability,
                year_probability: data.year_probability,
                year_range_start: data.year_range_start,
                year_range_end: data.year_range_end,
                dedup: data.dedup
            };

            const response = await fetch('/settings/api/settings/generator', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configData)
            });

            const result = await response.json();

            if (result.success) {
                showToast('Generator configuration saved successfully', 'success');
            } else {
                showToast('Failed to save generator config', 'error');
            }
        } catch (error) {
            showToast('Error saving generator config', 'error');
            console.error('Error:', error);
        }
    });

    // SMTP Form
    document.getElementById('smtp-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        data.smtp_use_tls = formData.get('smtp_use_tls') === 'on' ? 1 : 0;
        data.smtp_port = parseInt(data.smtp_port);

        try {
            const response = await fetch('/settings/api/settings/smtp', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showToast('SMTP settings saved successfully', 'success');
            } else {
                showToast('Failed to save SMTP settings', 'error');
            }
        } catch (error) {
            showToast('Error saving SMTP settings', 'error');
            console.error('Error:', error);
        }
    });

    // Notifications Form
    document.getElementById('notifications-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = {
            enable_email_notifications: formData.get('enable_email_notifications') === 'on'
        };

        try {
            const response = await fetch('/settings/api/settings/notifications', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showToast('Notification settings saved successfully', 'success');
            } else {
                showToast('Failed to save notification settings', 'error');
            }
        } catch (error) {
            showToast('Error saving notification settings', 'error');
            console.error('Error:', error);
        }
    });
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
