from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/openstack/skyline/api/v1/login', methods=['POST'])
def login():
    return jsonify({
        "success": True,
        "data": {"token": "test123", "user": {"name": "admin"}}
    })

# print("✅ Backend: http://127.0.0.1:28000")
print("✅ Backend: http://0.0.0.0:28000")
app.run(port=28000)
