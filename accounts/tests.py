from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
import json


class AccountsTestCase(APITestCase):
    """Test cases for accounts app authentication endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.auth_info_url = reverse('auth_info')

        # Test user data
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

        # Create a test user for protected endpoint tests
        self.user = User.objects.create_user(
            username='existinguser',
            password='existingpass123',
            email='existing@example.com'
        )
        self.token = Token.objects.create(user=self.user)


class RegisterTestCase(AccountsTestCase):
    """Test cases for user registration"""

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['message'], 'User registered successfully')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertIsNotNone(response.data['token'])

        # Verify user was created in database
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_register_missing_username(self):
        """Test registration with missing username"""
        data = self.user_data.copy()
        del data['username']
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_missing_password(self):
        """Test registration with missing password"""
        data = self.user_data.copy()
        del data['password']
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_duplicate_username(self):
        """Test registration with existing username"""
        # Create user first
        User.objects.create_user(username='testuser', password='pass123')
        
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_without_email(self):
        """Test registration without email (should work)"""
        data = self.user_data.copy()
        del data['email']
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], '')

    def test_register_invalid_email(self):
        """Test registration with invalid email format"""
        data = self.user_data.copy()
        data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class LoginTestCase(AccountsTestCase):
    """Test cases for user login"""

    def setUp(self):
        super().setUp()
        # Create a user for login tests
        self.login_user = User.objects.create_user(
            username='loginuser',
            password='loginpass123',
            email='login@example.com'
        )

    def test_login_success(self):
        """Test successful login"""
        login_data = {
            'username': 'loginuser',
            'password': 'loginpass123'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertEqual(response.data['user']['username'], 'loginuser')
        self.assertEqual(response.data['user']['email'], 'login@example.com')
        self.assertIsNotNone(response.data['token'])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'loginuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {
            'username': 'nonexistentuser',
            'password': 'somepassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_missing_username(self):
        """Test login with missing username"""
        login_data = {'password': 'loginpass123'}
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_login_missing_password(self):
        """Test login with missing password"""
        login_data = {'username': 'loginuser'}
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class LogoutTestCase(AccountsTestCase):
    """Test cases for user logout"""

    def test_logout_success(self):
        """Test successful logout"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Logout successful')

        # Verify token was deleted
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=self.user)

    def test_logout_unauthorized(self):
        """Test logout without authentication"""
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalid_token(self):
        """Test logout with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTestCase(AccountsTestCase):
    """Test cases for user profile"""

    def test_profile_success(self):
        """Test successful profile retrieval"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'existinguser')
        self.assertEqual(response.data['user']['email'], 'existing@example.com')
        self.assertIn('id', response.data['user'])
        self.assertIn('date_joined', response.data['user'])

    def test_profile_unauthorized(self):
        """Test profile access without authentication"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_invalid_token(self):
        """Test profile access with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthInfoTestCase(AccountsTestCase):
    """Test cases for auth info endpoint"""

    def test_auth_info_success(self):
        """Test successful auth info retrieval"""
        response = self.client.get(self.auth_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('endpoints', response.data)
        self.assertIn('usage', response.data)
        self.assertEqual(response.data['message'], 'Authentication API')
        self.assertIn('register', response.data['endpoints'])
        self.assertIn('login', response.data['endpoints'])
        self.assertIn('logout', response.data['endpoints'])
        self.assertIn('profile', response.data['endpoints'])


class SerializerTestCase(TestCase):
    """Test cases for serializers"""

    def test_register_serializer_valid_data(self):
        """Test RegisterSerializer with valid data"""
        from .serializers import RegisterSerializer
        
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_register_serializer_invalid_data(self):
        """Test RegisterSerializer with invalid data"""
        from .serializers import RegisterSerializer
        
        data = {
            'username': '',  # Empty username
            'password': 'testpass123',
            'email': 'invalid-email'
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)

    def test_login_serializer_valid_data(self):
        """Test LoginSerializer with valid data"""
        from .serializers import LoginSerializer
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'testuser')
        self.assertEqual(serializer.validated_data['password'], 'testpass123')

    def test_login_serializer_invalid_data(self):
        """Test LoginSerializer with invalid data"""
        from .serializers import LoginSerializer
        
        data = {
            'username': '',  # Empty username
            'password': ''   # Empty password
        }
        
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('password', serializer.errors)


class TokenTestCase(TestCase):
    """Test cases for token functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='tokenuser',
            password='tokenpass123',
            email='token@example.com'
        )

    def test_token_creation(self):
        """Test token creation for user"""
        token, created = Token.objects.get_or_create(user=self.user)
        
        self.assertIsNotNone(token)
        self.assertTrue(created)
        self.assertEqual(token.user, self.user)

    def test_token_retrieval(self):
        """Test token retrieval for existing user"""
        # Create token first
        token1, created1 = Token.objects.get_or_create(user=self.user)
        
        # Get token again (should not create new one)
        token2, created2 = Token.objects.get_or_create(user=self.user)
        
        self.assertEqual(token1, token2)
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_token_deletion(self):
        """Test token deletion"""
        token, created = Token.objects.get_or_create(user=self.user)
        
        # Delete token
        token.delete()
        
        # Verify token is deleted
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=self.user)
