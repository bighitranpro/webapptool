/**
 * Admin Panel Mobile Enhancement
 * Handles mobile-specific interactions and fixes
 */

(function() {
    'use strict';

    // Mobile Detection
    const isMobile = () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
            || window.innerWidth <= 768;
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        if (isMobile()) {
            initMobileFeatures();
        }
        
        // Re-check on resize
        window.addEventListener('resize', debounce(function() {
            if (isMobile()) {
                initMobileFeatures();
            } else {
                cleanupMobileFeatures();
            }
        }, 250));
    });

    function initMobileFeatures() {
        setupMobileSidebar();
        setupTouchGestures();
        setupMobileTable();
        setupMobileModals();
        setupMobileForms();
        fixIOSScrolling();
        addMobileClasses();
    }

    function cleanupMobileFeatures() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar) {
            sidebar.classList.remove('active');
        }
        if (overlay) {
            overlay.remove();
        }
        
        document.body.classList.remove('mobile-view');
    }

    // Mobile Sidebar
    function setupMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        
        if (!sidebar || !sidebarToggle) return;

        // Create overlay if it doesn't exist
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }

        // Toggle sidebar
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        });

        // Close on overlay click
        overlay.addEventListener('click', function() {
            closeSidebar();
        });

        // Close on navigation item click
        const navItems = sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                if (isMobile()) {
                    closeSidebar();
                }
            });
        });

        // Swipe gestures
        let touchStartX = 0;
        let touchEndX = 0;

        document.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        document.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchEndX - touchStartX;

            // Swipe right from left edge to open
            if (touchStartX < 50 && diff > swipeThreshold) {
                openSidebar();
            }
            // Swipe left to close
            else if (sidebar.classList.contains('active') && diff < -swipeThreshold) {
                closeSidebar();
            }
        }

        function toggleSidebar() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.classList.toggle('sidebar-open');
        }

        function openSidebar() {
            sidebar.classList.add('active');
            overlay.classList.add('active');
            document.body.classList.add('sidebar-open');
        }

        function closeSidebar() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
        }

        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                closeSidebar();
            }
        });
    }

    // Touch Gestures
    function setupTouchGestures() {
        // Add visual feedback on touch
        const touchableElements = document.querySelectorAll('.btn, .nav-item, .stat-card, .btn-action');
        
        touchableElements.forEach(el => {
            el.addEventListener('touchstart', function() {
                this.style.opacity = '0.7';
            }, { passive: true });
            
            el.addEventListener('touchend', function() {
                this.style.opacity = '1';
            }, { passive: true });
            
            el.addEventListener('touchcancel', function() {
                this.style.opacity = '1';
            }, { passive: true });
        });
    }

    // Mobile Table Enhancements
    function setupMobileTable() {
        const tables = document.querySelectorAll('.data-table');
        
        tables.forEach(table => {
            // Add horizontal scroll indicator
            const container = table.closest('.table-container');
            if (container) {
                const scrollIndicator = document.createElement('div');
                scrollIndicator.className = 'scroll-indicator';
                scrollIndicator.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Swipe to view more';
                scrollIndicator.style.cssText = `
                    text-align: center;
                    padding: 10px;
                    color: var(--text-muted);
                    font-size: 12px;
                    background: rgba(243, 156, 18, 0.1);
                    border-radius: 8px;
                    margin-bottom: 10px;
                `;
                
                if (table.scrollWidth > container.clientWidth) {
                    container.insertBefore(scrollIndicator, table);
                    
                    // Hide indicator after first scroll
                    container.addEventListener('scroll', function() {
                        scrollIndicator.style.display = 'none';
                    }, { once: true, passive: true });
                }
            }
        });
    }

    // Mobile Modal Improvements
    function setupMobileModals() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            // Prevent body scroll when modal is open
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.attributeName === 'class') {
                        if (modal.classList.contains('show')) {
                            document.body.style.overflow = 'hidden';
                        } else {
                            document.body.style.overflow = '';
                        }
                    }
                });
            });
            
            observer.observe(modal, { attributes: true });
            
            // Close on backdrop click
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeModal(modal);
                }
            });
            
            // Prevent modal content clicks from closing
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        });
    }

    // Mobile Form Enhancements
    function setupMobileForms() {
        // Auto-scroll to focused input
        const inputs = document.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                setTimeout(() => {
                    this.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 300);
            }, { passive: true });
        });

        // Prevent zoom on input focus (iOS)
        const meta = document.querySelector('meta[name="viewport"]');
        if (meta) {
            const originalContent = meta.content;
            
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    meta.content = originalContent + ', user-scalable=no';
                }, { passive: true });
                
                input.addEventListener('blur', function() {
                    meta.content = originalContent;
                }, { passive: true });
            });
        }
    }

    // Fix iOS Scrolling Issues
    function fixIOSScrolling() {
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        
        if (isIOS) {
            // Fix rubber band scrolling
            document.body.addEventListener('touchmove', function(e) {
                const target = e.target.closest('.table-container, .modal-content, .sidebar');
                if (!target) {
                    return;
                }
                
                const scrollTop = target.scrollTop;
                const scrollHeight = target.scrollHeight;
                const height = target.clientHeight;
                const delta = e.touches[0].clientY - touchStartY;
                
                if ((scrollTop <= 0 && delta > 0) || 
                    (scrollTop + height >= scrollHeight && delta < 0)) {
                    e.preventDefault();
                }
            }, { passive: false });
        }
    }

    // Add Mobile-Specific Classes
    function addMobileClasses() {
        document.body.classList.add('mobile-view');
        
        // Mark charts for mobile optimization
        const charts = document.querySelectorAll('canvas');
        charts.forEach(chart => {
            chart.parentElement.classList.add('mobile-chart');
        });
    }

    // Utility: Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Utility: Close modal
    function closeModal(modal) {
        modal.classList.remove('show');
    }

    // Show loading indicator
    window.showMobileLoading = function(message = 'Loading...') {
        const loading = document.createElement('div');
        loading.className = 'mobile-loading';
        loading.innerHTML = `
            <div class="spinner"></div>
            <div>${message}</div>
        `;
        document.body.appendChild(loading);
        return loading;
    };

    // Hide loading indicator
    window.hideMobileLoading = function() {
        const loading = document.querySelector('.mobile-loading');
        if (loading) {
            loading.remove();
        }
    };

    // Show mobile toast
    window.showMobileToast = function(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    // Export for global use
    window.AdminMobile = {
        isMobile,
        showLoading: window.showMobileLoading,
        hideLoading: window.hideMobileLoading,
        showToast: window.showMobileToast
    };

})();

// CSS Animation for toast slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
`;
document.head.appendChild(style);
