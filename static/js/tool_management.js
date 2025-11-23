/**
 * Tool Management JavaScript
 * Handles admin tool visibility, maintenance, and configuration
 */

let toolsData = [];

// Load tool settings on page load
async function loadToolSettings() {
    try {
        const response = await fetch('/admin/api/tools');
        const tools = await response.json();
        
        if (Array.isArray(tools)) {
            toolsData = tools;
            renderToolManagementCards(tools);
        } else {
            console.error('Invalid tools data:', tools);
            showNotification('Lỗi tải danh sách tools', 'error');
        }
    } catch (error) {
        console.error('Error loading tools:', error);
        showNotification('Không thể tải danh sách tools', 'error');
    }
}

// Render tool management cards
function renderToolManagementCards(tools) {
    const grid = document.getElementById('toolsManagementGrid');
    const template = document.getElementById('toolManagementCardTemplate');
    
    if (!grid || !template) {
        console.error('Grid or template not found');
        return;
    }
    
    // Clear grid
    grid.innerHTML = '';
    
    if (!tools || tools.length === 0) {
        grid.innerHTML = '<div class="loading-indicator"><i class="fas fa-inbox"></i><br>Không có tools nào</div>';
        return;
    }
    
    // Render each tool
    tools.forEach(tool => {
        const card = template.content.cloneNode(true);
        const cardElement = card.querySelector('.tool-management-card');
        
        // Set data attributes
        cardElement.dataset.toolId = tool.tool_id;
        cardElement.dataset.originalVisible = tool.visible;
        cardElement.dataset.originalMaintenance = tool.maintenance_mode;
        cardElement.dataset.originalOrder = tool.order_position;
        cardElement.dataset.originalMessage = tool.maintenance_message || '';
        
        // Set tool info
        card.querySelector('.tool-icon-display').className = `tool-icon-display ${tool.icon_class || 'fas fa-cog'}`;
        card.querySelector('.tool-name-display').textContent = tool.tool_name;
        card.querySelector('.tool-category-display').textContent = `Danh mục: ${tool.tool_category}`;
        
        // Set status badge
        const statusBadge = card.querySelector('.status-badge');
        if (tool.maintenance_mode) {
            statusBadge.textContent = 'Bảo trì';
            statusBadge.className = 'status-badge maintenance';
        } else if (tool.visible) {
            statusBadge.textContent = 'Hiển thị';
            statusBadge.className = 'status-badge visible';
        } else {
            statusBadge.textContent = 'Ẩn';
            statusBadge.className = 'status-badge hidden';
        }
        
        // Set toggle states
        card.querySelector('.tool-visible-toggle').checked = tool.visible;
        card.querySelector('.tool-maintenance-toggle').checked = tool.maintenance_mode;
        card.querySelector('.tool-order-input').value = tool.order_position;
        card.querySelector('.tool-maintenance-msg').value = tool.maintenance_message || '';
        
        // Show/hide maintenance message row
        const maintenanceRow = card.querySelector('.maintenance-message-row');
        maintenanceRow.style.display = tool.maintenance_mode ? 'flex' : 'none';
        
        grid.appendChild(card);
    });
}

// Update tool status when toggles change
function updateToolStatus(toggle) {
    const card = toggle.closest('.tool-management-card');
    const visibleToggle = card.querySelector('.tool-visible-toggle');
    const maintenanceToggle = card.querySelector('.tool-maintenance-toggle');
    const statusBadge = card.querySelector('.status-badge');
    const maintenanceRow = card.querySelector('.maintenance-message-row');
    
    // Update status badge
    if (maintenanceToggle.checked) {
        statusBadge.textContent = 'Bảo trì';
        statusBadge.className = 'status-badge maintenance';
        maintenanceRow.style.display = 'flex';
    } else if (visibleToggle.checked) {
        statusBadge.textContent = 'Hiển thị';
        statusBadge.className = 'status-badge visible';
        maintenanceRow.style.display = 'none';
    } else {
        statusBadge.textContent = 'Ẩn';
        statusBadge.className = 'status-badge hidden';
        maintenanceRow.style.display = 'none';
    }
}

// Save individual tool settings
async function saveToolSettings(button) {
    const card = button.closest('.tool-management-card');
    const toolId = card.dataset.toolId;
    
    const settings = {
        visible: card.querySelector('.tool-visible-toggle').checked,
        maintenance_mode: card.querySelector('.tool-maintenance-toggle').checked,
        maintenance_message: card.querySelector('.tool-maintenance-msg').value,
        order_position: parseInt(card.querySelector('.tool-order-input').value)
    };
    
    try {
        const response = await fetch(`/admin/api/tools/${toolId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Đã lưu cài đặt cho ${toolId}`, 'success');
            
            // Update original data
            card.dataset.originalVisible = settings.visible;
            card.dataset.originalMaintenance = settings.maintenance_mode;
            card.dataset.originalOrder = settings.order_position;
            card.dataset.originalMessage = settings.maintenance_message;
        } else {
            showNotification(result.error || 'Lỗi lưu cài đặt', 'error');
        }
    } catch (error) {
        console.error('Error saving tool settings:', error);
        showNotification('Không thể lưu cài đặt', 'error');
    }
}

// Reset tool settings to original
function resetToolSettings(button) {
    const card = button.closest('.tool-management-card');
    
    card.querySelector('.tool-visible-toggle').checked = card.dataset.originalVisible === 'true';
    card.querySelector('.tool-maintenance-toggle').checked = card.dataset.originalMaintenance === 'true';
    card.querySelector('.tool-order-input').value = card.dataset.originalOrder;
    card.querySelector('.tool-maintenance-msg').value = card.dataset.originalMessage;
    
    // Update status display
    updateToolStatus(card.querySelector('.tool-visible-toggle'));
    
    showNotification('Đã đặt lại cài đặt', 'info');
}

// Save all tool settings
async function saveAllToolSettings() {
    const cards = document.querySelectorAll('.tool-management-card');
    const tools = [];
    
    cards.forEach(card => {
        tools.push({
            tool_id: card.dataset.toolId,
            visible: card.querySelector('.tool-visible-toggle').checked,
            maintenance_mode: card.querySelector('.tool-maintenance-toggle').checked,
            maintenance_message: card.querySelector('.tool-maintenance-msg').value,
            order_position: parseInt(card.querySelector('.tool-order-input').value)
        });
    });
    
    try {
        const response = await fetch('/admin/api/tools/batch-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tools })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Đã lưu cài đặt cho ${result.updated} tools`, 'success');
            loadToolSettings(); // Reload to sync
        } else {
            showNotification(result.error || 'Lỗi lưu cài đặt', 'error');
        }
    } catch (error) {
        console.error('Error batch saving:', error);
        showNotification('Không thể lưu cài đặt', 'error');
    }
}

// Search tools
function searchTools() {
    const query = document.getElementById('toolSearchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.tool-management-card');
    
    cards.forEach(card => {
        const toolName = card.querySelector('.tool-name-display').textContent.toLowerCase();
        const toolId = card.dataset.toolId.toLowerCase();
        
        if (toolName.includes(query) || toolId.includes(query)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('page-tool-management')) {
            loadToolSettings();
        }
    });
} else {
    if (document.getElementById('page-tool-management')) {
        loadToolSettings();
    }
}
