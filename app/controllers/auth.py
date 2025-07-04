import logging  
from flask import Blueprint, request, jsonify  
from flask_jwt_extended import (  
    create_access_token,  
    create_refresh_token,  
    jwt_required,  
    get_jwt_identity  
)  
from ..models.user import User  
from .. import db  

# Настраиваем базовый логгер (можно перенести в точку старта приложения)  
logging.basicConfig(  
    level=logging.DEBUG,  
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s'  
)  
logger = logging.getLogger('auth')  

auth = Blueprint('auth', __name__)  

@auth.route('/register', methods=['POST'])  
def register():  
    logger.info("ENTER /register")  
    data = request.get_json()  
    logger.debug("Request JSON: %s", data)  

    # Проверка наличия необходимых полей  
    if not data or not data.get('email') or not data.get('password'):  
        logger.warning("Missing fields in register: %s", data)  
        return jsonify({'msg': 'Отсутствуют необходимые поля: email, password'}), 400  

    # Проверка на уникальность email  
    exists = User.query.filter_by(email=data['email']).first()  
    logger.debug("Email exists? %s", bool(exists))  
    if exists:  
        logger.warning("Attempt to register existing email: %s", data['email'])  
        return jsonify({'msg': 'Пользователь с таким email уже существует'}), 409  

    # Определяем username  
    username = data.get('username') or data['email'].split('@')[0]  
    logger.debug("Resolved username: %s", username)  

    new_user = User(  
        username=username,  
        email=data['email'],  
        password=data['password'],  
        role=data.get('role', 'buyer')  
    )  

    try:  
        db.session.add(new_user)  
        db.session.commit()  
        logger.info("User created with id=%s", new_user.id)  
    except Exception as e:  
        db.session.rollback()  
        logger.exception("DB error on user registration")  
        return jsonify({'msg': 'Ошибка при сохранении пользователя'}), 500  

    return jsonify({  
        'msg': 'Пользователь успешно зарегистрирован',  
        'user_id': new_user.id,  
        'username': new_user.username  
    }), 201  

@auth.route('/login', methods=['POST'])  
def login():  
    logger.info("ENTER /login")  
    data = request.get_json()  
    logger.debug("Request JSON: %s", data)  

    if not data or not data.get('email') or not data.get('password'):  
        logger.warning("Missing fields in login: %s", data)  
        return jsonify({'msg': 'Отсутствуют необходимые поля: email, password'}), 400  

    user = User.query.filter_by(email=data['email']).first()  
    logger.debug("User fetched: %s", user)  

    if not user or not user.verify_password(data['password']):  
        logger.warning("Invalid credentials for email: %s", data.get('email'))  
        return jsonify({'msg': 'Неверный email или пароль'}), 401  

    # Логируем тип и значение identity  
    identity = str(user.id)  
    logger.debug("Identity for tokens – type: %s, value: %s", type(identity), identity)  

    try:  
        access_token = create_access_token(identity=identity)  
        refresh_token = create_refresh_token(identity=identity)  
        logger.info("Tokens created for user id=%s", identity)  
    except Exception as e:  
        logger.exception("Error creating JWT tokens")  
        return jsonify({'msg': 'Ошибка создания токенов'}), 500  

    return jsonify({  
        'access_token': access_token,  
        'refresh_token': refresh_token,  
        'user': user.to_dict()  
    }), 200  

@auth.route('/refresh', methods=['POST'])  
@jwt_required(refresh=True)  
def refresh():  
    logger.info("ENTER /refresh")  
    current_user_id = get_jwt_identity()  
    logger.debug("Current user identity from refresh token – type: %s, value: %s",  
                 type(current_user_id), current_user_id)  

    try:  
        access_token = create_access_token(identity=current_user_id)  
        logger.info("New access token issued for user id=%s", current_user_id)  
    except Exception as e:  
        logger.exception("Error refreshing access token")  
        return jsonify({'msg': 'Ошибка обновления токена'}), 500  

    return jsonify({'access_token': access_token}), 200  

@auth.route('/me', methods=['GET'])  
@jwt_required()  
def get_user_info():  
    logger.info("ENTER /me")  
    current_user_id = get_jwt_identity()  
    logger.debug("Current user identity: %s (type: %s)",  
                 current_user_id, type(current_user_id))  

    user = User.query.get(current_user_id)  
    logger.debug("User fetched by id: %s", user)  

    if not user:  
        logger.warning("User not found for id: %s", current_user_id)  
        return jsonify(message="User not found"), 404  

    logger.info("Returning profile for user id=%s", current_user_id)  
    return jsonify(  
        id=user.id,  
        username=user.username,  
        email=user.email,  
        role=user.role,  
        # created_at=user.created_at.isoformat() if present  
    ), 200