from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__)

# Add CORS headers manually
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/api/openstack/skyline/api/v1/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"Login attempt with: {request.json}")
    
    # ALWAYS SUCCESS
    return jsonify({
        "success": True,
        "data": {
            "token": "skyline_jwt_token_123456",
            "user": {
                "id": "1",
                "name": "admin",
                "email": "admin@example.com",
                "roles": ["admin"]
            }
        }
    })

# Serve frontend files
FRONTEND_DIR = '/mnt/c/xampp/htdocs/PCL_Project/OpneStack/skyline-console/skyline_console/static'

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    # Fallback to index.html for React routing
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    print("="*60)
    print("🚀 SIMPLE SKYLINE SERVER")
    print("📍 http://127.0.0.1:8088")
    print("🔑 Login with ANY credentials")
    print("="*60)
    app.run(host='127.0.0.1', port=8088, debug=True)
