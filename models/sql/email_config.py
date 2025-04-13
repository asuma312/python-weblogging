from hashlib import sha256
from datetime import datetime,timedelta
from models import db
import jwt
from uuid import uuid4
import os


class EmailToContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userhash = db.Column(db.String(50), db.ForeignKey('user.userhash'))
    email = db.Column(db.String(100), nullable=False)
    notifications = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
