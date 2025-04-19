from flask import *
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from models import db
from flasgger import Swagger
from flask_session import Session

load_dotenv()


socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SQLITE_DBPATH'] = os.getenv('USERS_LOGDB_PATH')
    app.config['JWT_SECRET_TOKEN'] = os.getenv('JWT_SECRET_TOKEN')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    for key in os.environ.keys():
        app.config[key] = os.environ[key]

    with app.app_context():
        db.init_app(app)
        db.create_all()
        if not os.path.exists(app.config['SQLITE_DBPATH']):
            os.makedirs(app.config['SQLITE_DBPATH'])

    socketio.init_app(app, cors_allowed_origins="*")
    socketio.app = app

    from routes.api.logs import logs_bp
    from routes.api.auth import auth_bp
    from routes.main import main_bp
    from routes.api.frontend import frontendapi_bp

    app.register_blueprint(main_bp)
    app.config['socketio'] = socketio

    app.register_blueprint(logs_bp, url_prefix='/api/v1/logs')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(frontendapi_bp, url_prefix='/api/v1/frontend')
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "PyWebLog API",
            "description": "API para PyWebLog.",
            "contact": {
                "email": "asuma312@gmail.com"
            },
            "version": "1.0"
        },
        "schemes": [
            "http",
            "https"
        ],
        "uiConfig": {
            "docExpansion": "none",
            "deepLinking": False
        }
    }

    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    #change for redis in prod
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    server_session = Session(app)


    @app.route("/debug")
    def debug():
        return render_template("debug.html")
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=1234, debug=True, allow_unsafe_werkzeug=True)

