from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/add/', views.recipe_add, name='recipe_add'),
    path('signup/', views.signup, name='signup'),  # Добавляем маршрут для регистрации
    path('profile/', views.profile, name='profile'),
    path('accounts/profile/', views.profile, name='profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('user/<int:user_id>/block/', views.block_user, name='block_user'),
    path('recipe/<int:pk>/like/', views.like_recipe, name='like_recipe'),
    path('recipe/<int:pk>/dislike/', views.dislike_recipe, name='dislike_recipe'),  # Добавляем маршрут для дизлайков
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
