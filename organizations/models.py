from django.db import models

# Create your models here.
class NKO(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    CATEGORY_CHOICES = [
        ('ecology', 'Экология'),
        ('animals', 'Защита животных'),
        ('children', 'Помощь детям'),
        ('elderly', 'Помощь пожилым'),
        ('sport', 'Спорт'),
        ('culture', 'Культура'),
        ('education', 'Образование'),
        ('health', 'Здравоохранение'),
    ]

    # Основная информация
    name = models.CharField("Название НКО", max_length=200)
    description = models.TextField("Описание деятельности")
    mission = models.TextField("Миссия организации", blank=True)

    # Категории
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES)

    # Контакты
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=20, blank=True)
    website = models.URLField("Сайт", blank=True)
    social_links = models.JSONField("Соцсети", default=dict, blank=True)  # {vk: url, tg: url}

    # Локация
    city = models.CharField("Город", max_length=100)
    address = models.TextField("Адрес", blank=True)

    # Визуал
    logo = models.ImageField("Логотип", upload_to='nko/logos/', blank=True)
    cover_image = models.ImageField("Обложка", upload_to='nko/covers/', blank=True)

    # Владелец и статус
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name='owned_nkos'
    )
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='draft')

    # Даты
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    # Системные поля
    is_active = models.BooleanField("Активно", default=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class NKOMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('volunteer', 'Волонтер'),
        ('coordinator', 'Координатор'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('approved', 'Подтвержден'),
        ('rejected', 'Отклонен'),
        ('banned', 'Заблокирован'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name="Пользователь")
    nko = models.ForeignKey(NKO, on_delete=models.CASCADE, verbose_name="НКО")

    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')

    # Дополнительная информация
    responsibilities = models.TextField("Обязанности", blank=True)
    skills = models.CharField("Навыки", max_length=500, blank=True)

    # Даты
    joined_at = models.DateTimeField("Вступил", auto_now_add=True)

    class Meta:
        unique_together = ['user', 'nko']  # пользователь может быть в НКО только один раз
        verbose_name = "Членство в НКО"
        verbose_name_plural = "Членства в НКО"

    def __str__(self):
        return f"{self.user.username} в {self.nko.name} ({self.role})"