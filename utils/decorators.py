from flask import request,jsonify,g,session,redirect
from functools import wraps
from models.sql.user import User
from flask_socketio import emit
authenticated_sessions = {}
def verify_token():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Unauthorized, missing or invalid Authorization header"}), 401

            token = auth_header.split(' ')[1]
            user = User.query.filter_by(token=token).first()
            if not user:
                return jsonify({"error": "Unauthorized, invalid token"}), 401
            g.user = user


            return f(*args, **kwargs)

        return decorated_function

    return decorator
def authenticated_only(f):
    @wraps(f)
    def wrapped(data, *args, **kwargs):
        session_id = data.get('session_id') if isinstance(data, dict) else None
        if session_id not in authenticated_sessions:
            emit('error', {'message': 'Authentication required'})
            return
        data['user'] = authenticated_sessions[session_id]
        return f(data, *args, **kwargs)
    return wrapped

def frontend_login(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user_hash = session.get('uh')
        if not user_hash:
            return redirect('/login')
        user = User.query.filter_by(userhash=user_hash).first()
        if not user:
            return redirect('/login')
        g.user = user
        return f(*args, **kwargs)
    return wrapped

