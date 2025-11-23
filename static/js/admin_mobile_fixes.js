/**
 * Admin Mobile Fixes
 * - Mobile navigation toggle
 * - Chart initialization fixes
 * - Responsive behavior
 */

(function() {
    'use strict';
    
    // Create mobile menu button and overlay
    function initMobileMenu() {
        // Check if already initialized
        if (document.querySelector('.mobile-menu-btn')) {
            return;
        }
        
        // Create mobile menu button
        const menuBtn = document.createElement('button');
        menuBtn.className = 'mobile-menu-btn';
        menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        menuBtn.setAttribute('aria-label', 'Toggle menu');
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        
        // Add to DOM
        document.body.appendChild(menuBtn);
        document.body.appendChild(overlay);
        
        // Get sidebar
        const sidebar = document.querySelector('.sidebar');
        
        // Toggle menu function
        function toggleMenu() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.classList.toggle('overflow-hidden');
            
            // Update button icon
            const icon = menuBtn.querySelector('i');
            if (sidebar.classList.contains('active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        }
        
        // Close menu function
        function closeMenu() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('overflow-hidden');
            menuBtn.querySelector('i').className = 'fas fa-bars';
        }
        
        // Event listeners
        menuBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', closeMenu);
        
        // Close menu when clicking nav items on mobile
        const navItems = sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    closeMenu();
                }
            });
        });
        
        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth > 768) {
                    closeMenu();
                }
            }, 250);
        });
    }
    
    // Fix chart initialization
    function fixCharts() {
        // Wait for Chart.js to load
        if (typeof Chart === 'undefined') {
            console.log('Chart.js not loaded yet, retrying...');
            setTimeout(fixCharts, 100);
            return;
        }
        
        // Set default Chart.js config
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.color = '#b0b3c1';
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Ensure canvases have proper dimensions
        const canvases = document.querySelectorAll('.chart-container canvas');
        canvases.forEach(canvas => {
            const container = canvas.closest('.chart-container');
            if (container) {
                // Set canvas dimensions based on container
                const width = container.clientWidth - 40; // Subtract padding
                const height = 280;
                
                canvas.style.width = width + 'px';
                canvas.style.height = height + 'px';
                canvas.width = width;
                canvas.height = height;
            }
        });
        
        console.log('✅ Charts fixed');
    }
    
    // Fix page navigation
    function fixPageNavigation() {
        // Ensure loadPage function exists
        if (typeof window.loadPage !== 'function') {
            window.loadPage = function(pageName) {
                console.log('Loading page:', pageName);
                
                // Hide all pages
                const pages = document.querySelectorAll('.admin-page');
                pages.forEach(page => {
                    page.classList.remove('active');
                    page.style.display = 'none';
                });
                
                // Show selected page
                const targetPage = document.getElementById('page-' + pageName);
                if (targetPage) {
                    targetPage.classList.add('active');
                    targetPage.style.display = 'block';
                }
                
                // Update nav items
                const navItems = document.querySelectorAll('.nav-item');
                navItems.forEach(item => {
                    item.classList.remove('active');
                    if (item.getAttribute('data-page') === pageName) {
                        item.classList.add('active');
                    }
                });
                
                // Update page title
                const pageTitle = document.getElementById('pageTitle');
                if (pageTitle) {
                    const pageTitles = {
                        'overview': 'Tổng quan',
                        'users': 'Quản lý Users',
                        'vip': 'Quản lý VIP',
                        'settings': 'Cài đặt',
                        'logs': 'Activity Logs',
                        'tool-management': 'Quản lý Tools'
                    };
                    pageTitle.textContent = pageTitles[pageName] || 'Dashboard';
                }
            };
        }
        
        // Set up nav item click handlers
        const navItems = document.querySelectorAll('.nav-item[data-page]');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const pageName = item.getAttribute('data-page');
                if (pageName) {
                    window.loadPage(pageName);
                }
            });
        });
    }
    
    // Fix stats display
    function fixStatsDisplay() {
        // Add loading state to stat cards
        const statCards = document.querySelectorAll('.stat-value');
        statCards.forEach(card => {
            if (card.textContent === '0' || card.textContent === '') {
                card.innerHTML = '<div class="loading-spinner"></div>';
            }
        });
    }
    
    // Initialize when DOM is ready
    function init() {
        console.log('🔧 Initializing admin mobile fixes...');
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        // Initialize features
        initMobileMenu();
        fixPageNavigation();
        fixStatsDisplay();
        
        // Fix charts after a short delay to ensure Chart.js is loaded
        setTimeout(fixCharts, 500);
        
        // Re-fix charts when window is resized
        let chartResizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(chartResizeTimer);
            chartResizeTimer = setTimeout(fixCharts, 250);
        });
        
        console.log('✅ Admin mobile fixes initialized');
    }
    
    // Start initialization
    init();
    
})();
