from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """User profile model to extend User with starting balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    starting_balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username} - Starting Balance: ${self.starting_balance}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile and default categories when a new User is created"""
    if created:
        # Create user profile
        UserProfile.objects.create(user=instance)
        
        # Import Category model here to avoid circular imports
        from api.models import Category
        
        # Create default categories
        default_categories = [
            {'name': 'Car', 'type': 'expense'},
            {'name': 'Food', 'type': 'expense'},
            {'name': 'Clothes', 'type': 'expense'},
            {'name': 'Salary', 'type': 'income'},
        ]
        
        for category_data in default_categories:
            Category.objects.create(
                user=instance,
                name=category_data['name'],
                type=category_data['type']
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
