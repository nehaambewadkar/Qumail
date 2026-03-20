"""
QuMail Web Server
Main Flask application with REST API endpoints.
"""

import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory

from app.controller import QuMailController
from email_client.imap_client import IMAPClient
from config.settings import FLASK_HOST, FLASK_PORT

app = Flask(__name__, static_folder='web', static_url_path='/static')

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

controller = QuMailController()

# ── Static Files ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

# ── Key Manager API ───────────────────────────────────────────────────────────

@app.route('/api/v1/km/status', methods=['GET'])
def km_status():
    return jsonify(controller.km_status())

@app.route('/api/v1/km/replenish', methods=['POST'])
def km_replenish():
    from km_client.etsi_qkd_client import ETSIQKDClient
    client = ETSIQKDClient()
    result = client.replenish_keys(20)
    return jsonify(result)

# ── Send Email ────────────────────────────────────────────────────────────────

@app.route('/api/v1/send', methods=['POST'])
def send_email():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No JSON body provided"}), 400

    required = ['sender_email', 'app_password', 'recipient', 'subject', 'message']
    for field in required:
        if not data.get(field, '').strip():
            return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

    result = controller.send_secure_email(
        sender_email=data['sender_email'].strip(),
        app_password=data['app_password'].strip(),
        recipient=data['recipient'].strip(),
        subject=data['subject'].strip(),
        message=data['message'].strip(),
        security_level=data.get('security_level', 'QUANTUM_AES'),
    )
    return jsonify(result)

# ── Decrypt Email ─────────────────────────────────────────────────────────────

@app.route('/api/v1/decrypt', methods=['POST'])
def decrypt_email():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No JSON body"}), 400

    email_body = data.get('email_body', '').strip()
    key_hex = data.get('key_hex', '').strip()

    if not email_body or not key_hex:
        return jsonify({"success": False, "message": "email_body and key_hex required"}), 400

    # Use IMAPClient's decrypt logic
    imap = IMAPClient('', '')
    result = imap.decrypt_email(email_body, key_hex)
    return jsonify(result)

# ── Fetch Inbox ───────────────────────────────────────────────────────────────

@app.route('/api/v1/inbox', methods=['POST'])
def fetch_inbox():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No JSON body", "emails": []}), 400

    email_addr = data.get('email', '').strip()
    app_password = data.get('app_password', '').strip()

    if not email_addr or not app_password:
        return jsonify({"success": False, "message": "email and app_password required", "emails": []}), 400

    imap = IMAPClient(email_addr, app_password)
    result = imap.fetch_inbox(limit=15)
    return jsonify(result)

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 QuMail Web Server Starting...")
    print("=" * 70)
    print()
    print(f"  📧 Web Interface:   http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"  🔑 Key Manager API: http://{FLASK_HOST}:{FLASK_PORT}/api/v1/km/status")
    print()
    print("  Press CTRL+C to stop")
    print("=" * 70)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
