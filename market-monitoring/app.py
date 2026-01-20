#!/usr/bin/env python3
"""
Web Application for Financial News Monitoring System
Provides web interface for monitoring, configuration, and digest viewing
"""

import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import subprocess
from functools import wraps
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from database.db_manager import DatabaseManager
from scrapers.google_news import GoogleNewsScraper, ArticlePrioritizer
from emailer.digest import DigestGenerator

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize database
db = DatabaseManager(config.DATABASE_PATH)

# Simple user storage (in production, use a proper database)
USERS_FILE = 'users.json'

def load_users():
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes

@app.route('/')
@login_required
def index():
    """Dashboard home page"""
    stats = db.get_statistics()

    # Get recent articles
    recent_articles = db.get_recent_articles(hours=24)

    # Organize by priority
    priority_1 = [a for a in recent_articles if a['priority'] == 1]
    priority_2 = [a for a in recent_articles if a['priority'] == 2]
    priority_3 = [a for a in recent_articles if a['priority'] == 3]

    return render_template('dashboard.html',
                         stats=stats,
                         priority_1=priority_1[:5],
                         priority_2=priority_2[:5],
                         priority_3=priority_3[:5],
                         total_articles=len(recent_articles))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            session.permanent = True
            flash('Login successful!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        users = load_users()

        if username in users:
            flash('Username already exists', 'error')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            save_users(users)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/articles')
@login_required
def articles():
    """View all articles"""
    hours = request.args.get('hours', 24, type=int)
    priority = request.args.get('priority', type=int)
    asset_class = request.args.get('asset_class')

    if priority:
        articles_list = db.get_articles_by_priority(priority, hours)
    elif asset_class:
        articles_list = db.get_articles_by_asset_class(asset_class, hours)
    else:
        articles_list = db.get_recent_articles(hours)

    return render_template('articles.html',
                         articles=articles_list,
                         hours=hours,
                         asset_classes=config.ASSET_CLASSES,
                         selected_priority=priority,
                         selected_asset_class=asset_class)

@app.route('/digests')
@login_required
def digests():
    """View digest history"""
    output_dir = Path(config.OUTPUT_DIR)
    digest_files = []

    if output_dir.exists():
        for file in sorted(output_dir.glob('digest_*.html'), reverse=True):
            stat = file.stat()
            digest_files.append({
                'name': file.name,
                'path': str(file),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
            })

    return render_template('digests.html', digests=digest_files)

@app.route('/digest/<filename>')
@login_required
def view_digest(filename):
    """View a specific digest"""
    digest_path = Path(config.OUTPUT_DIR) / filename

    if digest_path.exists() and digest_path.suffix == '.html':
        return send_file(digest_path)
    else:
        flash('Digest not found', 'error')
        return redirect(url_for('digests'))

@app.route('/run-monitoring', methods=['POST'])
@login_required
def run_monitoring():
    """Run the monitoring script"""
    try:
        # Run monitor.py as subprocess
        result = subprocess.run(
            [sys.executable, 'monitor.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Monitoring completed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Monitoring failed',
                'error': result.stderr
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Monitoring timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/config')
@login_required
def configuration():
    """Configuration page"""
    return render_template('config.html',
                         asset_classes=config.ASSET_CLASSES,
                         priority_funds=config.PRIORITY_FUNDS,
                         lookback_hours=config.NEWS_LOOKBACK_HOURS,
                         max_articles=config.MAX_ARTICLES_PER_ASSET_CLASS,
                         deal_threshold=config.PRIORITY_DEAL_THRESHOLD,
                         fund_close_threshold=config.PRIORITY_FUND_CLOSE_THRESHOLD)

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for statistics"""
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/test-scraper', methods=['POST'])
@login_required
def test_scraper():
    """Test the news scraper with a simple query"""
    try:
        scraper = GoogleNewsScraper(lookback_hours=24, max_results=5)
        query = request.json.get('query', 'private equity')

        articles = scraper.search_news(query)

        return jsonify({
            'success': True,
            'count': len(articles),
            'articles': [{
                'title': a.title,
                'source': a.source,
                'url': a.url
            } for a in articles[:5]]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/about')
@login_required
def about():
    """About page"""
    return render_template('about.html',
                         version='1.0.0',
                         asset_classes=config.ASSET_CLASSES,
                         priority_funds=config.PRIORITY_FUNDS)

# Error handlers

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500

# Initialize default admin user
def init_default_user():
    """Create default admin user if no users exist"""
    users = load_users()
    if not users:
        users['admin'] = {
            'password': generate_password_hash('admin123'),
            'email': 'admin@example.com',
            'created_at': datetime.now().isoformat()
        }
        save_users(users)
        print("✓ Default user created: admin / admin123")
        print("⚠️  Please change the password after first login!")

if __name__ == '__main__':
    init_default_user()

    # Get port from environment or use 5000
    port = int(os.environ.get('PORT', 5000))

    print("=" * 60)
    print("Financial News Monitoring System - Web Interface")
    print("=" * 60)
    print(f"Server starting on http://localhost:{port}")
    print()
    print("Default credentials (change after first login):")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
