/**
 * Bản dịch Tiếng Việt
 * Vietnamese Translation
 */

const vi = {
    // Common
    common: {
        language: 'Ngôn ngữ',
        welcome: 'Chào mừng',
        loading: 'Đang tải...',
        success: 'Thành công',
        error: 'Lỗi',
        warning: 'Cảnh báo',
        confirm: 'Xác nhận',
        cancel: 'Hủy',
        save: 'Lưu',
        delete: 'Xóa',
        edit: 'Sửa',
        add: 'Thêm',
        search: 'Tìm kiếm',
        filter: 'Lọc',
        export: 'Xuất',
        import: 'Nhập',
        close: 'Đóng',
        back: 'Quay lại',
        next: 'Tiếp theo',
        previous: 'Trước',
        submit: 'Gửi',
        reset: 'Đặt lại',
        refresh: 'Làm mới',
        download: 'Tải xuống',
        upload: 'Tải lên',
        copy: 'Sao chép',
        paste: 'Dán',
        select_all: 'Chọn tất cả',
        deselect_all: 'Bỏ chọn tất cả',
        total: 'Tổng',
        status: 'Trạng thái',
        action: 'Hành động',
        options: 'Tùy chọn',
        settings: 'Cài đặt',
        help: 'Trợ giúp',
        about: 'Giới thiệu',
        logout: 'Đăng xuất',
        profile: 'Hồ sơ',
        dashboard: 'Bảng điều khiển',
        notifications: 'Thông báo',
        messages: 'Tin nhắn'
    },

    // Register Page
    register: {
        title: 'Đăng Ký',
        subtitle: 'Tạo tài khoản của bạn',
        username: 'Tên đăng nhập',
        username_placeholder: 'Nhập tên đăng nhập',
        email: 'Email',
        email_placeholder: 'Nhập địa chỉ email',
        password: 'Mật khẩu',
        password_placeholder: 'Nhập mật khẩu',
        confirm_password: 'Xác nhận mật khẩu',
        confirm_password_placeholder: 'Nhập lại mật khẩu',
        agree: 'Tôi đồng ý với',
        terms: 'Điều khoản & Điều kiện',
        register_button: 'Tạo tài khoản',
        or: 'HOẶC',
        have_account: 'Đã có tài khoản?',
        login: 'Đăng nhập tại đây',
        success: 'Đăng ký thành công!',
        error: 'Đăng ký thất bại'
    },

    // Login Page
    login: {
        title: 'Đăng Nhập',
        subtitle: 'Công cụ MMO chuyên nghiệp',
        username: 'Tên đăng nhập',
        username_placeholder: 'Nhập tên đăng nhập',
        password: 'Mật khẩu',
        password_placeholder: 'Nhập mật khẩu',
        remember_me: 'Ghi nhớ đăng nhập',
        forgot_password: 'Quên mật khẩu?',
        login_button: 'Đăng Nhập',
        no_account: 'Chưa có tài khoản?',
        register: 'Đăng ký ngay',
        logging_in: 'Đang đăng nhập...',
        success: 'Đăng nhập thành công! Đang chuyển hướng...',
        error: 'Đăng nhập thất bại',
        invalid_credentials: 'Tên đăng nhập hoặc mật khẩu không đúng',
        network_error: 'Lỗi kết nối mạng. Vui lòng thử lại.',
        welcome_back: 'Chào mừng trở lại!',
        quick_access: 'Truy cập nhanh',
        demo_login: 'Demo Login',
        demo_loaded: 'Đã tải thông tin demo. Nhấn Đăng nhập để tiếp tục.',
        enter_credentials: 'Vui lòng nhập tên đăng nhập và mật khẩu'
    },

    // Dashboard
    dashboard: {
        title: 'Bảng điều khiển',
        welcome: 'Chào mừng trở lại',
        analytics: 'Thống kê',
        stats: 'Thống kê',
        recent_activity: 'Hoạt động gần đây',
        quick_actions: 'Thao tác nhanh',
        tools: 'Công cụ',
        search_placeholder: 'Tìm kiếm công cụ, lệnh hoặc trợ giúp...',
        
        // Welcome Stats
        total_actions: 'Hành động',
        logins: 'Đăng nhập',
        member_since: 'Thành viên từ',
        
        // Stats Cards
        live_emails: 'Email LIVE',
        die_emails: 'Email DIE',
        total_validated: 'Đã kiểm tra',
        total_processed: 'Tổng đã xử lý',
        can_receive_code: 'Nhận được mã',
        success_rate: 'Tỷ lệ thành công',
        failure_rate: 'Tỷ lệ thất bại',
        '2fa_ready': 'Sẵn sàng 2FA',
        last_7_days: '7 ngày qua',
        today: 'Hôm nay',
        this_week: 'Tuần này',
        this_month: 'Tháng này',
        
        // Tool Stats
        accuracy: 'Chính xác',
        fast: 'Nhanh',
        unlimited: 'Không giới hạn',
        multi_domain: 'Nhiều tên miền',
        secure: 'Bảo mật',
        pages: 'Trang',
        advanced_tool: 'Nâng cao',
        multi_source: 'Nhiều nguồn',
        smart: 'Thông minh',
        
        // Badges
        popular: 'Phổ biến',
        hot: 'Nóng',
        view_all: 'Xem tất cả',
        
        // Activity
        activity: {
            validation_completed: 'Hoàn thành kiểm tra Email',
            validation_details: 'Đã kiểm tra 150 email với 92% LIVE • 2 phút trước',
            emails_generated: 'Đã tạo Email',
            generation_details: 'Tạo 500 email ngẫu nhiên trên 4 tên miền • 15 phút trước',
            fb_check: 'Kiểm tra liên kết FB',
            fb_check_details: 'Đã kiểm tra 80 email, tìm thấy 25 tài khoản liên kết • 1 giờ trước'
        },
        
        // Tool Cards
        email_validator: {
            title: 'Kiểm tra Email',
            description: 'Kiểm tra tính hợp lệ của email, phân loại LIVE/DIE',
            action: 'Bắt đầu kiểm tra'
        },
        email_generator: {
            title: 'Tạo Email',
            description: 'Tạo danh sách email ngẫu nhiên hoặc theo mẫu',
            action: 'Tạo email'
        },
        email_extractor: {
            title: 'Trích xuất Email',
            description: 'Trích xuất email từ văn bản, file hoặc URL',
            action: 'Trích xuất'
        },
        email_formatter: {
            title: 'Định dạng Email',
            description: 'Chuyển đổi và định dạng danh sách email',
            action: 'Định dạng'
        },
        fb_checker: {
            title: 'Kiểm tra Facebook',
            description: 'Kiểm tra email có liên kết với Facebook',
            action: 'Kiểm tra FB'
        },
        pass_2fa_checker: {
            title: 'Kiểm tra 2FA',
            description: 'Kiểm tra email:password có 2FA và Page',
            action: 'Kiểm tra 2FA'
        },
        page_mining: {
            title: 'Mining Page',
            description: 'Khai thác thông tin Page từ UID Facebook',
            action: 'Mining'
        },
        email_analyzer: {
            title: 'Phân tích Email',
            description: 'Phân tích chi tiết danh sách email',
            action: 'Phân tích'
        },
        email_combiner: {
            title: 'Gộp Email',
            description: 'Gộp nhiều danh sách email thành một',
            action: 'Gộp'
        }
    },

    // Email Validator
    validator: {
        title: 'Kiểm tra Email',
        input_label: 'Nhập danh sách email',
        input_placeholder: 'Nhập email, mỗi email một dòng...\n\nVí dụ:\nemail1@gmail.com\nemail2@yahoo.com\nemail3@hotmail.com',
        options: 'Tùy chọn',
        check_mx: 'Kiểm tra MX Record',
        check_smtp: 'Kiểm tra SMTP',
        check_disposable: 'Kiểm tra email tạm',
        check_fb_compat: 'Kiểm tra tương thích FB',
        use_cache: 'Sử dụng cache',
        max_workers: 'Số luồng',
        validate_button: 'Kiểm tra ngay',
        validating: 'Đang kiểm tra...',
        results: 'Kết quả',
        live: 'LIVE',
        die: 'DIE',
        unknown: 'KHÔNG RÕ',
        export_live: 'Xuất LIVE',
        export_die: 'Xuất DIE',
        export_all: 'Xuất tất cả',
        clear: 'Xóa',
        stats: {
            total: 'Tổng số',
            live: 'LIVE',
            die: 'DIE',
            unknown: 'Không rõ',
            can_receive_code: 'Nhận được mã',
            processing_time: 'Thời gian xử lý'
        }
    },

    // Email Generator
    generator: {
        title: 'Tạo Email',
        email_type: 'Loại email',
        random: 'Ngẫu nhiên',
        pattern: 'Theo mẫu',
        base_text: 'Văn bản gốc',
        base_text_placeholder: 'Nhập văn bản gốc (cho loại Pattern)',
        total: 'Số lượng',
        domains: 'Tên miền',
        domains_placeholder: 'gmail.com, yahoo.com, hotmail.com',
        char_type: 'Loại ký tự',
        lowercase: 'Chữ thường',
        uppercase: 'Chữ HOA',
        mixed: 'Hỗn hợp',
        number_type: 'Kiểu số',
        prefix: 'Tiền tố',
        suffix: 'Hậu tố',
        random_pos: 'Vị trí ngẫu nhiên',
        generate_button: 'Tạo Email',
        generating: 'Đang tạo...',
        results: 'Kết quả',
        generated: 'Đã tạo',
        export: 'Xuất danh sách'
    },

    // Email Extractor
    extractor: {
        title: 'Trích xuất Email',
        input_label: 'Nhập văn bản hoặc URL',
        input_placeholder: 'Dán văn bản chứa email hoặc nhập URL...',
        options: 'Tùy chọn',
        remove_dups: 'Xóa trùng lặp',
        filter_domains: 'Lọc theo tên miền',
        filter_pattern: 'Lọc theo mẫu',
        extract_button: 'Trích xuất',
        extracting: 'Đang trích xuất...',
        results: 'Kết quả',
        found: 'Tìm thấy',
        export: 'Xuất danh sách'
    },

    // Facebook Checker
    fb_checker: {
        title: 'Kiểm tra Facebook',
        input_label: 'Nhập danh sách email',
        input_placeholder: 'Nhập email, mỗi email một dòng...',
        options: 'Tùy chọn',
        api_type: 'Loại API',
        random: 'Ngẫu nhiên',
        proxy_config: 'Cấu hình Proxy',
        max_workers: 'Số luồng',
        start_from: 'Bắt đầu từ',
        check_code_68: 'Kiểm tra mã 6/8',
        check_button: 'Kiểm tra FB',
        checking: 'Đang kiểm tra...',
        results: 'Kết quả',
        linked: 'Có liên kết',
        hidden_linked: 'Liên kết ẩn',
        not_linked: 'Không liên kết',
        error: 'Lỗi',
        code6: 'Mã 6 ký tự',
        code8: 'Mã 8 ký tự',
        export_linked: 'Xuất có liên kết',
        export_not_linked: 'Xuất không liên kết'
    },

    // 2FA Checker
    twofa_checker: {
        title: 'Kiểm tra 2FA & Page',
        input_label: 'Nhập danh sách email:password',
        input_placeholder: 'Nhập email:password, mỗi cặp một dòng...\n\nVí dụ:\nemail1@gmail.com:password123\nemail2@yahoo.com:mypass456',
        options: 'Tùy chọn',
        api_type: 'Loại API',
        password_pattern: 'Mẫu mật khẩu',
        validate_pattern: 'Xác thực mẫu',
        check_button: 'Kiểm tra 2FA',
        checking: 'Đang kiểm tra...',
        results: 'Kết quả',
        hit_2fa: 'Có 2FA',
        has_page: 'Có Page',
        not_hit: 'Không hit',
        error: 'Lỗi',
        export_hit: 'Xuất có 2FA',
        export_page: 'Xuất có Page'
    },

    // Page Mining
    page_mining: {
        title: 'Mining ID Page',
        input_label: 'Nhập danh sách UID',
        input_placeholder: 'Nhập UID Facebook, mỗi UID một dòng...\n\nVí dụ:\n100001234567890\n100009876543210',
        options: 'Tùy chọn',
        filter_has_ads: 'Lọc có quảng cáo',
        filter_country: 'Lọc theo quốc gia',
        filter_verified: 'Lọc đã xác minh',
        mine_button: 'Bắt đầu Mining',
        mining: 'Đang mining...',
        results: 'Kết quả',
        pages_found: 'Page tìm thấy',
        emails_collected: 'Email thu thập',
        export_pages: 'Xuất Pages',
        export_emails: 'Xuất Emails'
    },

    // Sidebar
    sidebar: {
        main: 'CHÍNH',
        email_tools: 'CÔNG CỤ EMAIL',
        facebook_tools: 'CÔNG CỤ FACEBOOK',
        advanced: 'NÂNG CAO',
        filter: 'Lọc',
        deduplicator: 'Loại bỏ trùng'
    },

    // Admin Panel
    admin: {
        title: 'Quản trị hệ thống',
        overview: 'Tổng quan',
        users: 'Quản lý người dùng',
        vip: 'Quản lý VIP',
        permissions: 'Phân quyền',
        settings: 'Cài đặt hệ thống',
        logs: 'Nhật ký hoạt động',
        backup: 'Sao lưu dữ liệu',
        payments: 'Lịch sử thanh toán',
        
        // Stats
        stats: {
            total_users: 'Tổng người dùng',
            active_users: 'Đang hoạt động',
            vip_users: 'Thành viên VIP',
            revenue: 'Doanh thu',
            operations: 'Thao tác hôm nay'
        },
        
        // VIP Levels
        vip_levels: {
            free: 'Miễn phí',
            basic: 'Cơ bản',
            pro: 'Chuyên nghiệp',
            enterprise: 'Doanh nghiệp'
        },
        
        // Actions
        add_user: 'Thêm người dùng',
        edit_user: 'Sửa thông tin',
        delete_user: 'Xóa người dùng',
        upgrade_vip: 'Nâng cấp VIP',
        view_logs: 'Xem nhật ký',
        export_data: 'Xuất dữ liệu',
        import_data: 'Nhập dữ liệu'
    },

    // VIP System
    vip: {
        title: 'Gói VIP',
        current_plan: 'Gói hiện tại',
        upgrade: 'Nâng cấp',
        features: 'Tính năng',
        limits: 'Giới hạn',
        price: 'Giá',
        per_month: '/tháng',
        subscribe: 'Đăng ký',
        unlimited: 'Không giới hạn',
        
        free: {
            name: 'Miễn phí',
            short: 'Free',
            validations: '100 kiểm tra/ngày',
            generations: '50 tạo email/ngày',
            support: 'Hỗ trợ cộng đồng'
        },
        basic: {
            name: 'Cơ bản',
            short: 'Basic',
            validations: '1,000 kiểm tra/ngày',
            generations: '500 tạo email/ngày',
            support: 'Hỗ trợ email'
        },
        pro: {
            name: 'Gói PRO',
            short: 'Pro',
            validations: '10,000 kiểm tra/ngày',
            generations: '5,000 tạo email/ngày',
            support: 'Hỗ trợ ưu tiên'
        },
        enterprise: {
            name: 'Doanh nghiệp',
            validations: 'Không giới hạn',
            generations: 'Không giới hạn',
            support: 'Hỗ trợ 24/7'
        }
    },

    // Notifications
    notifications: {
        success: {
            saved: 'Đã lưu thành công',
            deleted: 'Đã xóa thành công',
            updated: 'Đã cập nhật thành công',
            uploaded: 'Đã tải lên thành công',
            copied: 'Đã sao chép vào clipboard',
            exported: 'Đã xuất thành công'
        },
        error: {
            general: 'Đã xảy ra lỗi',
            network: 'Lỗi kết nối mạng',
            invalid_input: 'Dữ liệu đầu vào không hợp lệ',
            not_found: 'Không tìm thấy',
            permission_denied: 'Bạn không có quyền thực hiện thao tác này',
            server_error: 'Lỗi máy chủ'
        },
        warning: {
            unsaved_changes: 'Bạn có thay đổi chưa được lưu',
            confirm_delete: 'Bạn có chắc muốn xóa?',
            limit_reached: 'Đã đạt giới hạn'
        }
    },

    // Tooltips
    tooltips: {
        click_to_copy: 'Nhấn để sao chép',
        click_to_download: 'Nhấn để tải xuống',
        click_to_edit: 'Nhấn để chỉnh sửa',
        click_to_delete: 'Nhấn để xóa',
        drag_to_upload: 'Kéo thả file vào đây',
        max_file_size: 'Kích thước tối đa',
        allowed_formats: 'Định dạng cho phép'
    },

    // Info Sections
    info_sections: {
        usage_notes: {
            title: 'Lưu Ý Quan Trọng',
            email_validation: 'Kiểm tra Email:',
            email_validation_desc: 'Kết quả chính xác 95%. Luôn xác minh thủ công email quan trọng.',
            rate_limits: 'Giới hạn tốc độ:',
            rate_limits_desc: 'MIỄN PHÍ: 50/ngày, CƠ BẢN: 500/ngày, PRO: Không giới hạn.',
            data_privacy: 'Bảo mật dữ liệu:',
            data_privacy_desc: 'Tất cả dữ liệu được mã hóa và lưu trữ an toàn. Chúng tôi không bao giờ chia sẻ thông tin của bạn.',
            best_performance: 'Hiệu suất tốt nhất:',
            best_performance_desc: 'Sử dụng xử lý hàng loạt cho danh sách lớn (1000+ email) để có kết quả nhanh hơn.'
        },
        quick_start: {
            title: 'Hướng Dẫn Nhanh',
            step1_title: 'Chọn Công Cụ',
            step1_desc: 'Chọn từ Kiểm tra Email, Tạo Email, hoặc Công cụ Facebook dựa trên nhu cầu của bạn.',
            step2_title: 'Nhập Dữ Liệu',
            step2_desc: 'Dán email hoặc nhập tham số. Hỗ trợ nhập hàng loạt (mỗi dòng một email).',
            step3_title: 'Xử Lý & Tải Xuống',
            step3_desc: 'Nhấn "Xử lý" và tải xuống kết quả ở định dạng TXT, CSV, hoặc JSON.',
            view_docs: 'Xem Tài Liệu Đầy Đủ'
        },
        vip_packages: {
            title: 'Gói VIP',
            free_plan: 'MIỄN PHÍ',
            basic_plan: 'CƠ BẢN',
            pro_plan: 'PRO',
            enterprise_plan: 'DOANH NGHIỆP',
            per_month: '/tháng',
            validations_day: 'kiểm tra/ngày',
            basic_tools: 'Công cụ email cơ bản',
            all_email_tools: 'Tất cả công cụ email',
            all_tools_unlocked: 'Mở khóa tất cả công cụ',
            facebook_basic: 'Facebook cơ bản',
            facebook_advanced: 'Facebook nâng cao',
            standard_support: 'Hỗ trợ tiêu chuẩn',
            priority_support: 'Hỗ trợ ưu tiên',
            vip_support_24_7: 'Hỗ trợ VIP 24/7',
            api_access: 'Truy cập API',
            everything_in_pro: 'Mọi thứ trong PRO',
            dedicated_server: 'Máy chủ riêng',
            custom_integrations: 'Tích hợp tùy chỉnh',
            white_label: 'Tùy chọn nhãn trắng',
            no_facebook_tools: 'Không có công cụ Facebook',
            unlimited_validations: 'Kiểm tra không giới hạn',
            upgrade_to_pro: 'Nâng cấp lên PRO',
            popular: 'PHỔ BIẾN'
        }
    },

    // Settings Modal
    settings_modal: {
        title: 'Cài Đặt',
        profile_tab: 'Hồ sơ',
        preferences_tab: 'Tùy chọn',
        api_tab: 'API Keys',
        security_tab: 'Bảo mật',
        theme_tab: 'Giao diện',
        
        profile: {
            title: 'Thông Tin Hồ Sơ',
            full_name: 'Họ và tên',
            full_name_placeholder: 'Nhập họ và tên của bạn',
            email: 'Địa chỉ Email',
            email_placeholder: 'your@email.com',
            username: 'Tên đăng nhập',
            vip_level: 'Cấp VIP',
            upgrade: 'Nâng cấp',
            save_changes: 'Lưu Thay Đổi'
        },
        
        preferences: {
            title: 'Tùy Chọn Ứng Dụng',
            language: 'Ngôn ngữ',
            theme: 'Giao diện',
            theme_dark: 'Tối (Mặc định)',
            theme_light: 'Sáng',
            theme_auto: 'Tự động (Hệ thống)',
            enable_notifications: 'Bật thông báo desktop',
            auto_save_results: 'Tự động lưu kết quả kiểm tra',
            enable_sound: 'Bật hiệu ứng âm thanh',
            save_preferences: 'Lưu Tùy Chọn'
        },
        
        api: {
            title: 'Truy Cập API',
            info: 'Truy cập API có sẵn cho người dùng PRO và ENTERPRISE. Tạo API keys để tích hợp dịch vụ của chúng tôi vào ứng dụng của bạn.',
            your_api_key: 'API Key Của Bạn',
            regenerate: 'Tạo Lại API Key',
            view_docs: 'Xem Tài Liệu API'
        },
        
        security: {
            title: 'Cài Đặt Bảo Mật',
            current_password: 'Mật khẩu hiện tại',
            current_password_placeholder: 'Nhập mật khẩu hiện tại',
            new_password: 'Mật khẩu mới',
            new_password_placeholder: 'Nhập mật khẩu mới',
            confirm_password: 'Xác nhận mật khẩu mới',
            confirm_password_placeholder: 'Xác nhận mật khẩu mới',
            change_password: 'Đổi Mật Khẩu',
            two_factor_auth: 'Xác Thực Hai Yếu Tố',
            two_factor_desc: 'Thêm một lớp bảo mật bổ sung cho tài khoản của bạn',
            enable_2fa: 'Bật 2FA'
        },
        
        theme: {
            title: 'Cài Đặt Giao Diện',
            theme_mode: 'Chế độ giao diện',
            light_mode: 'Sáng',
            dark_mode: 'Tối',
            preset_themes: 'Giao diện mẫu',
            professional: 'Chuyên nghiệp',
            creative: 'Sáng tạo',
            minimal: 'Tối giản',
            bold: 'Táo bạo',
            elegant: 'Thanh lịch',
            primary_color: 'Màu chính',
            secondary_color: 'Màu phụ',
            accent_color: 'Màu nhấn',
            background_color: 'Màu nền',
            text_color: 'Màu chữ',
            font_family: 'Font chữ',
            font_size: 'Kích thước chữ',
            sidebar_width: 'Độ rộng sidebar',
            border_radius: 'Bo góc',
            animation_speed: 'Tốc độ animation',
            custom_css: 'CSS tùy chỉnh',
            custom_css_placeholder: 'Nhập CSS tùy chỉnh của bạn...',
            reset_theme: 'Đặt lại mặc định',
            export_theme: 'Xuất giao diện',
            import_theme: 'Nhập giao diện',
            save_theme: 'Lưu Giao Diện'
        }
    },

    // Notifications Panel
    notifications_panel: {
        title: 'Thông Báo',
        mark_all_read: 'Đánh dấu tất cả đã đọc',
        validation_complete: 'Hoàn Thành Kiểm Tra',
        validation_complete_msg: 'Đã kiểm tra thành công 150 email với tỷ lệ LIVE 95%',
        system_update: 'Cập Nhật Hệ Thống',
        system_update_msg: 'Tính năng mới: Công cụ kiểm tra Facebook nâng cao với 6 APIs',
        upgrade_pro: 'Nâng cấp lên PRO',
        upgrade_pro_msg: 'Nhận kiểm tra không giới hạn và mở khóa tất cả tính năng nâng cao',
        welcome_title: 'Chào mừng!',
        welcome_msg: 'Tài khoản của bạn đã được tạo thành công',
        minutes_ago: 'phút trước',
        hours_ago: 'giờ trước',
        days_ago: 'ngày trước'
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = vi;
}
