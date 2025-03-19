from django.contrib import admin
from .models import Recipe, Like, Category  # Импортируем модель Category

admin.site.register(Recipe)
admin.site.register(Like)
admin.site.register(Category)  # Регистрируем категорию в админке


# Register your models here.
