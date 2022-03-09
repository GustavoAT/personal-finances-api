from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TestUser(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='TestUser', password='testpassword')
    
    def test_user_login(self):
        response = self.client.post(
            '/v1/login/',
            {
                'username': 'TestUser',
                'password': 'testpassword'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.json())

class TestHome(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='TestUser2', password='testpassword2')
        self.token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token[0]}')
    
    def test_home_logged(self):
        response = self.client.get('/v1/')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)