from django.contrib.auth.forms import UserCreationForm
from .models import Recipe, Category
from .models import Comment
from django import forms
from .models import Profile
from django.contrib.auth.models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

# Форма для изменения имени пользователя
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Поле для текста комментария


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'cooking_time', 'image', 'category']  # Добавляем поле category

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Добавляем поле для email

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")  # Поля формы

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


