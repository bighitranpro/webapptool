/**
 * Tool Visibility Manager
 * Dynamically shows/hides tools based on admin configuration
 */

// Tool ID to modal ID mapping
const toolModalMapping = {
    'email_validator': 'validatorModal',
    'email_generator': 'generatorModal',
    'email_extractor': 'extractorModal',
    'fb_linked_checker': 'fbLinkedModal',
    'check_2fa': 'check2faModal',
    'page_mining': 'miningModal',
    'email_filter': 'filterModal',
    'email_analyzer': 'analyzerModal',
    'email_deduplicator': 'deduplicatorModal'
};

// Load tool visibility settings
async function loadToolVisibility() {
    try {
        const response = await fetch('/api/tools/visible');
        const data = await response.json();
        
        if (data.tools && Array.isArray(data.tools)) {
            applyToolVisibility(data.tools);
        }
    } catch (error) {
        console.error('Error loading tool visibility:', error);
        // On error, show all tools (fail-safe)
    }
}

// Apply visibility settings to tool cards
function applyToolVisibility(tools) {
    const toolsGrid = document.querySelector('.tools-grid');
    if (!toolsGrid) return;
    
    // Create a Set of visible tool IDs
    const visibleTools = new Set(
        tools
            .filter(tool => !tool.maintenance && tool.accessible)
            .map(tool => tool.tool_id)
    );
    
    // Find all tool cards
    const toolCards = toolsGrid.querySelectorAll('.tool-card');
    
    toolCards.forEach(card => {
        // Find which tool this card represents by checking the onclick attribute
        const onclickAttr = card.getAttribute('onclick');
        if (!onclickAttr) return;
        
        // Extract modal ID from onclick (e.g., "openModal('validatorModal')")
        const match = onclickAttr.match(/openModal\('([^']+)'\)/);
        if (!match) return;
        
        const modalId = match[1];
        
        // Find corresponding tool_id
        const toolId = Object.keys(toolModalMapping).find(
            key => toolModalMapping[key] === modalId
        );
        
        if (!toolId) return;
        
        // Check if tool is visible
        if (visibleTools.has(toolId)) {
            card.style.display = 'block';
            card.classList.remove('tool-hidden');
        } else {
            card.style.display = 'none';
            card.classList.add('tool-hidden');
        }
    });
    
    // Show maintenance badges for tools in maintenance
    const maintenanceTools = tools.filter(tool => tool.maintenance);
    maintenanceTools.forEach(tool => {
        const modalId = toolModalMapping[tool.tool_id];
        if (!modalId) return;
        
        const card = Array.from(toolCards).find(c => {
            const onclick = c.getAttribute('onclick');
            return onclick && onclick.includes(modalId);
        });
        
        if (card) {
            // Add maintenance badge
            addMaintenanceBadge(card, tool.maintenance_message || 'Đang bảo trì');
        }
    });
}

// Add maintenance badge to tool card
function addMaintenanceBadge(card, message) {
    // Check if badge already exists
    if (card.querySelector('.maintenance-badge')) return;
    
    const badge = document.createElement('div');
    badge.className = 'maintenance-badge';
    badge.innerHTML = `
        <i class="fas fa-wrench"></i>
        <span>${message}</span>
    `;
    
    // Add to card footer
    const footer = card.querySelector('.tool-card-footer');
    if (footer) {
        footer.appendChild(badge);
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadToolVisibility);
} else {
    loadToolVisibility();
}

// Refresh visibility every 5 minutes
setInterval(loadToolVisibility, 5 * 60 * 1000);
