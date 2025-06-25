from datetime import datetime
from .. import db

class Category(db.Model):  
    __tablename__ = 'categories'  
    
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False, unique=True)  
    
    def __repr__(self):  
        return f'<Category {self.name}>'  
    
    def to_dict(self):  
        return {  
            'id': self.id,  
            'name': self.name  
        }


class Product(db.Model):  
    __tablename__ = 'products'  

    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)  
    price = db.Column(db.Float, nullable=False)  
    description = db.Column(db.Text, nullable=True)  
    image_url = db.Column(db.String(255), nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  
    category = db.relationship('Category', backref='products')  
    in_stock = db.Column(db.Boolean, default=True)  # Добавляем новую колонку с дефолтным значением True  

    def __init__(self, name, price, description=None, image_url=None, category_id=None, in_stock=True):  
        self.name = name  
        self.price = price  
        self.description = description  
        self.image_url = image_url  
        self.category_id = category_id  
        self.in_stock = in_stock  # Инициализируем in_stock  

    def to_dict(self):  
        return {  
            'id': self.id,  
            'name': self.name,  
            'price': self.price,  
            'description': self.description,  
            'category': self.category.to_dict() if self.category else None,  
            'image_url': self.image_url,  
            'created_at': self.created_at.isoformat(),  
            'updated_at': self.updated_at.isoformat(),  
            'in_stock': self.in_stock,  # Добавляем in_stock в выходной словарь  
        }
        
        
        
        
