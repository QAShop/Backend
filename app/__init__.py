from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate  
import os
from .config import config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)

    # === Выбираем конфиг из переменной окружения Render ===
    config_name = config_name or os.getenv('FLASK_ENV', 'production')
    app.config.from_object(config.get(config_name, config['default']))
    
    # === Инициализация расширений ===
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # === CORS: в проде можно разрешить фронт Render ===
    frontend_origin = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS(app, resources={r"/api/*": {
        "origins": frontend_origin,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    }})

    # === Регистрация Blueprint'ов ===
    from .controllers.auth import auth
    from .controllers.products import products
    
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(products, url_prefix='/api/products')
    
    # === Инициализация базовой структуры ===
    # ⚠️ На Render не вызываем db.create_all() — сделки делает Alembic
    # Но можно вызывать init_categories(), если категории нужны всегда.
    with app.app_context():
        try:
            init_categories()
        except Exception as e:
            print("init_categories() skipped:", e)

    return app


def init_categories():  
    from app.models.product import Category  
    
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
    
    for cat_name in categories:  
        if not Category.query.filter_by(name=cat_name).first():  
            db.session.add(Category(name=cat_name))  
    
    db.session.commit()  
    print("Базовые категории созданы")
