"""
Auto-create UserProfile and UserPreference when a User is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile, UserPreference


@receiver(post_save, sender=User)
def create_user_profile_and_preferences(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        UserPreference.objects.get_or_create(user=instance)
