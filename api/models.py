from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    """Category model for income and expense categorization"""
    
    class CategoryType(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
        default=CategoryType.EXPENSE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return f"{self.name} ({self.type}) - {self.user.username}"
