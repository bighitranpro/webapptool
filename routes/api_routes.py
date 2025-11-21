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
from modules.page_mining_enhanced import PageMiningEnhanced

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

# Initialize Enhanced Page Mining Module
page_miner_enhanced = PageMiningEnhanced(api_configs={
    'graph_api': {
        'enabled': False,  # Enable when token is available
        'token': None,
        'version': 'v18.0'
    },
    'scraper_api': {
        'enabled': True,
        'endpoints': []
    }
})


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
    ID Page Mining - Enhanced Extract pages from UIDs
    
    Request:
        {
            "uids": ["100001234567890", "100009876543210"],
            "options": {
                "proxy_config": {...},
                "max_workers": 100,
                "start_from": 0,
                "filters": {
                    "has_ads": true,
                    "country": "Vietnam",
                    "verified": false,
                    "category": "Restaurant",
                    "min_likes": 1000,
                    "has_email": true,
                    "has_phone": true,
                    "has_website": false
                }
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
                "phones_collected": 85,
                "websites_collected": 120,
                "processing_time": 45.2,
                "cache_hits": 15,
                "api_calls": 85
            },
            "results": {
                "pages": [{
                    "page_id": "123456789",
                    "page_name": "Nhà Hàng ABC",
                    "username": "nhahangarbc",
                    "page_url": "https://facebook.com/nhahangarbc",
                    "uid_owner": "100001234567890",
                    "has_ads": true,
                    "country": "Vietnam",
                    "location": "Hồ Chí Minh",
                    "verified": false,
                    "likes": 15000,
                    "category": "Restaurant",
                    "about": "...",
                    "email": "contact@abc.com",
                    "domain_email": "abc.com",
                    "phone": "+84901234567",
                    "website": "https://abc.com",
                    "data_source": "graph_api",
                    "timestamp": "2024-01-15T..."
                }],
                "statistics": {
                    "by_category": {...},
                    "by_country": {...},
                    "by_domain": {...}
                }
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
        
        # Run enhanced bulk mining with all new features
        result = page_miner_enhanced.bulk_mine(uids, options)
        
        # Log activity if session exists
        if 'user_id' in session:
            try:
                user_id = session['user_id']
                conn = sqlite3.connect('email_tool.db')
                cursor = conn.cursor()
                
                # Log the mining activity
                cursor.execute('''
                    INSERT INTO user_activities 
                    (user_id, activity_type, activity_title, activity_description, 
                     status, icon, color, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    'page_mining',
                    'Khai thác Page từ UID',
                    f'Đã khai thác {result.get("stats", {}).get("total_pages_found", 0)} trang từ {len(uids)} UID',
                    'success' if result.get('success') else 'error',
                    'fa-bullseye',
                    'purple',
                    json.dumps({
                        'uids_count': len(uids),
                        'pages_found': result.get("stats", {}).get("total_pages_found", 0),
                        'emails_collected': result.get("stats", {}).get("emails_collected", 0)
                    })
                ))
                
                conn.commit()
                conn.close()
            except Exception as log_error:
                print(f"Warning: Failed to log activity: {log_error}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/page-mining/export', methods=['POST'])
def api_page_mining_export():
    """
    Export Page Mining results in various formats
    
    Request:
        {
            "pages": [{...page data...}],
            "format": "csv" | "json" | "txt"
        }
    
    Response:
        {
            "success": true,
            "data": "exported content as string",
            "format": "csv"
        }
    """
    try:
        data = request.get_json()
        pages = data.get('pages', [])
        export_format = data.get('format', 'csv')
        
        if not pages:
            return jsonify({
                'success': False,
                'message': 'No pages provided for export'
            }), 400
        
        if export_format == 'csv':
            exported_data = page_miner_enhanced.export_pages_csv(pages)
        elif export_format == 'json':
            exported_data = page_miner_enhanced.export_pages_json(pages)
        elif export_format == 'txt':
            exported_data = page_miner_enhanced.export_pages_txt(pages)
        else:
            return jsonify({
                'success': False,
                'message': f'Unsupported export format: {export_format}'
            }), 400
        
        return jsonify({
            'success': True,
            'data': exported_data,
            'format': export_format,
            'count': len(pages)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@api_bp.route('/api/page-mining/statistics', methods=['POST'])
def api_page_mining_statistics():
    """
    Get detailed statistics from mining results
    
    Request:
        {
            "pages": [{...page data...}]
        }
    
    Response:
        {
            "success": true,
            "statistics": {
                "by_category": {...},
                "by_country": {...},
                "by_domain": {...}
            }
        }
    """
    try:
        data = request.get_json()
        pages = data.get('pages', [])
        
        if not pages:
            return jsonify({
                'success': False,
                'message': 'No pages provided for statistics'
            }), 400
        
        # Temporarily set pages in module for statistics
        page_miner_enhanced.pages = pages
        statistics = page_miner_enhanced.get_statistics_summary()
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
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

# ============================================
# SETTINGS MODAL APIs
# ============================================

@api_bp.route('/api/user/profile', methods=['GET', 'POST'])
def user_profile():
    """Get or update user profile"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        try:
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, email, full_name, role, created_at 
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return jsonify({
                    'success': True,
                    'user': {
                        'username': user[0],
                        'email': user[1],
                        'full_name': user[2],
                        'role': user[3],
                        'created_at': user[4]
                    }
                })
            return jsonify({'success': False, 'message': 'User not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            full_name = data.get('full_name', '')
            email = data.get('email', '')
            
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, email = ?
                WHERE id = ?
            ''', (full_name, email, user_id))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/user/preferences', methods=['GET', 'POST'])
def user_preferences():
    """Get or update user preferences"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        try:
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            
            # Try to get preferences from a preferences table (we'll create it if needed)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    language VARCHAR(10) DEFAULT 'vi',
                    theme VARCHAR(20) DEFAULT 'dark',
                    notifications_enabled BOOLEAN DEFAULT 1,
                    auto_save_results BOOLEAN DEFAULT 1,
                    sound_effects BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
            prefs = cursor.fetchone()
            
            if not prefs:
                # Create default preferences
                cursor.execute('''
                    INSERT INTO user_preferences (user_id, language, theme)
                    VALUES (?, 'vi', 'dark')
                ''', (user_id,))
                conn.commit()
                prefs = ('', user_id, 'vi', 'dark', 1, 1, 0, '', '')
            
            conn.close()
            
            return jsonify({
                'success': True,
                'preferences': {
                    'language': prefs[2],
                    'theme': prefs[3],
                    'notifications_enabled': bool(prefs[4]),
                    'auto_save_results': bool(prefs[5]),
                    'sound_effects': bool(prefs[6])
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_preferences
                SET language = ?,
                    theme = ?,
                    notifications_enabled = ?,
                    auto_save_results = ?,
                    sound_effects = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                data.get('language', 'vi'),
                data.get('theme', 'dark'),
                1 if data.get('notifications_enabled') else 0,
                1 if data.get('auto_save_results') else 0,
                1 if data.get('sound_effects') else 0,
                user_id
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Preferences saved successfully'
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/user/password', methods=['POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        user_id = session['user_id']
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Current password and new password are required'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 6 characters'
            }), 400
        
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        # Verify current password
        cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user or user[0] != current_password:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 400
        
        # Update password
        cursor.execute('''
            UPDATE users 
            SET password = ?
            WHERE id = ?
        ''', (new_password, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/user/apikey', methods=['GET', 'POST'])
def manage_api_key():
    """Get or regenerate API key"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        try:
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            
            # Create API keys table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    api_key VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            cursor.execute('''
                SELECT api_key, created_at, last_used 
                FROM api_keys 
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            key = cursor.fetchone()
            
            if not key:
                # Generate new key
                import secrets
                api_key = 'sk_live_' + secrets.token_hex(24)
                cursor.execute('''
                    INSERT INTO api_keys (user_id, api_key)
                    VALUES (?, ?)
                ''', (user_id, api_key))
                conn.commit()
                key = (api_key, datetime.now(), None)
            
            conn.close()
            
            return jsonify({
                'success': True,
                'api_key': key[0],
                'created_at': str(key[1]),
                'last_used': str(key[2]) if key[2] else None
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        # Regenerate API key
        try:
            import secrets
            
            conn = sqlite3.connect('email_tool.db')
            cursor = conn.cursor()
            
            # Deactivate old keys
            cursor.execute('''
                UPDATE api_keys SET is_active = 0 WHERE user_id = ?
            ''', (user_id,))
            
            # Generate new key
            api_key = 'sk_live_' + secrets.token_hex(24)
            cursor.execute('''
                INSERT INTO api_keys (user_id, api_key)
                VALUES (?, ?)
            ''', (user_id, api_key))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'API key regenerated successfully',
                'api_key': api_key
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/activities/recent', methods=['GET'])
def get_recent_activities():
    """Get recent user activities from database"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        limit = request.args.get('limit', 10, type=int)
        
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        # Create activities table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                activity_title VARCHAR(200) NOT NULL,
                activity_description TEXT,
                status VARCHAR(20) DEFAULT 'success',
                icon VARCHAR(50),
                color VARCHAR(20),
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Get recent activities
        cursor.execute('''
            SELECT activity_type, activity_title, activity_description, 
                   status, icon, color, created_at, metadata
            FROM user_activities
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'type': row[0],
                'title': row[1],
                'description': row[2],
                'status': row[3],
                'icon': row[4] or 'fa-circle',
                'color': row[5] or 'blue',
                'time': row[6],
                'metadata': json.loads(row[7]) if row[7] else {}
            })
        
        conn.close()
        
        # If no activities, return sample data
        if not activities:
            activities = [
                {
                    'type': 'validation',
                    'title': 'Hoàn thành kiểm tra Email',
                    'description': 'Đã kiểm tra 150 email với 92% LIVE',
                    'status': 'success',
                    'icon': 'fa-shield-check',
                    'color': 'blue',
                    'time': 'Vài phút trước',
                    'metadata': {'count': 150, 'live': 138}
                }
            ]
        
        return jsonify({
            'success': True,
            'activities': activities,
            'total': len(activities)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/activities/log', methods=['POST'])
def log_activity():
    """Log a new user activity"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        data = request.json
        
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activities 
            (user_id, activity_type, activity_title, activity_description, 
             status, icon, color, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('type', 'general'),
            data.get('title', ''),
            data.get('description', ''),
            data.get('status', 'success'),
            data.get('icon', 'fa-circle'),
            data.get('color', 'blue'),
            json.dumps(data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Activity logged successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    """Get user stats summary"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        
        conn = sqlite3.connect('email_tool.db')
        cursor = conn.cursor()
        
        # Get validation stats from email_results table
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'LIVE' THEN 1 ELSE 0 END) as live,
                SUM(CASE WHEN status = 'DIE' THEN 1 ELSE 0 END) as die,
                SUM(CASE WHEN can_receive_code = 1 THEN 1 ELSE 0 END) as can_receive_code
            FROM email_results
            WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        
        # Get recent activities count
        cursor.execute('''
            SELECT COUNT(*) FROM user_activities WHERE user_id = ?
        ''', (user_id,))
        
        total_activities = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_validated': stats[0] or 0,
                'live_emails': stats[1] or 0,
                'die_emails': stats[2] or 0,
                'can_receive_code': stats[3] or 0,
                'total_activities': total_activities,
                'success_rate': round((stats[1] / stats[0] * 100) if stats[0] > 0 else 0, 1)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
