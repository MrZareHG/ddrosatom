from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профиль
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/activity/', views.activity_log, name='activity_log'),

    # Верификация
    path('verify/email/', views.email_verification, name='email_verification'),
    path('verify/email/resend/', views.resend_verification_code, name='resend_verification'),

    # Пароли
    path('password/reset/', views.password_reset_request, name='password_reset_request'),
    path('password/change/', views.password_change, name='password_change'),
]