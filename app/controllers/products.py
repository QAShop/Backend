from flask import Blueprint, request, jsonify, current_app  
from sqlalchemy import or_  
from flask_jwt_extended import jwt_required  
from ..models.product import Product, Category  # Добавлен импорт Category  
from ..middleware.auth import admin_required  
from .. import db  

products = Blueprint('products', __name__)  

@products.route('/', methods=['GET'])  
def get_products():  
    # Параметры фильтрации  
    name = request.args.get('name', '')  
    min_price = request.args.get('min_price', type=float)  
    max_price = request.args.get('max_price', type=float)  
    category_id = request.args.get('category_id', type=int)  # Добавлен параметр фильтрации по категории  

    # Базовый запрос  
    query = Product.query  

    # Применение фильтров  
    if name:  
        query = query.filter(or_(  
            Product.name.ilike(f'%{name}%'),  
            Product.description.ilike(f'%{name}%')  
        ))  

    if min_price is not None:  
        query = query.filter(Product.price >= min_price)  

    if max_price is not None:  
        query = query.filter(Product.price <= max_price)  
        
    # Фильтр по категории  
    if category_id is not None:  
        query = query.filter(Product.category_id == category_id)  

    # Пагинация  
    page = request.args.get('page', 1, type=int)  
    per_page = request.args.get('per_page', 10, type=int)  

    # Получение результатов  
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)  
    products = pagination.items  

    return jsonify({  
        'products': [product.to_dict() for product in products],  
        'total': pagination.total,  
        'pages': pagination.pages,  
        'current_page': pagination.page  
    }), 200  

@products.route('/<int:product_id>', methods=['GET'])  
def get_product(product_id):  
    product = Product.query.get(product_id)  

    if not product:  
        return jsonify({'msg': 'Товар не найден'}), 404  

    return jsonify({'product': product.to_dict()}), 200  

# Добавляем новый метод для получения всех категорий  
@products.route('/categories', methods=['GET'])  
def get_categories():  
    categories = Category.query.all()  
    return jsonify({  
        'categories': [category.to_dict() for category in categories]  
    }), 200  

@products.route('/', methods=['POST'])  
@admin_required  
def create_product():  
    data = request.get_json()  

    # Проверка наличия обязательных полей  
    if not data or not data.get('name') or data.get('price') is None:  
        return jsonify({'msg': 'Отсутствуют обязательные поля: name, price'}), 400  

    # Проверяем категорию, если указана  
    category_id = data.get('category')  
    if category_id is not None:  
        category = Category.query.get(category_id)  
        if not category:  
            return jsonify({'msg': 'Указанная категория не найдена'}), 400  

    # Создание нового товара  
    new_product = Product(  
        name=data['name'],  
        price=float(data['price']),  
        description=data.get('description'),  
        image_url=data.get('image_url'),  
        category_id=category_id,
        in_stock=data.get('in_stock', True)        
    )  

    db.session.add(new_product)  
    db.session.commit()  

    return jsonify({  
        'msg': 'Товар успешно создан',  
        'product': new_product.to_dict()  
    }), 201  

@products.route('/<int:product_id>', methods=['PUT'])  
@admin_required  
def update_product(product_id):  
    product = Product.query.get(product_id)  

    if not product:  
        return jsonify({'msg': 'Товар не найден'}), 404  

    data = request.get_json()  

    # Обновление данных товара  
    if data.get('name'):  
        product.name = data['name']  

    if data.get('price') is not None:  
        product.price = float(data['price'])  

    if 'description' in data:  
        product.description = data['description']  

    if 'image_url' in data:  
        product.image_url = data['image_url']  
        
    # Добавляем возможность обновить категорию  
    if 'category_id' in data:  
        category_id = data['category_id']  
        if category_id is not None:  
            category = Category.query.get(category_id)  
            if not category:  
                return jsonify({'msg': 'Указанная категория не найдена'}), 400  
            product.category_id = category_id  
        else:  
            product.category_id = None  # Разрешаем сбрасывать категорию  

    db.session.commit()  

    return jsonify({  
        'msg': 'Товар успешно обновлен',  
        'product': product.to_dict()  
    }), 200  

@products.route('/<int:product_id>', methods=['DELETE'])  
@admin_required  
def delete_product(product_id):  
    product = Product.query.get(product_id)  

    if not product:  
        return jsonify({'msg': 'Товар не найден'}), 404  

    db.session.delete(product)  
    db.session.commit()  

    return jsonify({'msg': 'Товар успешно удален'}), 200