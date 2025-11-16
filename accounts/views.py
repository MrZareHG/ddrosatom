from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import random
import string

from .models import User, UserProfile, VerificationCode, UserActivity
from .forms import (CustomUserCreationForm, CustomUserChangeForm, UserProfileForm,
                    EmailVerificationForm, PasswordResetRequestForm, PasswordResetForm)
from .services import AuthService, VerificationService


def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Создаем профиль
            UserProfile.objects.create(user=user)

            # Логиним пользователя
            login(request, user)

            # Отправляем код верификации
            VerificationService.send_email_verification(user)

            # Записываем активность
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=AuthService.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            messages.success(request, 'Регистрация успешна! Подтвердите ваш email.')
            return redirect('accounts:email_verification')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Обновляем активность
            user.update_activity()

            # Записываем активность
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=AuthService.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            messages.success(request, f'Добро пожаловать, {user.first_name}!')

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """Выход из системы"""
    # Записываем активность перед выходом
    UserActivity.objects.create(
        user=request.user,
        action='logout',
        ip_address=AuthService.get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('accounts:login')


@login_required
def profile(request):
    """Профиль пользователя"""
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # Записываем активность
            UserActivity.objects.create(
                user=request.user,
                action='profile_update',
                ip_address=AuthService.get_client_ip(request)
            )

            messages.success(request, 'Профиль успешно обновлен')
            return redirect('accounts:profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def email_verification(request):
    """Подтверждение email"""
    if request.user.email_verified:
        messages.info(request, 'Ваш email уже подтвержден')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            if VerificationService.verify_email_code(request.user, code):
                request.user.email_verified = True
                request.user.email_verified_at = timezone.now()
                request.user.save()

                UserActivity.objects.create(
                    user=request.user,
                    action='email_verification',
                    ip_address=AuthService.get_client_ip(request)
                )

                messages.success(request, 'Email успешно подтвержден!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Неверный код или срок его действия истек')
    else:
        form = EmailVerificationForm()

        # Отправляем код при загрузке страницы (если еще не отправляли)
        if not VerificationService.has_active_email_code(request.user):
            VerificationService.send_email_verification(request.user)
            messages.info(request, 'Код подтверждения отправлен на ваш email')

    return render(request, 'accounts/email_verification.html', {'form': form})


@login_required
def resend_verification_code(request):
    """Повторная отправка кода верификации"""
    if VerificationService.send_email_verification(request.user):
        messages.success(request, 'Новый код подтверждения отправлен на ваш email')
    else:
        messages.error(request, 'Не удалось отправить код. Попробуйте позже.')

    return redirect('accounts:email_verification')


def password_reset_request(request):
    """Запрос на сброс пароля"""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                VerificationService.send_password_reset_code(user)
                messages.success(request, 'Инструкции по сбросу пароля отправлены на ваш email')
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


@login_required
def password_change(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()

            # Обновляем сессию чтобы пользователь не разлогинился
            update_session_auth_hash(request, request.user)

            UserActivity.objects.create(
                user=request.user,
                action='password_change',
                ip_address=AuthService.get_client_ip(request)
            )

            messages.success(request, 'Пароль успешно изменен')
            return redirect('accounts:profile')
    else:
        form = PasswordResetForm()

    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def activity_log(request):
    """История активности пользователя"""
    activities = UserActivity.objects.filter(user=request.user)[:50]
    return render(request, 'accounts/activity_log.html', {'activities': activities})