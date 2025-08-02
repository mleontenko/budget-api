from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Category, Expense


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


class ExpenseCRUDTestCase(APITestCase):
    """Simple CRUD test for Expense model"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Create a test category
        self.category = Category.objects.create(
            name='Food',
            type='expense',
            user=self.user
        )
        
        # Set up URLs
        self.expense_list_url = reverse('api:expense-list-create')
        
        # Test expense data with date
        self.expense_data = {
            'amount': 25.50,
            'category': self.category.id,
            'description': 'Lunch at restaurant',
            'date': '2024-08-01'
        }

    def test_create_expense(self):
        """Test creating an expense"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.expense_list_url, self.expense_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('expense', response.data)

    def test_read_expense(self):
        """Test reading an expense"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Create first
        response = self.client.post(self.expense_list_url, self.expense_data, format='json')
        expense_id = response.data['expense']['id']
        
        # Then read
        expense_detail_url = reverse('api:expense-detail', kwargs={'pk': expense_id})
        response = self.client.get(expense_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_expense(self):
        """Test updating an expense"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Create first
        response = self.client.post(self.expense_list_url, self.expense_data, format='json')
        expense_id = response.data['expense']['id']
        
        # Then update
        expense_detail_url = reverse('api:expense-detail', kwargs={'pk': expense_id})
        update_data = {
            'amount': 35.00, 
            'description': 'Dinner at restaurant',
            'category': self.category.id,
            'date': '2024-08-02'
        }
        response = self.client.put(expense_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_expense(self):
        """Test deleting an expense"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Create first
        response = self.client.post(self.expense_list_url, self.expense_data, format='json')
        expense_id = response.data['expense']['id']
        
        # Then delete
        expense_detail_url = reverse('api:expense-detail', kwargs={'pk': expense_id})
        response = self.client.delete(expense_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExpenseFilterTestCase(APITestCase):
    """Simple test for expense filtering"""

    def setUp(self):
        """Set up minimal test data"""
        # Create user and token
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        
        # Create one category
        self.category = Category.objects.create(name='Food', type='expense', user=self.user)
        
        # Create one expense with date
        self.expense = Expense.objects.create(
            amount=25.50,
            category=self.category,
            description='Lunch',
            date='2024-08-01',
            user=self.user
        )
        
        # Set up client
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = reverse('api:expense-list-create')

    def test_filter_by_category(self):
        """Test category filter"""
        response = self.client.get(f'{self.url}?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('category', response.data['filters_applied'])

    def test_filter_by_price(self):
        """Test price filter"""
        response = self.client.get(f'{self.url}?min_price=20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('min_price', response.data['filters_applied'])

    def test_filter_by_date(self):
        """Test date filter"""
        response = self.client.get(f'{self.url}?start_date=2024-08-01&end_date=2024-08-31')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', response.data['filters_applied'])
        self.assertIn('end_date', response.data['filters_applied'])

    def test_no_filters(self):
        """Test no filters"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['filters_applied']), 0)
