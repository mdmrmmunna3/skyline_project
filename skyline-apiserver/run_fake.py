from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/auth/tokens', methods=['POST'])
def login():
    return jsonify({"token": "test"})

print("Backend: http://localhost:28000")
app.run(port=28000)
