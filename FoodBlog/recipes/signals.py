
from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Recipe
from .telegram_bot import send_recipe_to_telegram
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Recipe)
def notify_telegram_on_new_recipe(sender, instance, created, **kwargs):
    if created:
        async_to_sync(send_recipe_to_telegram)(instance)  # Асинхронный вызов как синхронный



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


