from flask import Blueprint, request, jsonify, current_app  
from sqlalchemy import case, cast, String, or_, desc    
from flask_jwt_extended import jwt_required  
from ..models.product import Product, Category  # Добавлен импорт Category  
from ..middleware.auth import admin_required  
from .. import db  


products = Blueprint('products', __name__)  

# @products.route('/', methods=['GET'])  
# def get_products():  
#     # Параметры фильтрации  
#     name = request.args.get('name', '')  
#     min_price = request.args.get('min_price', type=float)  
#     max_price = request.args.get('max_price', type=float)  
#     category_id = request.args.get('category_id', type=int)  # Добавлен параметр фильтрации по категории  
    
#     # Параметр limit для ограничения количества товаров на странице  
#     limit = request.args.get('limit', 10, type=int)  
#     page = request.args.get('page', 1, type=int)
       
#     # Базовый запрос  
#     query = Product.query  

#     # Применение фильтров  
#     if name:  
#         query = query.filter(or_(  
#             Product.name.ilike(f'%{name}%'),  
#             Product.description.ilike(f'%{name}%')  
#         ))  

#     if min_price is not None:  
#         query = query.filter(Product.price >= min_price)  

#     if max_price is not None:  
#         query = query.filter(Product.price <= max_price)  
        
#     # Фильтр по категории  
#     if category_id is not None:  
#         query = query.filter(Product.category_id == category_id)  

#     # # Пагинация  
#     # page = request.args.get('page', 1, type=int)  
#     # per_page = request.args.get('per_page', 10, type=int)  

#     # Получение результатов  
#     pagination = query.paginate(page=page, per_page=limit, error_out=False)  
#     products = pagination.items  

#     return jsonify({  
#         'products': [product.to_dict() for product in products],  
#         'total': pagination.total,  
#         'pages': pagination.pages,  
#         'current_page': pagination.page  
#     }), 200  
@products.route('/get-products', methods=['POST'])  
def get_products():  
    try:  
        # Получение параметров пагинации из query-параметров  
        page = request.args.get('page', 1, type=int)  
        limit = request.args.get('limit', 10, type=int)  
        
        # Получение параметров фильтрации из тела запроса  
        filter_data = request.json or {}  
        
        # Извлечение параметров фильтрации  
        search_query = filter_data.get('search_query', '').strip()  
        min_price = filter_data.get('min_price')  
        max_price = filter_data.get('max_price')  
        category_id = filter_data.get('category_id')  
        in_stock = filter_data.get('in_stock')  
        sort_by = filter_data.get('sort_by')  
        sort_order = filter_data.get('sort_order', 'asc')  
        
        # Добавляем параметры фильтрации по дате создания  
        created_from = filter_data.get('created_from')  
        created_to = filter_data.get('created_to')  
        
        # Базовый запрос  
        query = Product.query  
        
        # Применяем фильтр поиска, если поисковый запрос содержит хотя бы 2 символа  
        if search_query and len(search_query) >= 2:  
            # Проверяем, является ли запрос числом  
            is_numeric = search_query.isdigit()  
            
            if is_numeric:  
                # Создаем выражение для определения приоритета сортировки  
                search_priority = case(  
                    # 1-й приоритет: точное совпадение по ID  
                    (Product.id == int(search_query), 1),  
                    # 2-й приоритет: частичное совпадение по ID (преобразуем ID в строку)  
                    else_=case(  
                        (cast(Product.id, String).like(f'%{search_query}%'), 2),  
                        # 3-й приоритет: совпадение в названии  
                        else_=3  
                    )  
                ).label('search_priority')  
                
                # Применяем фильтр для поиска (только ID и название)  
                query = query.filter(  
                    or_(  
                        Product.id == int(search_query),  
                        cast(Product.id, String).like(f'%{search_query}%'),  
                        Product.name.ilike(f'%{search_query}%')  
                    )  
                )  
                
                # Добавляем сортировку по приоритету  
                query = query.order_by(search_priority)  
            else:  
                # Если запрос не числовой, ищем только по названию  
                query = query.filter(Product.name.ilike(f'%{search_query}%'))  

        # Применение других фильтров  
        if min_price is not None:  
            query = query.filter(Product.price >= float(min_price))  

        if max_price is not None:  
            query = query.filter(Product.price <= float(max_price))  
            
        if category_id is not None:  
            query = query.filter(Product.category_id == category_id)  
            
        if in_stock is not None:  
            query = query.filter(Product.in_stock == bool(in_stock))  
        
        # Добавляем фильтр по дате создания  
        if created_from is not None:  
            from datetime import datetime  
            created_from_date = datetime.fromisoformat(created_from)  
            query = query.filter(Product.created_at >= created_from_date)  
            
        if created_to is not None:  
            from datetime import datetime  
            created_to_date = datetime.fromisoformat(created_to)  
            query = query.filter(Product.created_at <= created_to_date)  
        
        # Применяем дополнительную сортировку, если не было поиска по числовому запросу  
        if sort_by and (not search_query or not search_query.isdigit()):  
            sort_attr = getattr(Product, sort_by, None)  
            if sort_attr:  
                query = query.order_by(desc(sort_attr) if sort_order == 'desc' else sort_attr)  

        # Получение результатов с пагинацией  
        pagination = query.paginate(page=page, per_page=limit, error_out=False)  
        products = pagination.items  

        return jsonify({  
            'products': [product.to_dict() for product in products],  
            'total': pagination.total,  
            'pages': pagination.pages,  
            'current_page': pagination.page  
        }), 200  
    except Exception as e:  
        # Обработка исключений  
        return jsonify({'error': str(e)}), 500

# Добавляем новый метод для получения всех категорий  
@products.route('/categories', methods=['GET'])  
def get_categories():  
    categories = Category.query.all()  
    return jsonify({  
        'categories': [category.to_dict() for category in categories]  
    }), 200  

    # Создание нового товара 
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

    # Обновление данных товара 
@products.route('/<int:product_id>', methods=['PUT'])  
@admin_required  
def update_product(product_id):  
    product = Product.query.get(product_id)  

    if not product:  
        return jsonify({'msg': 'Товар не найден'}), 404  

    data = request.get_json()  

 
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

    # Удаление товара 
@products.route('/<int:product_id>', methods=['DELETE'])  
@admin_required  
def delete_product(product_id):  
    product = Product.query.get(product_id)  

    if not product:  
        return jsonify({'msg': 'Товар не найден'}), 404  

    db.session.delete(product)  
    db.session.commit()  

    return jsonify({'msg': 'Товар успешно удален'}), 200