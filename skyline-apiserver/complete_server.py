from flask import Flask, jsonify, request, send_from_directory
import os
import json

app = Flask(__name__, static_folder=None)

# Manual CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Frontend directory
FRONTEND_DIR = '/mnt/c/xampp/htdocs/PCL_Project/OpneStack/skyline-console/skyline_console/static'

# ============ API ENDPOINTS ============
@app.route('/api/openstack/skyline/api/v1/login', methods=['POST', 'OPTIONS'])
def skyline_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    print("✅ Login request received")
    
    # Skyline-console specific response
    return jsonify({
        "success": True,
        "data": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.test_token_123",
            "user": {
                "id": "1",
                "name": "admin",
                "email": "admin@example.com",
                "roles": ["admin", "_member_"],
                "permissions": ["*"]
            },
            "project": {
                "id": "1",
                "name": "admin",
                "domain_id": "default"
            },
            "catalog": [],
            "expires_at": "2024-12-31T23:59:59.999999Z"
        }
    })

# OpenStack compatible endpoints
@app.route('/api/auth/tokens', methods=['POST', 'OPTIONS'])
def keystone_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "token": {
            "id": "gAAAAABkeystone_token",
            "user": {"name": "admin", "id": "1"},
            "project": {"name": "admin", "id": "1"}
        }
    })

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

# Version
@app.route('/api/version', methods=['GET'])
def version():
    return jsonify({"version": "2024.1"})

# ============ FRONTEND SERVING ============
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Check if it's an API call
    if path.startswith('api/'):
        # Return mock API response
        return jsonify({
            "success": True,
            "endpoint": path,
            "message": "Mock API response"
        })
    
    # Serve static files
    if path == '':
        file_path = 'index.html'
    else:
        file_path = path
    
    full_path = os.path.join(FRONTEND_DIR, file_path)
    
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, file_path)
    
    # For React routing, fallback to index.html
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 COMPLETE SKYLINE SERVER")
    print("📍 http://127.0.0.1:8088")
    print("🔗 Login endpoint: /api/openstack/skyline/api/v1/login")
    print("👤 Username: ANYTHING")
    print("🔒 Password: ANYTHING")
    print("="*70 + "\n")
    
    # Test endpoint
    print("Test login with:")
    print('curl -X POST http://127.0.0.1:8088/api/openstack/skyline/api/v1/login \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username":"admin","password":"admin"}\'')
    print()
    
    app.run(host='127.0.0.1', port=8088, debug=True, threaded=True)
