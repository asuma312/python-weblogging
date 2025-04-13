from flask import *
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from models import db
from flasgger import Swagger
load_dotenv()


socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SQLITE_DBPATH'] = app.root_path + os.getenv('USERS_LOGDB_PATH')
    app.config['JWT_SECRET_TOKEN'] = os.getenv('JWT_SECRET_TOKEN')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    for key in os.environ.keys():
        app.config[key] = os.environ[key]

    #import models for sqlalchemy
    from models.sql.user import User

    with app.app_context():
        db.init_app(app)
        db.create_all()
        if not os.path.exists(app.config['SQLITE_DBPATH']):
            os.makedirs(app.config['SQLITE_DBPATH'])

    socketio.init_app(app, cors_allowed_origins="*")
    
    from events.logs import register_logs_events
    from events.auth import register_auth_events
    
    register_logs_events(socketio)
    register_auth_events(socketio)

    from routes.logs import logs_bp
    from routes.auth import auth_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)

    app.register_blueprint(logs_bp, url_prefix='/api/v1/logs')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    swagger = Swagger(app)


    @app.route("/debug")
    def debug():
        return render_template("debug.html")
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=1234, debug=True,allow_unsafe_werkzeug=True)
