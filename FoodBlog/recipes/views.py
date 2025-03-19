from django.contrib.auth import login, authenticate
from .models import Category, Like
from .forms import RecipeForm, CustomUserCreationForm
from .forms import CommentForm
from django.shortcuts import get_object_or_404
from .models import Comment
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProfileUpdateForm
from django.db.models import Q
from django.shortcuts import render
from .models import Recipe, Category



def recipe_list(request):
    query = request.GET.get('search')
    category_id = request.GET.get('category')

    if query:
        recipes = Recipe.objects.filter(Q(title__icontains=query))
    elif category_id:
        recipes = Recipe.objects.filter(category__id=category_id)
    else:
        recipes = Recipe.objects.all()

    categories = Category.objects.all()

    # Обновляем информацию о лайках и дизлайках для каждого рецепта
    for recipe in recipes:
        recipe.total_likes_count = recipe.total_likes()
        recipe.total_dislikes_count = recipe.total_dislikes()

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'categories': categories,
    })

@login_required
def profile_settings(request):
    if request.method == 'POST':
        # Получаем формы для обновления профиля и смены пароля
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        username = request.POST.get('username')

        # Проверяем никнейм (если никнейм пустой, показываем сообщение)
        if not username and not request.POST.get('old_password'):
            messages.error(request, 'Поле никнейма не может быть пустым.')
            return render(request, 'registration/profile_settings.html', {
                'p_form': p_form,
                'password_change_form': PasswordChangeForm(user=request.user)
            })

        # Форма для смены пароля
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)

        # Логика обновления профиля и пароля
        profile_updated = False
        password_updated = False

        # Проверка и сохранение формы профиля
        if p_form.is_valid() and username:
            request.user.username = username
            request.user.save()
            p_form.save()
            profile_updated = True
            messages.success(request, 'Ваш профиль был успешно обновлен!')

        # Проверка и изменение пароля
        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)  # Чтобы избежать автоматического выхода пользователя
            password_updated = True
            messages.success(request, 'Ваш пароль был успешно изменен!')

        # Если что-то было обновлено, перенаправляем на страницу профиля
        if profile_updated or password_updated:
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    else:
        # Обработка GET-запроса, загружаем формы профиля и смены пароля
        p_form = ProfileUpdateForm(instance=request.user.profile)
        password_change_form = PasswordChangeForm(user=request.user)

    return render(request, 'registration/profile_settings.html', {
        'p_form': p_form,
        'password_change_form': password_change_form
    })



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Чтобы избежать автоматического выхода пользователя
            messages.success(request, 'Ваш пароль был успешно изменен!')
            return redirect('profile')  # Перенаправление на личный кабинет после смены пароля
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'registration/change_password.html', {'form': form})



# Декоратор для проверки, что пользователь — суперпользователь
def admin_required(view_func):
    return user_passes_test(lambda user: user.is_superuser)(view_func)



@admin_required
def block_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Меняем статус активности пользователя
    if user.is_active:
        user.is_active = False
        messages.success(request, f'Пользователь {user.username} был заблокирован.')
    else:
        user.is_active = True
        messages.success(request, f'Пользователь {user.username} был разблокирован.')

    user.save()
    return redirect('profile')







@login_required
@user_passes_test(lambda user: user.is_superuser)  # Проверка, что пользователь — суперпользователь
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    recipe = comment.recipe  # Получаем рецепт, к которому относится комментарий
    comment.delete()  # Удаляем комментарий
    messages.success(request, 'Комментарий успешно удалён.')

    # Перенаправляем пользователя обратно на страницу рецепта
    return redirect('recipe_detail', pk=recipe.pk)


from django.contrib.auth.models import User

@login_required
def profile(request):
    if request.method == 'POST':
        # Форма для обновления профиля
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Если пользователь — суперпользователь, получаем всех пользователей
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = None  # Для обычных пользователей не передаем список

    # Получаем рецепты, созданные пользователем
    user_recipes = Recipe.objects.filter(author=request.user) if not request.user.is_superuser else Recipe.objects.all()

    context = {
        'p_form': p_form,
        'user_recipes': user_recipes,
        'users': users,  # Передаем список всех пользователей в шаблон для администратора
    }

    return render(request, 'registration/profile.html', context)




@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.user != recipe.author and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на редактирование этого рецепта.')
        return redirect('recipe_detail', pk=pk)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рецепт успешно обновлен.')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/recipe_edit.html', {'form': form})


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.user != recipe.author and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на удаление этого рецепта.')
        return redirect('recipe_detail', pk=pk)

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Рецепт успешно удален.')
        return redirect('profile')

    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})





def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    # Подсчет лайков и дизлайков
    likes = recipe.like_set.filter(is_like=True).count()
    dislikes = recipe.like_set.filter(is_like=False).count()

    # Работа с комментариями
    comments = recipe.comments.all()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            comment.save()
            return redirect('recipe_detail', pk=recipe.pk)  # Обновляем страницу после добавления комментария
    else:
        comment_form = CommentForm()

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'likes': likes,
        'dislikes': dislikes,
        'comments': comments,
        'comment_form': comment_form,
    })




@login_required
def recipe_add(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)  # Добавляем request.FILES для обработки загрузки файлов
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('recipe_list')  # После добавления перенаправляем на список рецептов
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_add.html', {'form': form})



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            messages.success(request, f'Регистрация прошла успешно! Добро пожаловать, {username}!')

            # Автоматически аутентифицируем пользователя после регистрации
            user = authenticate(username=username, password=password)
            login(request, user)  # Выполняем вход пользователя

            return redirect('profile')  # Перенаправляем в личный кабинет
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})



@login_required
def like_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        # Если лайк уже существует, то поменяем его
        like.is_like = not like.is_like
        like.save()

    return redirect('recipe_detail', pk=recipe.pk)


@login_required
def dislike_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)

    if created:
        # Если лайк был только что создан, сразу устанавливаем его на дизлайк
        like.is_like = False
    else:
        # Если запись уже существует, проверяем текущий статус
        if like.is_like:  # Если это был лайк, меняем на дизлайк
            like.is_like = False
        else:
            like.delete()  # Если это был дизлайк, удаляем запись

    like.save()

    return redirect('recipe_detail', pk=recipe.pk)
