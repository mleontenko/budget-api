from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Set the user to the current authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_name(self, value):
        """Validate that category name is not empty and is properly formatted"""
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty")
        return value.strip().title() 