from models.sql.user import User
from flask import current_app
import os

def get_user_path(user:User):
    full_path = current_app.config['SQLITE_DBPATH'] + user.userhash
    os.makedirs(full_path,exist_ok=True)

    logs_path = os.path.join(full_path, 'logs')
    os.makedirs(logs_path, exist_ok=True)

    return logs_path

