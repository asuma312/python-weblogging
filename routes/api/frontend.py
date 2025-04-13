from flask import *
from utils.path import get_user_path
from utils.decorators import frontend_login
from models.sql.email_config import EmailToContact
from models import db
import os
from models.dataclasses.logtypes import LOGTYPES
from app import socketio


frontendapi_bp = Blueprint('frontend', __name__)


@frontendapi_bp.route("/delete_logdb",methods=['DELETE'])
@frontend_login
def delete_logdb():
    user = g.user
    data = request.get_json()
    log_name = data.get("log_name", 'default')
    if not log_name:
        return jsonify({'status':'error','message':'log_name is required'}),400
    if not isinstance(log_name, str):
        return jsonify({'status':'error','message':'log_name must be a string'}),400
    if len(log_name) > 50:
        return jsonify({'status':'error','message':'log_name must be less than 50 characters'}),400
    user_path = get_user_path(user)
    db = os.path.join(user_path, f"log_{log_name}.sqlite")
    if not os.path.exists(db):
        return jsonify({'status':'error','message':'log_name not found'}),400
    try:
        os.remove(db)
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}),400
    return jsonify({'status':'success','message':'log_name deleted'}),200

@frontendapi_bp.route("/add_email",methods=['PUT'])
@frontend_login
def add_email():
    user = g.user
    data = request.get_json()
    email = data.get("email")
    notifications = data.get("notifications", [])
    LOGTYPES_VAL = [
        LOGTYPES.ERROR,
        LOGTYPES.CRITICAL,
        LOGTYPES.FAILURE
    ]

    if not all(notification in [log.value for log in LOGTYPES_VAL] for notification in notifications):
        return jsonify({'status':'error','message':'log type is invalid'}),400
    
    if not email:
        return jsonify({'status':'error','message':'email is required'}),400
    if not isinstance(email, str):
        return jsonify({'status':'error','message':'email must be a string'}),400
    if len(email) > 50:
        return jsonify({'status':'error','message':'email must be less than 50 characters'}),400

    user_emails = EmailToContact.query.filter_by(userhash=user.userhash).count()
    if user_emails >= int(current_app.config['USER_EMAILS_MAX']):
        return jsonify({'status':'error','message':'user emails limit exceeded'}),400
    
    email_config = EmailToContact.query.filter_by(email=email,userhash=user.userhash).first()

    if not email_config:
        email_config = EmailToContact(
            userhash=user.userhash,
            email=email,
            notifications=','.join(notifications)
        )
    else:
        email_config.notifications = ','.join(notifications)
        
    db.session.add(email_config)
    db.session.commit()
    return jsonify({'status':'success','message':'email added'}),200

@frontendapi_bp.route("/delete_email",methods=['DELETE'])
@frontend_login
def delete_email():
    user = g.user
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({'status':'error','message':'email is required'}),400
    if not isinstance(email, str):
        return jsonify({'status':'error','message':'email must be a string'}),400
    if len(email) > 50:
        return jsonify({'status':'error','message':'email must be less than 50 characters'}),400
    email_config = EmailToContact.query.filter_by(email=email,userhash=user.userhash).first()
    if not email_config:
        return jsonify({'status':'error','message':'email not found'}),400
    db.session.delete(email_config)
    db.session.commit()
    return jsonify({'status':'success','message':'email deleted'}),200

@frontendapi_bp.route("/edit_email",methods=['POST'])
@frontend_login
def edit_email():
    user = g.user
    data = request.get_json()
    old_email = data.get("old_email")
    new_email = data.get("new_email")
    notifications = data.get("notifications", [])
    LOGTYPES_VAL = [
        LOGTYPES.ERROR,
        LOGTYPES.CRITICAL,
        LOGTYPES.FAILURE
    ]

    if not all(notification in [log.value for log in LOGTYPES_VAL] for notification in notifications):
        return jsonify({'status':'error','message':'log type is invalid'}),400
    
    if not old_email:
        return jsonify({'status':'error','message':'old_email is required'}),400
    if not isinstance(old_email, str):
        return jsonify({'status':'error','message':'old_email must be a string'}),400
    if len(old_email) > 50:
        return jsonify({'status':'error','message':'old_email must be less than 50 characters'}),400
    if not new_email:
        return jsonify({'status':'error','message':'new_email is required'}),400
    if not isinstance(new_email, str):
        return jsonify({'status':'error','message':'new_email must be a string'}),400
    if len(new_email) > 50:
        return jsonify({'status':'error','message':'new_email must be less than 50 characters'}),400
    
    email_config = EmailToContact.query.filter_by(email=old_email,userhash=user.userhash).first()
    if not email_config:
        return jsonify({'status':'error','message':'email not found'}),400
    
    email_config.email = new_email
    email_config.notifications = ','.join(notifications)
    
    db.session.commit()
    return jsonify({'status':'success','message':'email edited'}),200


@frontendapi_bp.route("/get_uh",methods=['GET'])
@frontend_login
def get_uh():
    user = g.user
    return jsonify({
        'status':'success',
        'uh':user.userhash
    }),200

@frontendapi_bp.route("/test_notification",methods=['GET'])
@frontend_login
def test_not():
    user = g.user
    current_app.config['socketio'].notify_user(user.userhash, "SEU APP CAIU CUIDADO!!", 'red')
    return jsonify({'status':'success','message':'Notificação enviada'}),200

