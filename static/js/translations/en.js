/**
 * English Translation
 * Bản dịch Tiếng Anh
 */

const en = {
    // Common
    common: {
        language: 'Language',
        welcome: 'Welcome',
        loading: 'Loading...',
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        confirm: 'Confirm',
        cancel: 'Cancel',
        save: 'Save',
        delete: 'Delete',
        edit: 'Edit',
        add: 'Add',
        search: 'Search',
        filter: 'Filter',
        export: 'Export',
        import: 'Import',
        close: 'Close',
        back: 'Back',
        next: 'Next',
        previous: 'Previous',
        submit: 'Submit',
        reset: 'Reset',
        refresh: 'Refresh',
        download: 'Download',
        upload: 'Upload',
        copy: 'Copy',
        paste: 'Paste',
        select_all: 'Select All',
        deselect_all: 'Deselect All',
        total: 'Total',
        status: 'Status',
        action: 'Action',
        options: 'Options',
        settings: 'Settings',
        help: 'Help',
        about: 'About',
        logout: 'Logout',
        profile: 'Profile',
        dashboard: 'Dashboard',
        notifications: 'Notifications',
        messages: 'Messages'
    },

    // Register Page
    register: {
        title: 'Register',
        subtitle: 'Create Your Account',
        username: 'Username',
        username_placeholder: 'Enter username',
        email: 'Email',
        email_placeholder: 'Enter email address',
        password: 'Password',
        password_placeholder: 'Enter password',
        confirm_password: 'Confirm Password',
        confirm_password_placeholder: 'Re-enter password',
        agree: 'I agree to the',
        terms: 'Terms & Conditions',
        register_button: 'Create Account',
        or: 'OR',
        have_account: 'Already have an account?',
        login: 'Login here',
        success: 'Registration successful!',
        error: 'Registration failed'
    },

    // Login Page
    login: {
        title: 'Login',
        subtitle: 'Professional MMO Tools',
        username: 'Username',
        username_placeholder: 'Enter username',
        password: 'Password',
        password_placeholder: 'Enter password',
        remember_me: 'Remember me',
        forgot_password: 'Forgot password?',
        login_button: 'Login',
        no_account: "Don't have an account?",
        register: 'Register now',
        logging_in: 'Logging in...',
        success: 'Login successful! Redirecting...',
        error: 'Login failed',
        invalid_credentials: 'Invalid username or password',
        network_error: 'Network connection error. Please try again.',
        welcome_back: 'Welcome back!',
        quick_access: 'Quick Access',
        demo_login: 'Demo Login',
        demo_loaded: 'Demo credentials loaded. Click Login to continue.',
        enter_credentials: 'Please enter username and password'
    },

    // Dashboard
    dashboard: {
        welcome: 'Welcome back',
        stats: 'Statistics',
        recent_activity: 'Recent Activity',
        quick_actions: 'Quick Actions',
        tools: 'Tools',
        
        // Stats Cards
        live_emails: 'LIVE Emails',
        die_emails: 'DIE Emails',
        total_validated: 'Total Validated',
        success_rate: 'Success Rate',
        today: 'Today',
        this_week: 'This Week',
        this_month: 'This Month',
        
        // Tool Cards
        email_validator: {
            title: 'Email Validator',
            description: 'Validate emails and classify as LIVE/DIE',
            action: 'Start Validating'
        },
        email_generator: {
            title: 'Email Generator',
            description: 'Generate random or pattern-based email lists',
            action: 'Generate Emails'
        },
        email_extractor: {
            title: 'Email Extractor',
            description: 'Extract emails from text, files or URLs',
            action: 'Extract'
        },
        email_formatter: {
            title: 'Email Formatter',
            description: 'Format and transform email lists',
            action: 'Format'
        },
        fb_checker: {
            title: 'Facebook Checker',
            description: 'Check if emails are linked to Facebook',
            action: 'Check FB'
        },
        pass_2fa_checker: {
            title: '2FA Checker',
            description: 'Check email:password for 2FA and Pages',
            action: 'Check 2FA'
        },
        page_mining: {
            title: 'Page Mining',
            description: 'Mine Page information from Facebook UIDs',
            action: 'Mine'
        },
        email_analyzer: {
            title: 'Email Analyzer',
            description: 'Detailed analysis of email lists',
            action: 'Analyze'
        },
        email_combiner: {
            title: 'Email Combiner',
            description: 'Combine multiple email lists into one',
            action: 'Combine'
        }
    },

    // Email Validator
    validator: {
        title: 'Email Validator',
        input_label: 'Enter email list',
        input_placeholder: 'Enter emails, one per line...\n\nExample:\nemail1@gmail.com\nemail2@yahoo.com\nemail3@hotmail.com',
        options: 'Options',
        check_mx: 'Check MX Record',
        check_smtp: 'Check SMTP',
        check_disposable: 'Check Disposable',
        check_fb_compat: 'Check FB Compatible',
        use_cache: 'Use Cache',
        max_workers: 'Workers',
        validate_button: 'Validate Now',
        validating: 'Validating...',
        results: 'Results',
        live: 'LIVE',
        die: 'DIE',
        unknown: 'UNKNOWN',
        export_live: 'Export LIVE',
        export_die: 'Export DIE',
        export_all: 'Export All',
        clear: 'Clear',
        stats: {
            total: 'Total',
            live: 'LIVE',
            die: 'DIE',
            unknown: 'Unknown',
            can_receive_code: 'Can Receive Code',
            processing_time: 'Processing Time'
        }
    },

    // Email Generator
    generator: {
        title: 'Email Generator',
        email_type: 'Email Type',
        random: 'Random',
        pattern: 'Pattern',
        base_text: 'Base Text',
        base_text_placeholder: 'Enter base text (for Pattern type)',
        total: 'Total',
        domains: 'Domains',
        domains_placeholder: 'gmail.com, yahoo.com, hotmail.com',
        char_type: 'Character Type',
        lowercase: 'Lowercase',
        uppercase: 'UPPERCASE',
        mixed: 'Mixed',
        number_type: 'Number Type',
        prefix: 'Prefix',
        suffix: 'Suffix',
        random_pos: 'Random Position',
        generate_button: 'Generate Emails',
        generating: 'Generating...',
        results: 'Results',
        generated: 'Generated',
        export: 'Export List'
    },

    // Email Extractor
    extractor: {
        title: 'Email Extractor',
        input_label: 'Enter text or URL',
        input_placeholder: 'Paste text containing emails or enter URL...',
        options: 'Options',
        remove_dups: 'Remove Duplicates',
        filter_domains: 'Filter by Domains',
        filter_pattern: 'Filter by Pattern',
        extract_button: 'Extract',
        extracting: 'Extracting...',
        results: 'Results',
        found: 'Found',
        export: 'Export List'
    },

    // Facebook Checker
    fb_checker: {
        title: 'Facebook Checker',
        input_label: 'Enter email list',
        input_placeholder: 'Enter emails, one per line...',
        options: 'Options',
        api_type: 'API Type',
        random: 'Random',
        proxy_config: 'Proxy Config',
        max_workers: 'Workers',
        start_from: 'Start From',
        check_code_68: 'Check Code 6/8',
        check_button: 'Check FB',
        checking: 'Checking...',
        results: 'Results',
        linked: 'Linked',
        hidden_linked: 'Hidden Linked',
        not_linked: 'Not Linked',
        error: 'Error',
        code6: 'Code 6 Chars',
        code8: 'Code 8 Chars',
        export_linked: 'Export Linked',
        export_not_linked: 'Export Not Linked'
    },

    // 2FA Checker
    twofa_checker: {
        title: '2FA & Page Checker',
        input_label: 'Enter email:password list',
        input_placeholder: 'Enter email:password, one per line...\n\nExample:\nemail1@gmail.com:password123\nemail2@yahoo.com:mypass456',
        options: 'Options',
        api_type: 'API Type',
        password_pattern: 'Password Pattern',
        validate_pattern: 'Validate Pattern',
        check_button: 'Check 2FA',
        checking: 'Checking...',
        results: 'Results',
        hit_2fa: 'Has 2FA',
        has_page: 'Has Page',
        not_hit: 'Not Hit',
        error: 'Error',
        export_hit: 'Export With 2FA',
        export_page: 'Export With Page'
    },

    // Page Mining
    page_mining: {
        title: 'Page ID Mining',
        input_label: 'Enter UID list',
        input_placeholder: 'Enter Facebook UIDs, one per line...\n\nExample:\n100001234567890\n100009876543210',
        options: 'Options',
        filter_has_ads: 'Filter Has Ads',
        filter_country: 'Filter by Country',
        filter_verified: 'Filter Verified',
        mine_button: 'Start Mining',
        mining: 'Mining...',
        results: 'Results',
        pages_found: 'Pages Found',
        emails_collected: 'Emails Collected',
        export_pages: 'Export Pages',
        export_emails: 'Export Emails'
    },

    // Admin Panel
    admin: {
        title: 'System Administration',
        overview: 'Overview',
        users: 'User Management',
        vip: 'VIP Management',
        permissions: 'Permissions',
        settings: 'System Settings',
        logs: 'Activity Logs',
        backup: 'Data Backup',
        payments: 'Payment History',
        
        // Stats
        stats: {
            total_users: 'Total Users',
            active_users: 'Active Users',
            vip_users: 'VIP Members',
            revenue: 'Revenue',
            operations: 'Operations Today'
        },
        
        // VIP Levels
        vip_levels: {
            free: 'Free',
            basic: 'Basic',
            pro: 'Professional',
            enterprise: 'Enterprise'
        },
        
        // Actions
        add_user: 'Add User',
        edit_user: 'Edit User',
        delete_user: 'Delete User',
        upgrade_vip: 'Upgrade VIP',
        view_logs: 'View Logs',
        export_data: 'Export Data',
        import_data: 'Import Data'
    },

    // VIP System
    vip: {
        title: 'VIP Plans',
        current_plan: 'Current Plan',
        upgrade: 'Upgrade',
        features: 'Features',
        limits: 'Limits',
        price: 'Price',
        per_month: '/month',
        subscribe: 'Subscribe',
        
        free: {
            name: 'Free',
            validations: '100 validations/day',
            generations: '50 generations/day',
            support: 'Community support'
        },
        basic: {
            name: 'Basic',
            validations: '1,000 validations/day',
            generations: '500 generations/day',
            support: 'Email support'
        },
        pro: {
            name: 'Professional',
            validations: '10,000 validations/day',
            generations: '5,000 generations/day',
            support: 'Priority support'
        },
        enterprise: {
            name: 'Enterprise',
            validations: 'Unlimited',
            generations: 'Unlimited',
            support: '24/7 support'
        }
    },

    // Notifications
    notifications: {
        success: {
            saved: 'Saved successfully',
            deleted: 'Deleted successfully',
            updated: 'Updated successfully',
            uploaded: 'Uploaded successfully',
            copied: 'Copied to clipboard',
            exported: 'Exported successfully'
        },
        error: {
            general: 'An error occurred',
            network: 'Network connection error',
            invalid_input: 'Invalid input data',
            not_found: 'Not found',
            permission_denied: 'You do not have permission to perform this action',
            server_error: 'Server error'
        },
        warning: {
            unsaved_changes: 'You have unsaved changes',
            confirm_delete: 'Are you sure you want to delete?',
            limit_reached: 'Limit reached'
        }
    },

    // Tooltips
    tooltips: {
        click_to_copy: 'Click to copy',
        click_to_download: 'Click to download',
        click_to_edit: 'Click to edit',
        click_to_delete: 'Click to delete',
        drag_to_upload: 'Drag and drop files here',
        max_file_size: 'Maximum file size',
        allowed_formats: 'Allowed formats'
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = en;
}
