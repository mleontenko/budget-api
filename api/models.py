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


class Expense(models.Model):
    """Expense model for tracking user expenses"""
    
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    description = models.CharField(max_length=255)
    date = models.DateField()  # Date when the expense occurred
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
    
    def __str__(self):
        return f"${self.amount} - {self.description} ({self.category.name}) - {self.date}"
    
    def save(self, *args, **kwargs):
        """Ensure amount is always positive"""
        if self.amount < 0:
            self.amount = abs(self.amount)
        super().save(*args, **kwargs)
