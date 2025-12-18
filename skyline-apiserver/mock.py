from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/api/openstack/skyline/api/v1/login', methods=['POST'])
def login():
    return jsonify({
        "success": True,
        "data": {"token": "test", "user": {"name": "admin"}}
    })
@app.route('/<path:path>')
def serve(path):
    from flask import send_from_directory
    import os
    return send_from_directory('/mnt/c/xampp/htdocs/PCL_Project/OpneStack/skyline-console/skyline_console/static', path or 'index.html')
if __name__ == '__main__':
    print("Server: http://127.0.0.1:8088")
    app.run(port=8088, debug=True)
