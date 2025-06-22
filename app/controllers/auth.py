from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..models.user import User
from .. import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Проверка наличия необходимых полей
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'msg': 'Отсутствуют необходимые поля: email, password'}), 400

    # Проверка на уникальность email
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg': 'Пользователь с таким email уже существует'}), 409

    # Создание нового пользователя
    new_user = User(
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'buyer')  # По умолчанию - покупатель
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'Пользователь успешно зарегистрирован', 'user_id': new_user.id}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Проверка наличия необходимых полей
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'msg': 'Отсутствуют необходимые поля: email, password'}), 400

    # Поиск пользователя
    user = User.query.filter_by(email=data['email']).first()

    # Проверка существования пользователя и правильности пароля
    if not user or not user.verify_password(data['password']):
        return jsonify({'msg': 'Неверный email или пароль'}), 401

    # Создание токенов
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)

    return jsonify({'access_token': access_token}), 200

@auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    return jsonify({'user': user.to_dict()}), 200
