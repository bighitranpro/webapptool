"""
Email Tool Pro - Flask Application
Modular architecture with LIVE/DIE detection and Database storage
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sys

# Import all modules
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
    EmailBatchProcessor
)

# Import database
from database import Database

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Support Vietnamese characters
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max request size

# Initialize database
db = Database()

# Initialize module instances
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


@app.route('/')
def index():
    """Render dashboard page"""
    return render_template('index.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/validate', methods=['POST'])
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


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Generate random emails + Save to Database
    
    Request:
        {
            "email_type": "random",
            "text": "base",
            "total": 10,
            "domain": "gmail.com",
            "char_type": "lowercase",
            "number_type": "suffix"
        }
    """
    try:
        data = request.get_json()
        
        email_type = data.get('email_type', 'random')
        text = data.get('text', '')
        total = int(data.get('total', 10))
        domain = data.get('domain', 'gmail.com')
        char_type = data.get('char_type', 'lowercase')
        number_type = data.get('number_type', 'suffix')
        
        if total < 1 or total > 10000:
            return jsonify({
                'success': False,
                'message': 'Total must be between 1 and 10,000'
            }), 400
        
        result = generator.generate_emails(
            email_type, text, total, domain, char_type, number_type
        )
        
        # Save generated emails to database
        if result.get('success') and result.get('emails'):
            params = {
                'email_type': email_type,
                'domain': domain,
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


@app.route('/api/extract', methods=['POST'])
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


@app.route('/api/format', methods=['POST'])
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


@app.route('/api/filter', methods=['POST'])
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


@app.route('/api/split', methods=['POST'])
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


@app.route('/api/combine', methods=['POST'])
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


@app.route('/api/analyze', methods=['POST'])
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


@app.route('/api/deduplicate', methods=['POST'])
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


@app.route('/api/batch', methods=['POST'])
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


@app.route('/api/db/stats', methods=['GET'])
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


@app.route('/api/db/search', methods=['POST'])
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


@app.route('/api/health', methods=['GET'])
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Check if running in production mode
    port = 80 if len(sys.argv) > 1 and sys.argv[1] == 'production' else 5000
    debug_mode = port == 5000
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║      Email Tool Pro v2.0                  ║
    ║      Modular Architecture                 ║
    ╚══════════════════════════════════════════╝
    
    🚀 Server starting on port {port}
    🔧 Debug mode: {debug_mode}
    📦 All modules loaded successfully
    
    Dashboard: http://localhost:{port}/
    API Docs: http://localhost:{port}/api/health
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
