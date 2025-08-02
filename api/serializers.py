from rest_framework import serializers
from .models import Category, Expense

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


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model"""
    
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'description', 'date', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Set the user to the current authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update instance with validated data, preserving existing values for missing fields"""
        instance.amount = validated_data.get('amount', instance.amount)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.date = validated_data.get('date', instance.date)
        instance.save()
        return instance
    
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate_category(self, value):
        """Validate that category belongs to the authenticated user"""
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("You can only use your own categories")
        return value
    
    def validate_date(self, value):
        """Validate that date is not in the future"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Date cannot be in the future")
        return value