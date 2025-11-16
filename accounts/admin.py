from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, VerificationCode, UserActivity


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'city', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'email_verified', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_activity')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        ('Профиль', {'fields': ('role', 'city', 'bio', 'skills', 'interests')}),
        ('Статистика', {'fields': ('total_volunteer_hours', 'events_participated')}),
        ('Настройки', {'fields': ('email_notifications', 'newsletter_subscription')}),
        ('Верификация', {'fields': ('email_verified', 'phone_verified', 'email_verified_at')}),
        ('Даты', {'fields': ('date_joined', 'last_activity')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'occupation', 'organization', 'has_car')
    search_fields = ('user__username', 'user__email', 'occupation', 'organization')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code_type', 'code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('code_type', 'is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('created_at',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('timestamp',)