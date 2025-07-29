from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Category


class CategoryCRUDTestCase(APITestCase):
    """Basic CRUD test for Category model"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Set up URLs
        self.category_list_url = reverse('api:category-list-create')
        
        # Test category data
        self.category_data = {
            'name': 'Clothes',
            'type': 'expense'
        }

    def test_category_crud_operations(self):
        """Test Create, Read, Update, Delete operations for Category"""
        # Authenticate user
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # CREATE - Create a new category
        response = self.client.post(self.category_list_url, self.category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('category', response.data)
        category_id = response.data['category']['id']
        
        # READ - Get the created category
        category_detail_url = reverse('api:category-detail', kwargs={'pk': category_id})
        response = self.client.get(category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category']['name'], 'Clothes')
        self.assertEqual(response.data['category']['type'], 'expense')
        
        # UPDATE - Update the category
        update_data = {'name': 'Food', 'type': 'expense'}
        response = self.client.put(category_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category']['name'], 'Food')
        
        # DELETE - Delete the category
        response = self.client.delete(category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Food', response.data['message'])
        
        # Verify category is deleted
        response = self.client.get(category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
