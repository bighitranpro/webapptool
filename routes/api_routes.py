"""
API Routes - All Email Tool Endpoints
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import sqlite3
import json
from database import Database
from modules import (
    EmailValidator,
    EmailGenerator,
    EmailExtractor,
    EmailFormatter,
    EmailFilter,
    EmailSplitter,
    EmailCombiner,
    EmailAnalyzer,
    EmailDeduplicator,
    EmailBatchProcessor,
    FBLinkedChecker,
    EmailPass2FAChecker,
    PageMining
)

api_bp = Blueprint('api', __name__)

# Initialize database
db = Database()

# Initialize modules
validator = EmailValidator()
generator = EmailGenerator()
extractor = EmailExtractor()
formatter = EmailFormatter()
email_filter = EmailFilter()
splitter = EmailSplitter()
combiner = EmailCombiner()
analyzer = EmailAnalyzer()
deduplicator = EmailDeduplicator()
batch_processor = EmailBatchProcessor()
fb_checker = FBLinkedChecker()
pass_2fa_checker = EmailPass2FAChecker()
page_miner = PageMining()


@api_bp.route('/api/validate', methods=['POST'])
def api_validate():
    """
    Email validation with LIVE/DIE detection + Database storage
    
    Request:
        {
            "emails": ["email1@gmail.com", "email2@yahoo.com"],
            "options": {
                "check_mx": true,
                "check_smtp": true,
                "check_disposable": true,
                "check_fb_compat": true,
                "max_workers": 10,
                "timeout": 5,
                "use_cache": true
            }
        }
    
    Response:
        {
            "success": true,
            "stats": {...},
            "results": {
                "live": [...],
                "die": [...],
                "unknown": [...]
            },
            "db_saved": true
        }
    """
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        options = data.get('options', {})
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        use_cache = options.get('use_cache', True)
        
        # Check cache first if enabled
        cached_results = []
        emails_to_validate = []
        
        if use_cache:
            for email in emails:
                cached = db.get_validation_result(email)
                if cached:
                    cached_results.append(cached)
                else:
                    emails_to_validate.append(email)
        else:
            emails_to_validate = emails
        
        # Run bulk validation for uncached emails
        max_workers = options.get('max_workers', 10)
        
        if emails_to_validate:
            result = validator.bulk_validate(emails_to_validate, max_workers=max_workers)
            
            # Save results to database
            for live_result in result['results']['live']:
                db.save_validation_result(live_result)
            
            for die_result in result['results']['die']:
                db.save_validation_result(die_result)
            
            for unknown_result in result['results']['unknown']:
                db.save_validation_result(unknown_result)
            
            # Save session stats
            db.save_validation_session(result['stats'])
        else:
            # All from cache
            result = {
                'stats': {
                    'total': len(cached_results),
                    'live': sum(1 for r in cached_results if r['status'] == 'LIVE'),
                    'die': sum(1 for r in cached_results if r['status'] == 'DIE'),
                    'unknown': sum(1 for r in cached_results if r['status'] == 'UNKNOWN'),
                    'can_receive_code': sum(1 for r in cached_results if r.get('can_receive_code')),
                    'processing_time': 0
                },
                'results': {
                    'live': [r for r in cached_results if r['status'] == 'LIVE'],
                    'die': [r for r in cached_results if r['status'] == 'DIE'],
                    'unknown': [r for r in cached_results if r['status'] == 'UNKNOWN']
                }
            }
        
        # Merge cached results
        if cached_results and emails_to_validate:
            result['results']['live'].extend([r for r in cached_results if r['status'] == 'LIVE'])
            result['results']['die'].extend([r for r in cached_results if r['status'] == 'DIE'])
            result['results']['unknown'].extend([r for r in cached_results if r['status'] == 'UNKNOWN'])
            
            # Recalculate stats
            all_results = cached_results + result['results']['live'] + result['results']['die'] + result['results']['unknown']
            result['stats']['total'] = len(emails)
            result['stats']['live'] = len(result['results']['live'])
            result['stats']['die'] = len(result['results']['die'])
            result['stats']['unknown'] = len(result['results']['unknown'])
        
        # Get dashboard data from database
        dashboard_data = db.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': result['stats'],
            'results': result['results'],
            'dashboard': dashboard_data,
            'db_saved': True,
            'from_cache': len(cached_results),
            'newly_validated': len(emails_to_validate),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Generate random emails + Save to Database
    
    Request:
        {
            "email_type": "random",
            "text": "base",
            "total": 10,
            "domains": ["gmail.com", "yahoo.com"],  // NEW: array of domains
            "char_type": "lowercase",
            "number_type": "suffix"
        }
    """
    try:
        data = request.get_json()
        
        email_type = data.get('email_type', 'random')
        text = data.get('text', '')
        total = int(data.get('total', 10))
        
        # Support both 'domains' (new) and 'domain' (backward compatibility)
        domains = data.get('domains')
        if not domains:
            # Fallback to single domain for backward compatibility
            single_domain = data.get('domain', 'gmail.com')
            domains = [single_domain]
        
        char_type = data.get('char_type', 'lowercase')
        number_type = data.get('number_type', 'suffix')
        
        if total < 1 or total > 10000:
            return jsonify({
                'success': False,
                'message': 'Total must be between 1 and 10,000'
            }), 400
        
        result = generator.generate_emails(
            email_type, text, total, domains, char_type, number_type
        )
        
        # Save generated emails to database
        if result.get('success') and result.get('emails'):
            params = {
                'email_type': email_type,
                'domains': ','.join(domains),  # Store as comma-separated string
                'char_type': char_type,
                'number_type': number_type
            }
            
            for email in result['emails']:
                try:
                    db.save_generated_email(email, params)
                except Exception as save_error:
                    print(f"Warning: Failed to save email {email}: {save_error}")
            
            result['db_saved'] = True
            result['saved_count'] = len(result['emails'])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/extract', methods=['POST'])
def api_extract():
    """Extract emails from text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        options = data.get('options', {})
        
        if not text:
            return jsonify({
                'success': False,
                'message': 'No text provided'
            }), 400
        
        remove_dups = options.get('remove_dups', True)
        filter_domains = options.get('filter_domains')
        filter_pattern = options.get('filter_pattern')
        
        result = extractor.extract_and_process(
            text, 
            remove_dups=remove_dups,
            filter_domains=filter_domains,
            filter_pattern=filter_pattern
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/format', methods=['POST'])
def api_format():
    """Format email list"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        case_format = data.get('case_format', 'lowercase')
        sort_type = data.get('sort_type')
        prefix = data.get('prefix')
        suffix = data.get('suffix')
        new_domain = data.get('new_domain')
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        result = formatter.format_emails(
            emails, 
            case_format=case_format,
            sort_type=sort_type,
            prefix=prefix,
            suffix=suffix,
            new_domain=new_domain
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/filter', methods=['POST'])
def api_filter():
    """Filter email list"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        filters = data.get('filters', {})
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        result = email_filter.apply_filters(emails, filters)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/split', methods=['POST'])
def api_split():
    """Split email list"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        method = data.get('method', 'count')
        count = data.get('count')
        chunks = data.get('chunks')
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        result = splitter.split_emails(emails, method, count=count, chunks=chunks)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/combine', methods=['POST'])
def api_combine():
    """Combine email lists"""
    try:
        data = request.get_json()
        email_lists = data.get('email_lists', [])
        method = data.get('method', 'unique')
        case_sensitive = data.get('case_sensitive', False)
        
        if not email_lists or len(email_lists) < 2:
            return jsonify({
                'success': False,
                'message': 'At least 2 email lists required'
            }), 400
        
        result = combiner.combine_emails(
            email_lists, 
            method=method,
            case_sensitive=case_sensitive
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze email list"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        result = analyzer.full_analysis(emails)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/deduplicate', methods=['POST'])
def api_deduplicate():
    """Remove duplicate emails"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        method = data.get('method', 'case_insensitive')
        keep_strategy = data.get('keep_strategy', 'first')
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        result = deduplicator.deduplicate(
            emails, 
            method=method,
            keep_strategy=keep_strategy
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/batch', methods=['POST'])
def api_batch():
    """Process emails in batch"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        batch_size = data.get('batch_size', 100)
        operation = data.get('operation', 'validate')
        max_workers = data.get('max_workers', 5)
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        # Define processor function based on operation
        if operation == 'validate':
            processor_func = lambda batch: validator.bulk_validate(batch, max_workers=5)
        elif operation == 'deduplicate':
            processor_func = lambda batch: deduplicator.deduplicate(batch)
        elif operation == 'format':
            processor_func = lambda batch: formatter.format_emails(batch)
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown operation: {operation}'
            }), 400
        
        result = batch_processor.process_parallel(
            emails,
            batch_size=batch_size,
            processor_func=processor_func,
            max_workers=max_workers
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/fb-check', methods=['POST'])
def api_fb_check():
    """
    Facebook Email Linked Checker
    Check if emails are linked to Facebook accounts
    
    Request:
        {
            "emails": ["email1@gmail.com", "email2@yahoo.com"],
            "options": {
                "api_type": "api1" | "api2" | ... | "api6" | "random",
                "proxy_config": {
                    "enabled": true,
                    "type": "http" | "socks4" | "socks5" | "tinsoft" | etc,
                    "host": "proxy.example.com",
                    "port": 8080,
                    "auth": {"username": "user", "password": "pass"}
                },
                "max_workers": 100,
                "start_from": 0,
                "check_code_68": false
            }
        }
    
    Response:
        {
            "success": true,
            "stats": {
                "total": 100,
                "linked": 40,
                "hidden_linked": 15,
                "not_linked": 43,
                "error": 2,
                "code6_count": 25,
                "code8_count": 30,
                "processing_time": 12.5
            },
            "results": {
                "linked": [...],
                "hidden_linked": [...],
                "not_linked": [...],
                "error": [...]
            }
        }
    """
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        options = data.get('options', {})
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        # Run bulk check
        result = fb_checker.bulk_check(emails, options)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/fb-check-code', methods=['POST'])
def api_fb_check_code():
    """
    Check CODE 6 or CODE 8 for emails
    Specialized endpoint for code length detection
    """
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        options = data.get('options', {})
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        result = fb_checker.check_code_type(emails, options)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/check-2fa', methods=['POST'])
def api_check_2fa():
    """
    Check Email:Password for 2FA and Page
    
    Request:
        {
            "accounts": ["email1:pass1", "email2:pass2"],
            "options": {
                "api_type": "api1" | "api2" | "random",
                "password_pattern": "1|@|.|#|*|5|*|!|?",
                "validate_pattern": true,
                "proxy_config": {...},
                "max_workers": 200,
                "start_from": 0
            }
        }
    
    Response:
        {
            "success": true,
            "stats": {
                "total": 100,
                "hit_2fa": 15,
                "has_page": 10,
                "not_hit": 65,
                "error": 10,
                "checked": 100,
                "processing_time": 25.5
            },
            "results": {
                "hit_2fa": [...],
                "has_page": [...],
                "not_hit": [...],
                "error": [...]
            }
        }
    """
    try:
        data = request.get_json()
        accounts = data.get('accounts', [])
        options = data.get('options', {})
        
        if not accounts:
            return jsonify({
                'success': False,
                'message': 'No accounts provided'
            }), 400
        
        # Run bulk check
        result = pass_2fa_checker.bulk_check(accounts, options)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/page-mining', methods=['POST'])
def api_page_mining():
    """
    ID Page Mining - Extract pages from UIDs
    
    Request:
        {
            "uids": ["100001234567890", "100009876543210"],
            "options": {
                "proxy_config": {...},
                "max_workers": 100,
                "start_from": 0,
                "filter_has_ads": true,
                "filter_country": "Vietnam",
                "filter_verified": false
            }
        }
    
    Response:
        {
            "success": true,
            "stats": {
                "total_uids": 100,
                "total_pages_found": 250,
                "pages_with_ads": 75,
                "pages_verified": 38,
                "emails_collected": 100,
                "processing_time": 45.2
            },
            "results": {
                "pages": [{page_id, page_name, has_ads, country, ...}],
                "emails": ["page123@gmail.com", ...]
            }
        }
    """
    try:
        data = request.get_json()
        uids = data.get('uids', [])
        options = data.get('options', {})
        
        if not uids:
            return jsonify({
                'success': False,
                'message': 'No UIDs provided'
            }), 400
        
        # Run bulk mining
        result = page_miner.bulk_mine(uids, options)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/db/stats', methods=['GET'])
def api_db_stats():
    """
    Get database statistics and recent data
    Returns dashboard data including LIVE/DIE tables
    """
    try:
        stats = db.get_statistics()
        live_emails = db.get_live_emails(100)
        die_emails = db.get_die_emails(100)
        recent_validations = db.get_recent_validations(50)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'live_emails': live_emails,
            'die_emails': die_emails,
            'recent_validations': recent_validations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/db/search', methods=['POST'])
def api_db_search():
    """
    Search emails in database
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'No search query provided'
            }), 400
        
        results = db.search_emails(query)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database status"""
    try:
        # Test database connection
        db_stats = db.get_statistics()
        db_healthy = True
    except Exception as e:
        db_stats = {}
        db_healthy = False
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'database': {
            'healthy': db_healthy,
            'stats': db_stats
        },
        'modules': {
            'validator': True,
            'generator': True,
            'extractor': True,
            'formatter': True,
            'filter': True,
            'splitter': True,
            'combiner': True,
            'analyzer': True,
            'deduplicator': True,
            'batch_processor': True,
            'database': db_healthy
        }
    })


@api_bp.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """
    Get real-time dashboard statistics from database
    
    Returns:
        - Total LIVE emails
        - Total DIE emails
        - Total emails processed
        - Can receive code count
        - Success rate percentage
        - Recent activity count
        - Today's activity count
        - This week's activity count
    """
    try:
        import sqlite3
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        # Get validation status counts
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count
            FROM validation_results
            GROUP BY status
        ''')
        
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        live_count = status_counts.get('LIVE', 0)
        die_count = status_counts.get('DIE', 0)
        total_count = live_count + die_count
        
        # Get can_receive_code count
        cursor.execute('''
            SELECT COUNT(*) 
            FROM validation_results 
            WHERE can_receive_code = 1 AND status = 'LIVE'
        ''')
        can_receive_code = cursor.fetchone()[0]
        
        # Calculate success rate
        success_rate = round((live_count / total_count * 100), 2) if total_count > 0 else 0
        
        # Get today's validations
        cursor.execute('''
            SELECT COUNT(*) 
            FROM validation_results 
            WHERE DATE(created_at) = DATE('now')
        ''')
        today_count = cursor.fetchone()[0]
        
        # Get this week's validations
        cursor.execute('''
            SELECT COUNT(*) 
            FROM validation_results 
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        ''')
        week_count = cursor.fetchone()[0]
        
        # Get recent activity (last 10 validations)
        cursor.execute('''
            SELECT 
                email,
                status,
                can_receive_code,
                created_at
            FROM validation_results
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        recent_activity = []
        for row in cursor.fetchall():
            recent_activity.append({
                'email': row[0],
                'status': row[1],
                'can_receive_code': bool(row[2]),
                'timestamp': row[3]
            })
        
        # Get activity logs if they exist
        cursor.execute('''
            SELECT COUNT(*) 
            FROM sqlite_master 
            WHERE type='table' AND name='activity_logs'
        ''')
        
        activity_logs_exist = cursor.fetchone()[0] > 0
        total_activities = 0
        
        if activity_logs_exist:
            cursor.execute('SELECT COUNT(*) FROM activity_logs')
            total_activities = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'live_emails': live_count,
                'die_emails': die_count,
                'total_emails': total_count,
                'can_receive_code': can_receive_code,
                'success_rate': success_rate,
                'today_count': today_count,
                'week_count': week_count,
                'total_activities': total_activities
            },
            'recent_activity': recent_activity,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch dashboard stats: {str(e)}'
        }), 500



# ==================== ADMIN THEME SETTINGS API ====================

@api_bp.route('/api/admin/theme/settings', methods=['GET'])
def get_theme_settings():
    """Get current theme settings for logged-in user"""
    try:
        user_id = session.get('user_id', 1)  # Default to admin
        
        conn = sqlite3.connect('email_tool.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT theme_config FROM admin_settings
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            theme_config = json.loads(row['theme_config'])
            return jsonify({
                'success': True,
                'theme': theme_config
            })
        else:
            # Return default theme
            default_theme = {
                "theme_mode": "dark",
                "primary_color": "#ffd700",
                "secondary_color": "#00d9ff",
                "accent_color": "#ff6b35",
                "background_color": "#0a0e27",
                "text_color": "#ffffff",
                "font_family": "Inter",
                "font_size_base": "16px",
                "sidebar_width": "280px",
                "border_radius": "12px",
                "animation_speed": "0.3s"
            }
            return jsonify({
                'success': True,
                'theme': default_theme
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/admin/theme/settings', methods=['POST'])
def save_theme_settings():
    """Save theme settings for logged-in user"""
    try:
        user_id = session.get('user_id', 1)
        theme_config = request.json.get('theme', {})
        
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        # Check if settings exist
        cursor.execute('SELECT id FROM admin_settings WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute('''
                UPDATE admin_settings 
                SET theme_config = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (json.dumps(theme_config), user_id))
        else:
            # Insert
            cursor.execute('''
                INSERT INTO admin_settings (user_id, theme_config)
                VALUES (?, ?)
            ''', (user_id, json.dumps(theme_config)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Theme settings saved successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/admin/theme/reset', methods=['PUT'])
def reset_theme_settings():
    """Reset theme to default"""
    try:
        user_id = session.get('user_id', 1)
        
        default_theme = {
            "theme_mode": "dark",
            "primary_color": "#ffd700",
            "secondary_color": "#00d9ff",
            "accent_color": "#ff6b35",
            "background_color": "#0a0e27",
            "text_color": "#ffffff",
            "font_family": "Inter",
            "font_size_base": "16px",
            "sidebar_width": "280px",
            "border_radius": "12px",
            "animation_speed": "0.3s"
        }
        
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE admin_settings 
            SET theme_config = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (json.dumps(default_theme), user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Theme reset to default',
            'theme': default_theme
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
