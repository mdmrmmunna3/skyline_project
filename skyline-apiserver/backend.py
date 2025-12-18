# from flask import Flask, jsonify
# from flask_cors import CORS

# app = Flask(__name__)

# CORS(
#     app,
#     supports_credentials=True,
#     # origins=["http://localhost:3000"]
#     origins=["http://127.0.0.1:8088"]
# )


# # =================================================================
# # ১. Authentication & User Info Routes
# # =================================================================

# @app.route('/api/v1/login', methods=['POST'])
# def login():
#     return jsonify({
#         "success": True,
#         "data": {"token": "test123", "user": {"name": "admin", "password" : "admin"}}
#     })

# @app.route('/api/v1/profile', methods=['GET'])
# def profile():
#     return jsonify({
#         "name": "admin",
#         "email": "admin@example.com",
#         "id": "1",
#     })

# @app.route('/api/v1/policies', methods=['GET'])
# def policies():
#     return jsonify({
#         "isAdmin": True,
#         "canViewDashboard": True,
#     })

# @app.route('/api/v1/user_info', methods=['GET'])
# def user_info():
#     return jsonify({
#         "username": "admin",
#         "user_id": "1",
#         "domain_id": "default",
#         "project_id": "tenant1"
#     })

# # =================================================================
# # ২. ড্যাশবোর্ড লোডিং এর জন্য প্রাথমিক ডেটা (skyline API)
# # =================================================================

# @app.route('/api/v1/projects', methods=['GET'])
# def projects():
#     return jsonify({
#         "data": [{"id": "tenant1", "name": "demo_project"}]
#     })

# @app.route('/api/v1/domains', methods=['GET'])
# def domains():
#     return jsonify({
#         "data": [{"id": "default", "name": "Default"}]
#     })

# @app.route('/api/v1/users', methods=['GET'])
# def users():
#     return jsonify({
#         "data": [{"id": "user1", "name": "admin"}]
#     })

# @app.route('/api/v1/available_regions', methods=['GET'])
# def regions():
#     return jsonify({
#         "data": [{"id": "RegionOne", "name": "Region One"}]
#     })

# # =================================================================
# # ৩. ড্যাশবোর্ড রিসোর্স কাউন্ট এবং অন্যান্য রুট (Nova, Neutron, Glance, Cinder APIs)
# # =================================================================

# @app.route('/api/v1/servers/count', methods=['GET'])
# def server_count():
#     return jsonify({"count": 5})

# @app.route('/api/v1/networks/count', methods=['GET'])
# def network_count():
#     return jsonify({"count": 10})

# @app.route('/api/v1/images/count', methods=['GET'])
# def image_count():
#     return jsonify({"count": 2})

# @app.route('/api/v1/flavors', methods=['GET'])
# def flavors():
#     return jsonify({
#         "data": [{"id": "1", "name": "m1.tiny"}]
#     })

# @app.route('/api/v1/security_groups', methods=['GET'])
# def security_groups():
#     return jsonify({
#         "data": [{"id": "sg1", "name": "default"}]
#     })

# @app.route('/api/v1/qos_specs', methods=['GET'])
# def qos_specs():
#     return jsonify({
#         "data": []
#     })

# # =================================================================
# # ৪. 404 ত্রুটি ঠিক করার জন্য অনুপস্থিত রুট (সরাসরি v3/v2.0 কল)
# # =================================================================

# @app.route('/v3/system/users/roles', methods=['GET'])
# def system_users_roles():
#     return jsonify({
#         "role_assignments": [
#             {"role": {"id": "admin", "name": "admin"}, "scope": {"system": {"all": True}}}
#         ]
#     })

# @app.route('/v2.0/extensions', methods=['GET'])
# def extensions():
#     return jsonify({
#         "extensions": [] 
#     })

# # =================================================================
# # ৫. সার্ভার রান করা (শুধুমাত্র একবার)
# # =================================================================

# print("✅ Backend: http://0.0.0.0:28000")
# app.run(host='0.0.0.0', port=28000)
# # print("✅ Backend: http://127.0.0.1:9999")
# # app.run(host='0.0.0.0', port=9999)
