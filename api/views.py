from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategorySerializer


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
