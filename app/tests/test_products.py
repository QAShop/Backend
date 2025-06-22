import unittest
import json
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from flask_jwt_extended import create_access_token

class ProductsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Создаем тестового админа
        self.admin = User(email='admin@example.com', password='adminpass', role='admin')
        db.session.add(self.admin)

        # Создаем тестовый товар
        self.product = Product(name='Test Product', price=100.0, description='Test Description')
        db.session.add(self.product)
        db.session.commit()

        # Создаем токен для админа
        with self.app.app_context():
            self.admin_token = create_access_token(identity=self.admin.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_products(self):
        """Тест получения списка товаров"""
        response = self.client.get('/api/products/')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('products' in data)
        self.assertEqual(len(data['products']), 1)

    def test_create_product(self):
        """Тест создания нового товара (только админ)"""
        response = self.client.post(
            '/api/products/',
            data=json.dumps({
                'name': 'New Product',
                'price': 200.0,
                'description': 'New Description'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertTrue('product' in data)
        self.assertEqual(data['product']['name'], 'New Product')
