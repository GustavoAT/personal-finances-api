from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from personal_finances.api_server.models import Account, Category

class TestUser(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='TestUser', password='testpassword')
        self.admin = User.objects.create_user(
            username='AdminUser',
            password='admintestpassword',
            is_superuser=True,
            is_staff=True
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
        response = self.client.get('/v1/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.get('/v1/user/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_user_retrieve(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.get(f'/v1/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data['username'], self.user.get_username())
    
    def test_user_update(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.patch(
            f'/v1/user/{self.user.id}/',
            {
                'first_name': 'foo',
                'last_name': 'bar'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.get_full_name(), 'foo bar')
    
    def test_user_delete(self):
        token = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token[0]}')
        response = self.client.delete(f'/v1/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class BaseTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='TestUser2', password='testpassword2')
        self.token = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token[0]}')

class TestHome(BaseTestCase):
    def test_home_logged(self):
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TestAccount(BaseTestCase):
    def test_crud(self):
        # create
        response = self.client.post(
            '/v1/account/',
            {
                'name': 'bank1',
                'description': 'first account',
                'initial_value': 0
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account_id = response.json()['id']
        # list
        response = self.client.get('/v1/account/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # retrieve
        response = self.client.get(f'/v1/account/{account_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'bank1')
        # update
        response = self.client.patch(
            f'/v1/account/{account_id}/',
            {
                'name': 'bank 2'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'bank 2')
        # delete
        response = self.client.delete(f'/v1/account/{account_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class TestCategory(BaseTestCase):
    def test_crud(self):
        # create
        categories = [
            {
                'name': 'Salary',
                'of_type': Category.INCOME
            },
            {
                'name': 'Home',
                'of_type': Category.EXPENSE
            }
        ]
        for category in categories:
            response = self.client.post(
                '/v1/category/',
                category
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            id = response.json()['id']
            # retrieve
            response = self.client.get(f'/v1/category/{id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        # list
        response = self.client.get('/v1/category/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            '/v1/category/', {'of_type': Category.INCOME})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        id = response.json()[0]['id']
        # update
        response = self.client.patch(
            f'/v1/category/{id}/',
            {'name': 'Health', 'of_type': Category.EXPENSE}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json()['of_type'], Category.EXPENSE)
        self.assertEqual(response.json()['name'], 'Health')
        # delete
        response = self.client.delete(f'/v1/category/{id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        