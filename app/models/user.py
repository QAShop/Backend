from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='buyer')  # buyer или admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, email=None, password=None, username=None, role='buyer'):  
        if email is None:  
            raise ValueError("Email is required")  
        # Если username не задан — берём до "@"  
        self.username = username or email.split('@')[0]  
        self.email = email  
        self.role = role  

        # Присваивание — так сработает @password.setter  
        if password is not None:  
            self.password = password  

    @property  
    def password(self):  
        raise AttributeError('Пароль не является читаемым атрибутом')  

    @password.setter  
    def password(self, plaintext):  
        self.password_hash = generate_password_hash(plaintext)  

    def verify_password(self, plaintext):  
        return check_password_hash(self.password_hash, plaintext)  

    def is_admin(self):  
        return self.role == 'admin'  

    def to_dict(self):  
        return {  
            'id': self.id,  
            'username': self.username,  
            'email': self.email,  
            'role': self.role,  
            'created_at': self.created_at.isoformat(),  
            'updated_at': self.updated_at.isoformat()  
        }  