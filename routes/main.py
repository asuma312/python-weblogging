from flask import *
from utils.decorators import frontend_login
main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route("/register")
def register():
    return render_template("register.html")

@main_bp.route("/login")
def login():
    return render_template("login.html")

@main_bp.route("/dashboard")
@frontend_login
def dashboard():
    return jsonify(logged='voce ta logado')