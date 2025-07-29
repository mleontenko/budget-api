from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategorySerializer, ExpenseSerializer


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
    """View for listing and creating expenses"""
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return expenses for the authenticated user"""
        return self.request.user.expenses.all()
    
    def get(self, request, *args, **kwargs):
        """Get all expenses for the authenticated user"""
        expenses = self.get_queryset()
        serializer = self.get_serializer(expenses, many=True)
        return Response({
            'message': 'Expenses retrieved successfully',
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
