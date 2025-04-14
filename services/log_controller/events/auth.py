from flask import current_app
from flask_socketio import emit, disconnect
from models import db
from models.sql.user import User
from utils.decorators import authenticated_sessions




def register_auth_events(socketio):
    @socketio.on('create_account')
    def handle_create_account(data):
        """
        Cria uma nova conta de usuário.
        """
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return emit('create_account_response', {"error": "Username and password are required"})

        existing_user = User.query.filter_by(name=username).first()
        if existing_user:
            return emit('create_account_response', {"error": "User already exists"})

        new_user = User(name=username)
        new_user.set_hashed_password(password)
        new_user.generate_hash256user()
        new_user.generate_token()
        new_user.generate_passkey()
        db.session.add(new_user)
        db.session.commit()

        emit('create_account_response', {
            "message": "User created successfully",
            "pass_key": new_user.pass_key,
            "token": new_user.token
        })

    @socketio.on('forgot_password')
    def handle_forgot_password(data):
        """
        Troca a senha pelo passkey
        """
        username = data.get('username')
        passkey = data.get('passkey')
        new_password = data.get('new_password')

        if not username or not passkey or not new_password:
            return emit('forgot_password_response', {"error": "Username, passkey and new password are required"})

        user = User.query.filter_by(name=username, pass_key=passkey).first()
        if not user:
            return emit('forgot_password_response', {"error": "Invalid username or passkey"})

        user.set_hashed_password(new_password)
        db.session.commit()

        emit('forgot_password_response', {"message": "Password updated successfully"})

    @socketio.on('login')
    def handle_login(data):
        """
        Autentica um usuário e armazena a sessão.
        """
        username = data.get('username')
        password = data.get('password')
        session_id = data.get('session_id')

        if not username or not password or not session_id:
            return emit('login_response', {"error": "Username, password and session_id are required"})

        user = User.query.filter_by(name=username).first()
        if not user or not user.verify_password(password):
            return emit('login_response', {"error": "Invalid credentials"})
        
        user.generate_token()
        db.session.commit()
        
        authenticated_sessions[session_id] = user
        
        emit('login_response', {"status": "success", "token": user.token})
    
    @socketio.on('logout')
    def handle_logout(data):
        """
        Desconecta um usuário.
        """
        session_id = data.get('session_id')
        if session_id in authenticated_sessions:
            del authenticated_sessions[session_id]
            emit('logout_response', {"status": "success", "message": "Logged out successfully"})
        else:
            emit('logout_response', {"status": "error", "message": "Not logged in"})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """
        Limpa a sessão quando o cliente desconectar.
        """
        #TODO implementar disconnect from client
        pass
