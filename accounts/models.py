from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = [
        ('volunteer', 'Волонтер'),
        ('nko_representative', 'Представитель НКО'),
        ('corporate_volunteer', 'Корпоративный волонтер'),
        ('corporate_coordinator', 'Координатор предприятия'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    # Основные поля (наследуются от AbstractUser):
    # username, email, first_name, last_name, password, is_active, etc.

    # Дополнительные поля:
    role = models.CharField(
        "Роль в системе",
        max_length=30,
        choices=ROLE_CHOICES,
        default='volunteer'
    )

    # Контактная информация
    phone = models.CharField("Телефон", max_length=20, blank=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True)

    # Локация
    city = models.CharField("Город", max_length=100, blank=True)

    # Профиль
    bio = models.TextField("О себе", blank=True)
    skills = models.CharField("Навыки", max_length=500, blank=True, help_text="Через запятую")
    interests = models.CharField("Интересы", max_length=500, blank=True, help_text="Через запятую")

    # Статистика
    total_volunteer_hours = models.PositiveIntegerField("Всего часов волонтерства", default=0)
    events_participated = models.PositiveIntegerField("Участий в мероприятиях", default=0)

    # Настройки
    email_notifications = models.BooleanField("Email уведомления", default=True)
    newsletter_subscription = models.BooleanField("Подписка на рассылку", default=True)

    # Верификация
    email_verified = models.BooleanField("Email подтвержден", default=False)
    phone_verified = models.BooleanField("Телефон подтвержден", default=False)

    # Даты
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)
    last_activity = models.DateTimeField("Последняя активность", auto_now=True)
    email_verified_at = models.DateTimeField("Email подтвержден", null=True, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_nko_representative(self):
        return self.role == 'nko_representative'

    def is_corporate_coordinator(self):
        return self.role == 'corporate_coordinator'

    def is_moderator_or_admin(self):
        return self.role in ['moderator', 'admin']

    def update_activity(self):
        """Обновить время последней активности"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class VerificationCode(models.Model):
    TYPE_CHOICES = [
        ('email_verification', 'Подтверждение email'),
        ('phone_verification', 'Подтверждение телефона'),
        ('password_reset', 'Сброс пароля'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    code_type = models.CharField("Тип кода", max_length=20, choices=TYPE_CHOICES)
    code = models.CharField("Код", max_length=6)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    expires_at = models.DateTimeField("Истекает")
    is_used = models.BooleanField("Использован", default=False)

    class Meta:
        verbose_name = "Код верификации"
        verbose_name_plural = "Коды верификации"
        indexes = [
            models.Index(fields=['user', 'code_type', 'is_used']),
        ]

    def __str__(self):
        return f"{self.code_type} для {self.user.username}"

    def is_valid(self):
        """Проверка валидности кода"""
        return not self.is_used and timezone.now() < self.expires_at


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('profile_update', 'Обновление профиля'),
        ('password_change', 'Смена пароля'),
        ('email_verification', 'Подтверждение email'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    action = models.CharField("Действие", max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField("IP адрес", blank=True, null=True)
    user_agent = models.TextField("User Agent", blank=True)
    timestamp = models.DateTimeField("Время", auto_now_add=True)

    class Meta:
        verbose_name = "Активность пользователя"
        verbose_name_plural = "Активности пользователей"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


class UserProfile(models.Model):
    """Дополнительная информация профиля (можно вынести отдельно)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Социальные сети
    vk_link = models.URLField("VK", blank=True)
    telegram_link = models.URLField("Telegram", blank=True)

    # Дополнительная информация
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    occupation = models.CharField("Род занятий", max_length=200, blank=True)
    organization = models.CharField("Организация", max_length=200, blank=True)

    # Навыки волонтера
    volunteer_experience = models.TextField("Опыт волонтерства", blank=True)
    available_weekdays = models.CharField("Доступные дни", max_length=100, blank=True)
    has_car = models.BooleanField("Есть автомобиль", default=False)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    def __str__(self):
        return f"Профиль {self.user.username}"