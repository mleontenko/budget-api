from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategorySerializer, ExpenseSerializer
from datetime import datetime
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


class CategoryListCreateView(ListCreateAPIView):
    """View for listing and creating categories"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return categories for the authenticated user"""
        return Category.objects.filter(user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        """Get all categories for the authenticated user"""
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response({
            'message': 'Categories retrieved successfully',
            'categories': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """Create a new category for the authenticated user"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                'message': 'Category created successfully',
                'category': CategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting a specific category"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return categories for the authenticated user"""
        return Category.objects.filter(user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        """Get a specific category"""
        category = self.get_object()
        serializer = self.get_serializer(category)
        return Response({
            'message': 'Category retrieved successfully',
            'category': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        """Update a specific category"""
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data)
        if serializer.is_valid():
            updated_category = serializer.save()
            return Response({
                'message': 'Category updated successfully',
                'category': CategorySerializer(updated_category).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """Delete a specific category"""
        category = self.get_object()
        category_name = category.name
        category.delete()
        return Response({
            'message': f'Category "{category_name}" deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_types(request):
    """Get available category types"""
    types = [
        {'value': choice[0], 'label': choice[1]} 
        for choice in Category.CategoryType.choices
    ]
    
    return Response({
        'message': 'Category types retrieved successfully',
        'types': types
    }, status=status.HTTP_200_OK)


class ExpenseListCreateView(ListCreateAPIView):
    """View for listing and creating expenses with filtering"""
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return filtered expenses for the authenticated user"""
        queryset = self.request.user.expenses.all()
        
        # Build filters dictionary
        filters = {}
        
        # Category filter
        if self.request.query_params.get('category'):
            filters['category_id'] = self.request.query_params.get('category')
        
        # Price filters
        if self.request.query_params.get('min_price'):
            filters['amount__gte'] = self.request.query_params.get('min_price')
        if self.request.query_params.get('max_price'):
            filters['amount__lte'] = self.request.query_params.get('max_price')
        
        # Date filters
        if self.request.query_params.get('start_date'):
            filters['created_at__date__gte'] = self.request.query_params.get('start_date')
        if self.request.query_params.get('end_date'):
            filters['created_at__date__lte'] = self.request.query_params.get('end_date')
        
        # Apply allfilters at once
        return queryset.filter(**filters).order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        """Get filtered expenses for the authenticated user"""
        expenses = self.get_queryset()
        serializer = self.get_serializer(expenses, many=True)
        
        # Get applied filters
        filters_applied = {k: v for k, v in request.query_params.items() 
                          if k in ['category', 'min_price', 'max_price', 'start_date', 'end_date']}
        
        return Response({
            'message': 'Expenses retrieved successfully',
            'filters_applied': filters_applied,
            'total_count': expenses.count(),
            'expenses': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """Create a new expense for the authenticated user"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            expense = serializer.save()
            return Response({
                'message': 'Expense created successfully',
                'expense': ExpenseSerializer(expense).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting a specific expense"""
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return expenses for the authenticated user"""
        return self.request.user.expenses.all()
    
    def get(self, request, *args, **kwargs):
        """Get a specific expense"""
        expense = self.get_object()
        serializer = self.get_serializer(expense)
        return Response({
            'message': 'Expense retrieved successfully',
            'expense': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        """Update a specific expense"""
        expense = self.get_object()
        serializer = self.get_serializer(expense, data=request.data)
        if serializer.is_valid():
            updated_expense = serializer.save()
            return Response({
                'message': 'Expense updated successfully',
                'expense': ExpenseSerializer(updated_expense).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """Delete a specific expense"""
        expense = self.get_object()
        expense_description = expense.description
        expense.delete()
        return Response({
            'message': f'Expense "{expense_description}" deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_period_balance(request):
    """Get balance and expenses for a custom date range"""
    user = request.user
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    
    # Validate required parameters
    if not start_date_str or not end_date_str:
        return Response({
            'error': 'Both start_date and end_date parameters are required (YYYY-MM-DD format)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Make them timezone-aware
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        # Validate date order
        if start_date > end_date:
            return Response({
                'error': 'start_date must be before or equal to end_date'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError:
        return Response({
            'error': 'Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-15)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get user's starting balance
    starting_balance = user.profile.starting_balance
    
    # Calculate balance at start of period
    expenses_before_period = user.expenses.filter(created_at__lt=start_date)
    income_before = expenses_before_period.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0
    expenses_before = expenses_before_period.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0
    balance_at_start = starting_balance + income_before - expenses_before
    
    # Calculate period expenses
    period_expenses = user.expenses.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    
    period_income = period_expenses.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0
    period_expenses_amount = period_expenses.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0
    period_net = period_income - period_expenses_amount
    
    # Calculate balance at end of period
    balance_at_end = balance_at_start + period_net
    
    # Get transaction details for the period
    income_transactions = period_expenses.filter(category__type='income').count()
    expense_transactions = period_expenses.filter(category__type='expense').count()
    
    return Response({
        'message': 'Custom period balance calculated successfully',
        'period': {
            'start_date': start_date_str,
            'end_date': end_date_str,
            'days': (end_date - start_date).days + 1
        },
        'balance': {
            'balance_at_start_of_period': float(balance_at_start),
            'balance_at_end_of_period': float(balance_at_end),
            'change_during_period': float(period_net)
        },
        'period_summary': {
            'total_income': float(period_income),
            'total_expenses': float(period_expenses_amount),
            'net_amount': float(period_net),
            'income_transactions': income_transactions,
            'expense_transactions': expense_transactions,
            'total_transactions': period_expenses.count()
        }
    }, status=status.HTTP_200_OK)
