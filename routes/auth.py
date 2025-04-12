from flask import *
from models import db
from models.sql.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/create_account", methods=['PUT'])
def create_account():
    """
    Create account.
    ---
    tags:
      - auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    description: Creates a new user.
    responses:
      201:
        description: Successfully created
        schema:
          type: object
          properties:
            message:
              type: string
            pass_key:
              type: string
            token:
              type: string
      400:
        description: Missing data or user already exists
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.get_json()
    username = data.get('email')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # check if username is a valid email
    if '@' not in username or '.' not in username.split('@')[-1]:
        return jsonify({"error": "Invalid email format"}), 400

    existing_user = User.query.filter_by(name=username).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(name=username)
    new_user.set_hashed_password(password)
    new_user.generate_hash256user()
    new_user.generate_token()
    new_user.generate_passkey()
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully","pass_key":new_user.pass_key,"token":new_user.token}), 201

@auth_bp.route("/forgot_password", methods=['POST'])
def forgot_password():
    """
    Recover password.
    ---
    tags:
      - auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            passkey:
              type: string
            new_password:
              type: string
    description: Resets the password of an existing account.
    responses:
      200:
        description: Password reset
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Missing data
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.get_json()
    username = data.get('username')
    passkey = data.get('passkey')
    new_password = data.get('new_password')

    if not username or not passkey or not new_password:
        return jsonify({"error": "Username, passkey and new password are required"}), 400

    user = User.query.filter_by(username=username, pass_key=passkey).first()
    if not user:
        return jsonify({"error": "Invalid username or passkey"}), 401

    user.set_hashed_password(new_password)
    user.generate_token()
    db.session.commit()


    return jsonify({"message": "Password updated successfully"}), 200


@auth_bp.route("/request_token",methods=['POST'])
def request_token():
    """
    Obtain token.
    ---
    tags:
      - auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    description: Generates an authentication token.
    responses:
      200:
        description: Token generated
        schema:
          type: object
          properties:
            token:
              type: string
      400:
        description: Missing data
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(name=username).first()
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    db.session.commit()
    return jsonify({"token": user.token}), 200


@auth_bp.route("/login",methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    user = User.query.filter_by(name=username).first()
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    session['uh'] = user.userhash
    return jsonify({"token": user.token}), 200

@auth_bp.route("/logout",methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200
