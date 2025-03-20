from flask import jsonify, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, db
import jwt
import datetime
from functools import wraps
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def login():
    auth = request.get_json()

    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401

    user = User.query.filter_by(email=auth.get('email')).first()

    if not user:
        return jsonify({'message': 'User not found!'}), 401

    if check_password_hash(user.password_hash, auth.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, Config.SECRET_KEY)

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        })

    return jsonify({'message': 'Invalid credentials!'}), 401

def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'message': 'Missing required fields!'}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'User already exists!'}), 400

    hashed_password = generate_password_hash(data.get('password'))
    
    new_user = User(
        email=data.get('email'),
        username=data.get('username'),
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode({
        'user_id': new_user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, Config.SECRET_KEY)

    return jsonify({
        'message': 'User created successfully!',
        'token': token,
        'user': {
            'id': new_user.id,
            'email': new_user.email,
            'username': new_user.username
        }
    }), 201

def logout():
    logout_user()
    return jsonify({'message': 'Successfully logged out!'}), 200

def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({'message': 'Not logged in!'}), 401
    
    return jsonify({
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username
        }
    }) 