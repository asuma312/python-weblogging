from hashlib import sha256
from datetime import datetime,timedelta
from models import db
import jwt
from uuid import uuid4
import os


class User(db.Model):
    name = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(50), nullable=False)
    pass_key = db.Column(db.String(50), nullable=False)
    userhash = db.Column(db.String(50), nullable=False)

    def generate_token(self,expiration_minutes=None):
        data = {
            'name': self.name,
            'password': self.password,
            'datetime': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'random': str(uuid4()),
        }
        payload = {
            "data": data,
        }
        if expiration_minutes:
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            payload['exp'] = expiration
        self.token = jwt.encode(payload, os.getenv("JWT_SECRET_TOKEN"), algorithm="HS256")
        return self.token

    def generate_hash256user(self):
        self.userhash = sha256(f"{self.name}{self.password}{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}".encode()).hexdigest()

    def hash_password(self,password):
        return sha256(password.encode()).hexdigest()

    def generate_passkey(self):
        self.pass_key = str(uuid4())
        return self.pass_key

    def set_hashed_password(self,password):
        self.password = self.hash_password(password)

    def verify_password(self,password):
        return self.password == self.hash_password(password)
