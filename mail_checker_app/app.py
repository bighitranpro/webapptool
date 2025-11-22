"""
Flask Web Application - Email Checker
Kiểm tra email SMTP, Facebook, và dự đoán quốc gia
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

# Import các module checker
from checkers.email_generator import generate_emails, get_email_info
from checkers.smtp_checker import SMTPChecker
from checkers.fb_checker import FacebookChecker
from checkers.geo_locator import GeoLocator
from utils.exporter import ResultExporter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['RESULTS_FOLDER'] = 'results'

# Initialize checkers
smtp_checker = SMTPChecker(timeout=10)
fb_checker = FacebookChecker(timeout=10, delay=0.5)
geo_locator = GeoLocator()
exporter = ResultExporter(output_dir=app.config['RESULTS_FOLDER'])

# Global variable to store checking progress
checking_progress = {
    'is_running': False,
    'current': 0,
    'total': 0,
    'results': [],
    'status': 'idle'
}
progress_lock = threading.Lock()


def calculate_overall_score(smtp_result, fb_result, geo_result):
    """
    Tính điểm tổng hợp cho email
    
    Score breakdown:
    - SMTP LIVE: 40 points
    - Has Facebook: 30 points
    - Country confidence: 30 points
    
    Returns:
        float: Score from 0.0 to 1.0
    """
    score = 0.0
    
    # SMTP status (40%)
    if smtp_result.get('status') == 'LIVE':
        score += 0.40
    elif smtp_result.get('status') == 'UNKNOWN':
        score += 0.20
    
    # Facebook (30%)
    if fb_result.get('has_facebook'):
        score += 0.30 * fb_result.get('confidence', 0.5)
    
    # Country confidence (30%)
    score += 0.30 * geo_result.get('confidence', 0.0)
    
    return round(score, 2)


def check_email_complete(email):
    """
    Kiểm tra toàn bộ thông tin của 1 email
    
    Returns:
        dict: Complete result
    """
    # Check SMTP
    smtp_result = smtp_checker.check_smtp_single(email)
    
    # Check Facebook (chỉ check nếu SMTP LIVE hoặc UNKNOWN)
    fb_result = {'has_facebook': False, 'confidence': 0.0, 'error': 'Skipped'}
    if smtp_result['status'] in ['LIVE', 'UNKNOWN']:
        fb_result = fb_checker.check_facebook_single(email)
    
    # Predict country
    geo_result = geo_locator.analyze_email(email)
    
    # Calculate overall score
    score = calculate_overall_score(smtp_result, fb_result, geo_result)
    
    # Combine results
    result = {
        'email': email,
        'smtp_status': smtp_result['status'],
        'smtp_error': smtp_result.get('error', ''),
        'mx_records': smtp_result.get('mx_records', []),
        'has_facebook': fb_result.get('has_facebook', False),
        'fb_confidence': fb_result.get('confidence', 0.0),
        'fb_error': fb_result.get('error', ''),
        'country': geo_result['country'],
        'country_confidence': geo_result['confidence'],
        'score': score,
        'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return result


def check_emails_batch(emails, update_progress=True):
    """
    Check nhiều email với progress tracking
    
    Args:
        emails: List of email addresses
        update_progress: Whether to update global progress
    
    Returns:
        list: Results
    """
    global checking_progress
    
    results = []
    total = len(emails)
    
    if update_progress:
        with progress_lock:
            checking_progress['is_running'] = True
            checking_progress['current'] = 0
            checking_progress['total'] = total
            checking_progress['results'] = []
            checking_progress['status'] = 'running'
    
    try:
        for i, email in enumerate(emails):
            result = check_email_complete(email)
            results.append(result)
            
            if update_progress:
                with progress_lock:
                    checking_progress['current'] = i + 1
                    checking_progress['results'].append(result)
        
        if update_progress:
            with progress_lock:
                checking_progress['status'] = 'completed'
    
    except Exception as e:
        if update_progress:
            with progress_lock:
                checking_progress['status'] = f'error: {str(e)}'
    
    finally:
        if update_progress:
            with progress_lock:
                checking_progress['is_running'] = False
    
    return results


@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate email addresses
    
    POST data:
        count: Number of emails to generate
        mix_ratio: Ratio of Vietnamese emails (0.0-1.0)
    """
    try:
        data = request.get_json()
        count = int(data.get('count', 10))
        mix_ratio = float(data.get('mix_ratio', 0.7))
        
        # Validate
        if count < 1 or count > 1000:
            return jsonify({'error': 'Count must be between 1 and 1000'}), 400
        
        if mix_ratio < 0 or mix_ratio > 1:
            return jsonify({'error': 'Mix ratio must be between 0.0 and 1.0'}), 400
        
        # Generate emails
        emails = generate_emails(count=count, mix_ratio=mix_ratio)
        
        return jsonify({
            'success': True,
            'emails': emails,
            'count': len(emails)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/check', methods=['POST'])
def check():
    """
    Start checking emails
    
    POST data:
        emails: List of email addresses
    """
    global checking_progress
    
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({'error': 'No emails provided'}), 400
        
        if len(emails) > 1000:
            return jsonify({'error': 'Maximum 1000 emails per batch'}), 400
        
        # Check if already running
        with progress_lock:
            if checking_progress['is_running']:
                return jsonify({'error': 'Check already in progress'}), 400
        
        # Start checking in background thread
        thread = threading.Thread(target=check_emails_batch, args=(emails,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Checking started',
            'total': len(emails)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/progress', methods=['GET'])
def progress():
    """Get checking progress"""
    with progress_lock:
        return jsonify({
            'is_running': checking_progress['is_running'],
            'current': checking_progress['current'],
            'total': checking_progress['total'],
            'status': checking_progress['status'],
            'results': checking_progress['results']
        })


@app.route('/export', methods=['POST'])
def export():
    """
    Export results to CSV
    
    POST data:
        results: List of result objects
        filename: Optional custom filename
    """
    try:
        data = request.get_json()
        results = data.get('results', [])
        filename = data.get('filename', None)
        
        if not results:
            return jsonify({'error': 'No results to export'}), 400
        
        # Export to CSV
        filepath = exporter.export_detailed_csv(results, filename)
        
        # Get stats
        stats = exporter.get_export_stats(results)
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    """Download exported CSV file"""
    try:
        filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/files', methods=['GET'])
def list_files():
    """List all exported CSV files"""
    try:
        files = exporter.list_exports()
        
        file_info = []
        for f in files:
            filepath = os.path.join(app.config['RESULTS_FOLDER'], f)
            size = os.path.getsize(filepath)
            mtime = os.path.getmtime(filepath)
            
            file_info.append({
                'filename': f,
                'size': size,
                'modified': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'files': file_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['POST'])
def stats():
    """Get statistics from results"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'No results provided'}), 400
        
        stats = exporter.get_export_stats(results)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Tạo thư mục results nếu chưa có
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Run app
    app.run(host='0.0.0.0', port=8000, debug=True)
