from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TestUser(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='TestUser', password='testpassword')
        self.admin = User.objects.create_user(
            username='AdminUser',
            password='admintestpassword',
            is_superuser=True
        )
    
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
        token = response.json()['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.delete('/v1/delete-token/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_list(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.get('v1/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        
    def test_user_retrieve(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.get(f'v1/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data['username'], self.user.get_username())
    
    def test_user_update(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.patch(
            f'v1/user/{self.user.id}/',
            {
                'first_name': 'foo',
                'last_name': 'bar'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_full_name(), 'foo bar')
    
    def test_user_delete(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.delete(f'v1/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
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