from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
import json
from database import (
    register_user, login_user, get_user_by_id, 
    get_all_properties, get_property_reviews, 
    add_review, get_property_rating
)

app = Flask(__name__, static_folder='.')
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)  # For session management

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    result = register_user(username, email, password)
    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Missing username or password"}), 400
    
    result = login_user(username, password)
    if result["success"]:
        session['user_id'] = result["user_id"]
        session['username'] = result["username"]
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True}), 200

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    user_id = session.get('user_id')
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({"authenticated": True, "user": user}), 200
    
    return jsonify({"authenticated": False}), 401

# Property endpoints
@app.route('/api/properties', methods=['GET'])
def get_properties():
    properties = get_all_properties()
    for prop in properties:
        prop['rating'] = get_property_rating(prop['id'])
    
    return jsonify(properties), 200

@app.route('/api/properties/<int:property_id>/reviews', methods=['GET'])
def get_reviews(property_id):
    reviews = get_property_reviews(property_id)
    return jsonify(reviews), 200

@app.route('/api/properties/<int:property_id>/reviews', methods=['POST'])
def create_review(property_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    data = request.json
    rating = data.get('rating')
    review_text = data.get('review')
    
    if not rating or not review_text:
        return jsonify({"success": False, "error": "Missing rating or review text"}), 400
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Invalid rating format"}), 400
    
    review_id = add_review(property_id, user_id, rating, review_text)
    return jsonify({"success": True, "review_id": review_id}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000) 