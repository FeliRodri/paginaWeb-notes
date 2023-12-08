from . import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True)

    def create_note(self, data, category=None, reminder=None):
        new_note = Note(data=data, category=category, reminder=reminder, user_id=self.id)
        db.session.add(new_note)
        db.session.commit()
        return new_note



class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(255))
    reminder = db.Column(db.DateTime, nullable=True)