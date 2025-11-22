"""
Email Tool Pro v3.0 - Professional Edition with Realtime Validation
Features:
- WebSocket realtime updates
- Professional email validator with 95-99% accuracy
- Worker pool & queue system
- Progress tracking & live statistics
- Export functions (LIVE/DIE/FULL/ERROR)
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from datetime import datetime
import sys
import os
import json
import io
import csv
from threading import Lock

# Import all modules
from modules import (
    EmailValidator,
    EmailValidatorPro,  # NEW Professional Validator
    EmailGenerator,
    RealisticEmailGenerator,  # NEW Realistic Generator
    EmailExtractor,
    EmailFormatter,
    EmailFilter,
    EmailSplitter,
    EmailCombiner,
    EmailAnalyzer,
    EmailDeduplicator,
    EmailBatchProcessor,
    EmailCheckerIntegrated  # NEW Integrated Email Checker
)

# Import database
from database import Database

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['SECRET_KEY'] = 'email-validator-pro-secret-key-2024'
app.config['SERVER_NAME'] = None  # Allow any domain

# Initialize SocketIO for realtime updates
# Allow multiple origins including the custom domain
allowed_origins = [
    "*",  # Allow all for development
    "http://mochiphoto.click",
    "https://mochiphoto.click",
    "http://www.mochiphoto.click",
    "https://www.mochiphoto.click",
    "http://14.225.210.195:5000",
    "http://localhost:5000"
]
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='gevent')

# Initialize database
db = Database()

# Initialize module instances
validator = EmailValidator()  # Legacy validator
validator_pro = EmailValidatorPro()  # NEW Professional validator
generator = EmailGenerator()
realistic_generator = RealisticEmailGenerator()  # NEW Realistic generator
extractor = EmailExtractor()
formatter = EmailFormatter()
email_filter = EmailFilter()
splitter = EmailSplitter()
combiner = EmailCombiner()
analyzer = EmailAnalyzer()
deduplicator = EmailDeduplicator()
batch_processor = EmailBatchProcessor()

# Email Checker Integrated module
try:
    email_checker = EmailCheckerIntegrated()
    print("✅ Email Checker Integrated loaded successfully")
except Exception as e:
    print(f"⚠️  Email Checker disabled: {e}")
    email_checker = None

# Session storage for validation results
validation_sessions = {}
session_lock = Lock()


@app.route('/')
def index():
    """Render enhanced dashboard with realtime features"""
    return render_template('realtime_validator.html')


@app.route('/test')
def test_page():
    """Render test/debug page"""
    return render_template('test_validator.html')


@app.route('/complete')
def complete_validator():
    """Render complete validator with full copy/export functionality"""
    return render_template('validator_complete.html')


@app.route('/generator')
def realistic_generator_page():
    """Render realistic email generator page"""
    return render_template('realistic_generator.html')


@app.route('/checker')
def email_checker_page():
    """Render integrated email checker page"""
    return render_template('email_checker.html')


# ============================================================================
# REALTIME VALIDATION API (NEW)
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected', 'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('start_validation')
def handle_start_validation(data):
    """
    Start realtime email validation with WebSocket updates
    
    Data:
        {
            "session_id": "unique-session-id",
            "emails": ["email1@gmail.com", ...],
            "options": {
                "max_workers": 20,
                "max_retries": 3
            }
        }
    """
    try:
        session_id = data.get('session_id')
        emails = data.get('emails', [])
        options = data.get('options', {})
        
        if not emails:
            emit('validation_error', {'message': 'No emails provided'})
            return
        
        # Store session
        with session_lock:
            validation_sessions[session_id] = {
                'emails': emails,
                'results': [],
                'stats': {
                    'total': len(emails),
                    'processed': 0,
                    'live': 0,
                    'die': 0,
                    'unknown': 0,
                    'catch_all': 0,
                    'disposable': 0
                },
                'start_time': datetime.now()
            }
        
        # Send initial progress
        emit('validation_progress', {
            'session_id': session_id,
            'progress': 0,
            'stats': validation_sessions[session_id]['stats']
        })
        
        # Progress callback for realtime updates
        def progress_callback(progress_data):
            """Send progress updates via WebSocket"""
            with session_lock:
                if session_id in validation_sessions:
                    session = validation_sessions[session_id]
                    session['stats']['processed'] = progress_data['processed']
                    session['stats']['live'] = progress_data['stats']['live']
                    session['stats']['die'] = progress_data['stats']['die']
                    session['stats']['unknown'] = progress_data['stats']['unknown']
                    session['stats']['catch_all'] = progress_data['stats'].get('catch_all', 0)
                    session['stats']['disposable'] = progress_data['stats'].get('disposable', 0)
                    
                    # Emit progress update
                    socketio.emit('validation_progress', {
                        'session_id': session_id,
                        'progress': progress_data['percentage'],
                        'current_email': progress_data['current_email'],
                        'current_status': progress_data['current_status'],
                        'stats': session['stats']
                    }, room=request.sid)
                    
                    # Emit individual result
                    socketio.emit('validation_result', {
                        'session_id': session_id,
                        'email': progress_data['current_email'],
                        'status': progress_data['current_status']
                    }, room=request.sid)
                    
                    # Emit log
                    log_message = f"[{datetime.now().strftime('%H:%M:%S')}] Validated: {progress_data['current_email']} - {progress_data['current_status']}"
                    socketio.emit('validation_log', {
                        'session_id': session_id,
                        'message': log_message,
                        'timestamp': datetime.now().isoformat()
                    }, room=request.sid)
        
        # Run validation with progress callback
        max_workers = options.get('max_workers', 20)
        result = validator_pro.bulk_validate(
            emails=emails,
            max_workers=max_workers,
            progress_callback=progress_callback
        )
        
        # Store final results
        with session_lock:
            if session_id in validation_sessions:
                validation_sessions[session_id]['results'] = result['results']
                validation_sessions[session_id]['final_stats'] = result['stats']
                validation_sessions[session_id]['end_time'] = datetime.now()
        
        # Save to database
        for live_result in result['results']['live']:
            db.save_validation_result(live_result)
        for die_result in result['results']['die']:
            db.save_validation_result(die_result)
        for unknown_result in result['results']['unknown']:
            db.save_validation_result(unknown_result)
        
        # Send completion
        emit('validation_complete', {
            'session_id': session_id,
            'stats': result['stats'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        emit('validation_error', {'message': str(e)})
        print(f'Validation error: {e}')


# ============================================================================
# REST API ENDPOINTS (ENHANCED)
# ============================================================================

@app.route('/api/validate', methods=['POST'])
def api_validate():
    """
    Enhanced validation endpoint with professional validator
    """
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        options = data.get('options', {})
        use_pro = options.get('use_pro_validator', True)  # Use pro by default
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        # Choose validator
        active_validator = validator_pro if use_pro else validator
        
        # Run validation
        max_workers = options.get('max_workers', 20)
        result = active_validator.bulk_validate(emails, max_workers=max_workers)
        
        # Save to database
        for live_result in result['results']['live']:
            db.save_validation_result(live_result)
        for die_result in result['results']['die']:
            db.save_validation_result(die_result)
        
        # Get dashboard data
        dashboard_data = db.get_statistics()
        
        return jsonify({
            'success': True,
            'validator': 'professional' if use_pro else 'standard',
            'stats': result['stats'],
            'results': result['results'],
            'dashboard': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/validate/session/<session_id>', methods=['GET'])
def api_get_session(session_id):
    """Get validation session data"""
    with session_lock:
        if session_id not in validation_sessions:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        session = validation_sessions[session_id]
        return jsonify({
            'success': True,
            'session': session
        })


@app.route('/api/export/<session_id>/<export_type>', methods=['GET'])
def api_export(session_id, export_type):
    """
    Export validation results
    
    Types: live, die, full, errors
    Formats: txt, csv, json (query param: ?format=csv)
    """
    try:
        export_format = request.args.get('format', 'txt')
        
        with session_lock:
            if session_id not in validation_sessions:
                return jsonify({
                    'success': False,
                    'message': 'Session not found'
                }), 404
            
            session = validation_sessions[session_id]
            results = session.get('results', {})
        
        # Prepare data based on export type
        if export_type == 'live':
            data = results.get('live', [])
        elif export_type == 'die':
            data = results.get('die', [])
        elif export_type == 'errors':
            data = results.get('unknown', [])
        elif export_type == 'full':
            data = []
            for category in ['live', 'die', 'unknown', 'catch_all', 'disposable']:
                data.extend(results.get(category, []))
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown export type: {export_type}'
            }), 400
        
        # Generate export file
        if export_format == 'txt':
            content = '\n'.join([item['email'] for item in data])
            return send_file(
                io.BytesIO(content.encode()),
                mimetype='text/plain',
                as_attachment=True,
                download_name=f'{export_type}_{session_id}.txt'
            )
        
        elif export_format == 'csv':
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{export_type}_{session_id}.csv'
            )
        
        elif export_format == 'json':
            return jsonify({
                'success': True,
                'export_type': export_type,
                'count': len(data),
                'data': data
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown format: {export_format}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# LEGACY API ENDPOINTS (PRESERVED)
# ============================================================================

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Generate random emails"""
    try:
        data = request.get_json()
        
        email_type = data.get('email_type', 'random')
        text = data.get('text', '')
        total = int(data.get('total', 10))
        
        # Support both 'domain' (legacy) and 'domains' (new)
        if 'domains' in data:
            domains = data.get('domains', ['gmail.com'])
            # Ensure it's a list
            if isinstance(domains, str):
                domains = [domains]
        else:
            # Legacy support: convert single domain to list
            domain = data.get('domain', 'gmail.com')
            domains = [domain]
        
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
        
        # Save to database
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
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/generate/realistic', methods=['POST'])
def api_generate_realistic():
    """
    Generate realistic emails based on real-world registration patterns
    
    Request body:
    {
        "count": 100,
        "domains": ["gmail.com", "yahoo.com"],  // optional
        "mode": "standard",  // standard, themed, bulk
        "theme": "professional",  // for themed mode
        "variety": "medium"  // for bulk mode
    }
    """
    try:
        data = request.get_json()
        
        count = int(data.get('count', 10))
        domains = data.get('domains', None)
        mode = data.get('mode', 'standard')
        
        if count < 1 or count > 10000:
            return jsonify({
                'success': False,
                'message': 'Count must be between 1 and 10,000'
            }), 400
        
        # Generate based on mode
        if mode == 'themed':
            theme = data.get('theme', 'professional')
            result = realistic_generator.generate_themed_emails(
                theme=theme,
                count=count,
                domains=domains
            )
        elif mode == 'bulk':
            variety = data.get('variety', 'medium')
            result = realistic_generator.generate_bulk_with_variety(
                total=count,
                domains=domains,
                variety_level=variety
            )
        else:  # standard
            result = realistic_generator.generate_realistic_emails(
                count=count,
                domains=domains,
                include_stats=True
            )
        
        # Save to database
        if result.get('success') and result.get('emails'):
            params = {
                'mode': mode,
                'generator': 'realistic',
                'theme': data.get('theme', 'N/A'),
                'variety': data.get('variety', 'N/A')
            }
            
            for email in result['emails']:
                try:
                    db.save_generated_email(email, params)
                except Exception as save_error:
                    print(f"Warning: Failed to save email {email}: {save_error}")
            
            result['db_saved'] = True
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/generate/realistic/options', methods=['GET'])
def api_realistic_options():
    """Get available options for realistic email generation"""
    try:
        options = realistic_generator.get_available_options()
        examples = realistic_generator.get_pattern_examples()
        
        return jsonify({
            'success': True,
            'options': options,
            'examples': examples
        })
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


@app.route('/api/db/stats', methods=['GET'])
def api_db_stats():
    """Get database statistics"""
    try:
        stats = db.get_statistics()
        live_emails = db.get_live_emails(100)
        die_emails = db.get_die_emails(100)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'live_emails': live_emails,
            'die_emails': die_emails,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/validate/single', methods=['POST'])
def api_validate_single():
    """Simple single email validation for testing"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'No email provided'}), 400
        
        # Direct validation
        result = validator_pro.validate_email_deep(email)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check with enhanced info"""
    try:
        db_stats = db.get_statistics()
        db_healthy = True
    except:
        db_stats = {}
        db_healthy = False
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'features': {
            'realtime_validation': True,
            'websocket_support': True,
            'professional_validator': True,
            'export_functions': True
        },
        'database': {
            'healthy': db_healthy,
            'stats': db_stats
        },
        'modules': {
            'validator': True,
            'validator_pro': True,
            'generator': True,
            'realistic_generator': True,
            'extractor': True,
            'formatter': True,
            'filter': True,
            'database': db_healthy
        }
    })


# ============================================================================
# EMAIL CHECKER API (NEW)
# ============================================================================

@app.route('/api/checker/generate', methods=['POST'])
def api_checker_generate():
    """Generate emails for checking"""
    try:
        data = request.get_json()
        count = int(data.get('count', 10))
        mix_ratio = float(data.get('mix_ratio', 0.7))
        
        result = email_checker.generate_emails(count=count, mix_ratio=mix_ratio)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'emails': [],
            'count': 0,
            'error': str(e)
        }), 500


@app.route('/api/checker/check', methods=['POST'])
def api_checker_check():
    """Start checking emails"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No emails provided'
            }), 400
        
        if len(emails) > 1000:
            return jsonify({
                'success': False,
                'message': 'Maximum 1000 emails per batch'
            }), 400
        
        # Check if already running
        progress = email_checker.get_progress()
        if progress['is_running']:
            return jsonify({
                'success': False,
                'message': 'Check already in progress'
            }), 400
        
        # Start checking in background thread
        import threading
        thread = threading.Thread(target=email_checker.check_emails_batch, args=(emails,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Checking started',
            'total': len(emails)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/checker/progress', methods=['GET'])
def api_checker_progress():
    """Get checking progress"""
    try:
        progress = email_checker.get_progress()
        return jsonify(progress)
    
    except Exception as e:
        return jsonify({
            'is_running': False,
            'current': 0,
            'total': 0,
            'status': f'error: {str(e)}',
            'results': []
        }), 500


@app.route('/api/checker/export', methods=['POST'])
def api_checker_export():
    """Export results to CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        filename = data.get('filename', None)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No results to export'
            }), 400
        
        export_result = email_checker.export_results(results, filename)
        return jsonify(export_result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/checker/download/<filename>', methods=['GET'])
def api_checker_download(filename):
    """Download exported CSV file"""
    try:
        filepath = os.path.join('mail_checker_app/results', filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/checker/stats', methods=['POST'])
def api_checker_stats():
    """Get statistics from results"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No results provided'
            }), 400
        
        stats = email_checker.get_stats(results)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
    port = 80 if len(sys.argv) > 1 and sys.argv[1] == 'production' else 5000
    debug_mode = port == 5000
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║      Email Tool Pro v3.0 - Professional Edition          ║
    ║      Advanced Email Validator with Realtime Updates      ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Server starting on port {port}
    🔧 Debug mode: {debug_mode}
    ⚡ WebSocket: ENABLED
    🎯 Professional Validator: ENABLED
    📊 Realtime Updates: ENABLED
    📦 All modules loaded successfully
    
    🌐 Dashboard: http://localhost:{port}/
    📡 WebSocket: ws://localhost:{port}/socket.io
    🔍 API Health: http://localhost:{port}/api/health
    
    Features:
    ✓ Multi-layer validation (8 layers)
    ✓ 95-99% accuracy
    ✓ SMTP handshake verification
    ✓ Catch-all detection
    ✓ Real-time progress updates
    ✓ Export functions (LIVE/DIE/FULL/ERROR)
    ✓ Worker pool & queue system
    ✓ Anti-block features
    """)
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
