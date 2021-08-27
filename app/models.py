from enum import unique
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import nullslast
from sqlalchemy.sql.schema import ForeignKey
from app import db, ma, login_manager, app
from flask_login import UserMixin
from datetime import datetime
from marshmallow import Schema
# from marshmallow_sqlalchemy import ModelSchema

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(150), unique=True)
    unId = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(150))
    qrcode = db.Column(db.String(20))
    field = db.Column(db.String(60))
    created_at= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False, default='pending')
    roles = db.Column(db.String(60), default="Guest")

    def get_reset_token(self, expires_sec=18000):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class Record(db.Model, UserMixin):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(150), unique=True)
    unId = db.Column(db.String(10), nullable=False)
    phoneNum = db.Column(db.String(10), nullable=False)
    full_name = db.Column(db.String(150))
    field = db.Column(db.String(60))
    created_at= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)