from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserProfile

@receiver(user_signed_up)
def create_user_profile(sender, request, user, **kwargs):
    """
    Create a UserProfile instance for a newly registered user.
    """
    UserProfile.objects.create(user=user)