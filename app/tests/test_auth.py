import unittest
import json
from app import create_app, db
from app.models.user import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Создаем тестового пользователя
        test_user = User(email='test@example.com', password='password')
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        """Тест регистрации нового пользователя"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'email': 'new@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertTrue('user_id' in data)

    def test_login(self):
        """Тест входа в систему"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access_token' in data)
        self.assertTrue('refresh_token' in data)
