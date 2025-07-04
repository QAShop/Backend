from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate  
from .config import config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # app.url_map.strict_slashes = False

    # Инициализация расширений
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173",   
                                  "allow_headers": ["Content-Type", "Authorization"],
                                  "methods": ["GET", "POST", "OPTIONS"]}})

    # Регистрация Blueprint'ов
    from .controllers.auth import auth
    from .controllers.products import products
    
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(products, url_prefix='/api/products')
    
    # Инициализация базовой структуры  
    with app.app_context():  
        db.create_all()  
        init_categories()

    return app


def init_categories():  
    from app.models.product import Category  
    
    # Список базовых категорий  
    categories = [  
        "Электроника",  
        "Одежда",  
        "Обувь",  
        "Аксессуары",  
        "Книги",  
        "Продукты питания",  
        "Бытовая техника",  
        "Мебель",  
        "Спортивные товары"  
    ]  
    
    # Добавляем категории, если их нет  
    for cat_name in categories:  
        if not Category.query.filter_by(name=cat_name).first():  
            category = Category(name=cat_name)  
            db.session.add(category)  
    
    db.session.commit()  
    print("Базовые категории созданы")
    
  