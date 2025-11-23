/**
 * Email Template Manager
 * Handle template selection and generation
 */

class TemplateManager {
    constructor() {
        this.templates = [];
        this.categories = {};
        this.selectedTemplate = null;
        this.init();
    }

    async init() {
        await this.loadTemplates();
        await this.loadCategories();
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates/list');
            const data = await response.json();
            
            if (data.success) {
                this.templates = data.templates;
                this.renderTemplateGrid();
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
        }
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/templates/categories');
            const data = await response.json();
            
            if (data.success) {
                this.categories = data.categories;
                this.renderCategoryFilter();
            }
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }

    renderCategoryFilter() {
        const filterContainer = document.getElementById('templateCategoryFilter');
        if (!filterContainer) return;

        let html = `
            <div class="category-pills">
                <button class="category-pill active" data-category="all" onclick="templateManager.filterByCategory('all')">
                    <i class="fas fa-th"></i> Tất cả
                </button>
        `;

        const categoryIcons = {
            'business': 'fa-briefcase',
            'personal': 'fa-user',
            'vietnamese': 'fa-flag',
            'testing': 'fa-flask',
            'marketing': 'fa-bullhorn',
            'ecommerce': 'fa-shopping-cart',
            'social': 'fa-hashtag'
        };

        for (const [key, name] of Object.entries(this.categories)) {
            const icon = categoryIcons[key] || 'fa-folder';
            html += `
                <button class="category-pill" data-category="${key}" onclick="templateManager.filterByCategory('${key}')">
                    <i class="fas ${icon}"></i> ${name}
                </button>
            `;
        }

        html += '</div>';
        filterContainer.innerHTML = html;
    }

    renderTemplateGrid() {
        const gridContainer = document.getElementById('templateGrid');
        if (!gridContainer) return;

        if (this.templates.length === 0) {
            gridContainer.innerHTML = '<p class="empty-state">Không có template nào</p>';
            return;
        }

        let html = '<div class="template-cards">';

        for (const template of this.templates) {
            const isActive = this.selectedTemplate?.id === template.id ? 'active' : '';
            
            html += `
                <div class="template-card ${isActive}" data-template-id="${template.id}" data-category="${template.category}">
                    <div class="template-card-header">
                        <h4>${template.name}</h4>
                        <span class="template-badge">${this.categories[template.category] || template.category}</span>
                    </div>
                    <div class="template-card-body">
                        <p class="template-description">${template.description}</p>
                        <code class="template-pattern">${template.pattern}</code>
                        <div class="template-examples">
                            <strong>Ví dụ:</strong>
                            ${template.examples.slice(0, 2).map(ex => `<div class="example-email">${ex}</div>`).join('')}
                        </div>
                    </div>
                    <div class="template-card-footer">
                        <div class="template-tags">
                            ${template.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <button class="btn btn-sm btn-primary" onclick="templateManager.selectTemplate('${template.id}')">
                            <i class="fas fa-check"></i> Chọn
                        </button>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        gridContainer.innerHTML = html;
    }

    filterByCategory(category) {
        // Update active pill
        document.querySelectorAll('.category-pill').forEach(pill => {
            pill.classList.remove('active');
            if (pill.dataset.category === category) {
                pill.classList.add('active');
            }
        });

        // Filter cards
        const cards = document.querySelectorAll('.template-card');
        cards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    async selectTemplate(templateId) {
        try {
            const response = await fetch(`/api/templates/${templateId}`);
            const data = await response.json();
            
            if (data.success) {
                this.selectedTemplate = data.template;
                this.renderTemplateForm();
                this.updateSelectedCard(templateId);
                
                if (typeof showNotification !== 'undefined') {
                    showNotification(`Đã chọn template: ${data.template.name}`, 'success');
                }
            }
        } catch (error) {
            console.error('Failed to select template:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification('Lỗi khi chọn template', 'error');
            }
        }
    }

    updateSelectedCard(templateId) {
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('active');
            if (card.dataset.templateId === templateId) {
                card.classList.add('active');
            }
        });
    }

    renderTemplateForm() {
        const formContainer = document.getElementById('templateVariablesForm');
        if (!formContainer || !this.selectedTemplate) return;

        let html = `
            <div class="template-form-header">
                <h3>
                    <i class="fas fa-edit"></i> ${this.selectedTemplate.name}
                </h3>
                <p>${this.selectedTemplate.description}</p>
                <code>${this.selectedTemplate.pattern}</code>
            </div>
            <div class="template-form-body">
        `;

        // Generate input fields for each variable
        for (const variable of this.selectedTemplate.variables) {
            const label = this.getVariableLabel(variable);
            const placeholder = this.getVariablePlaceholder(variable);
            
            html += `
                <div class="form-group">
                    <label for="var_${variable}">
                        <i class="fas fa-tag"></i> ${label}
                    </label>
                    <input 
                        type="text" 
                        id="var_${variable}" 
                        name="${variable}"
                        placeholder="${placeholder}"
                        class="template-variable-input"
                    >
                </div>
            `;
        }

        html += `
                <div class="form-group">
                    <label for="templateCount">
                        <i class="fas fa-hashtag"></i> Số lượng email
                    </label>
                    <input type="number" id="templateCount" value="10" min="1" max="10000">
                </div>
                <button onclick="templateManager.generateFromTemplate()" class="btn btn-success btn-large">
                    <i class="fas fa-magic"></i> Generate từ Template
                </button>
            </div>
        `;

        formContainer.innerHTML = html;
    }

    getVariableLabel(variable) {
        const labels = {
            'firstname': 'Tên',
            'lastname': 'Họ',
            'first_initial': 'Chữ cái đầu tên',
            'ho': 'Họ (Vietnamese)',
            'ten': 'Tên (Vietnamese)',
            'domain': 'Domain',
            'year': 'Năm sinh',
            'department': 'Phòng ban',
            'username': 'Username',
            'handle': 'Handle',
            'shop_name': 'Tên shop',
            'campaign': 'Campaign',
            'segment': 'Segment',
            'id': 'ID',
            'identifier': 'Identifier'
        };
        
        return labels[variable] || variable.charAt(0).toUpperCase() + variable.slice(1);
    }

    getVariablePlaceholder(variable) {
        const placeholders = {
            'firstname': 'John',
            'lastname': 'Smith',
            'ho': 'Nguyen',
            'ten': 'Van',
            'domain': 'gmail.com',
            'year': '1995',
            'department': 'sales',
            'username': 'cooluser',
            'handle': 'johndoe',
            'shop_name': 'techstore',
            'campaign': 'spring_sale',
            'segment': 'vip',
            'id': '12345',
            'identifier': 'abc123'
        };
        
        return placeholders[variable] || 'Enter value';
    }

    async generateFromTemplate() {
        if (!this.selectedTemplate) {
            if (typeof showNotification !== 'undefined') {
                showNotification('Vui lòng chọn template trước', 'warning');
            }
            return;
        }

        // Collect variable values
        const variables = {};
        for (const variable of this.selectedTemplate.variables) {
            const input = document.getElementById(`var_${variable}`);
            if (input) {
                variables[variable] = input.value.trim();
                
                if (!variables[variable]) {
                    if (typeof showNotification !== 'undefined') {
                        showNotification(`Vui lòng nhập ${this.getVariableLabel(variable)}`, 'warning');
                    }
                    return;
                }
            }
        }

        const count = parseInt(document.getElementById('templateCount')?.value || 10);

        if (typeof showNotification !== 'undefined') {
            showNotification('Đang generate emails...', 'info');
        }

        try {
            const response = await fetch('/api/templates/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_id: this.selectedTemplate.id,
                    variables: variables,
                    count: count
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayGeneratedEmails(data.emails);
                
                if (typeof showNotification !== 'undefined') {
                    showNotification(`Đã generate ${data.count} emails thành công!`, 'success');
                }
            } else {
                if (typeof showNotification !== 'undefined') {
                    showNotification(data.error || 'Lỗi khi generate emails', 'error');
                }
            }
        } catch (error) {
            console.error('Generation error:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification('Lỗi kết nối đến server', 'error');
            }
        }
    }

    displayGeneratedEmails(emails) {
        const outputDiv = document.getElementById('templateGeneratedOutput');
        if (!outputDiv) return;

        let html = `
            <div class="output-header">
                <h3>
                    <i class="fas fa-check-circle"></i> Đã generate ${emails.length} emails
                </h3>
                <div class="output-actions">
                    <button onclick="templateManager.copyGeneratedEmails()" class="btn btn-sm btn-primary">
                        <i class="fas fa-copy"></i> Copy All
                    </button>
                    <button onclick="templateManager.downloadGeneratedEmails()" class="btn btn-sm btn-secondary">
                        <i class="fas fa-download"></i> Download
                    </button>
                </div>
            </div>
            <div class="email-list">
                ${emails.map((email, i) => `
                    <div class="email-item">
                        <span class="email-number">${i + 1}.</span>
                        <span class="email-address">${email}</span>
                    </div>
                `).join('')}
            </div>
        `;

        outputDiv.innerHTML = html;
        outputDiv.dataset.emails = JSON.stringify(emails);
    }

    copyGeneratedEmails() {
        const outputDiv = document.getElementById('templateGeneratedOutput');
        if (!outputDiv) return;

        const emails = JSON.parse(outputDiv.dataset.emails || '[]');
        const text = emails.join('\n');

        navigator.clipboard.writeText(text).then(() => {
            if (typeof showNotification !== 'undefined') {
                showNotification('Đã copy danh sách email!', 'success');
            }
        }).catch(err => {
            console.error('Copy failed:', err);
        });
    }

    downloadGeneratedEmails() {
        const outputDiv = document.getElementById('templateGeneratedOutput');
        if (!outputDiv) return;

        const emails = JSON.parse(outputDiv.dataset.emails || '[]');
        const text = emails.join('\n');
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `template_emails_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        if (typeof showNotification !== 'undefined') {
            showNotification('Đã tải xuống danh sách email!', 'success');
        }
    }

    async searchTemplates(query) {
        if (!query || query.trim().length < 2) {
            this.renderTemplateGrid();
            return;
        }

        try {
            const response = await fetch(`/api/templates/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.templates = data.results;
                this.renderTemplateGrid();
            }
        } catch (error) {
            console.error('Search failed:', error);
        }
    }
}

// Initialize global template manager
let templateManager;

document.addEventListener('DOMContentLoaded', () => {
    templateManager = new TemplateManager();
});

// Expose for inline onclick handlers
window.templateManager = templateManager;
