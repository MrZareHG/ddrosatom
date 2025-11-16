from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class News(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'На модерации'),
        ('published', 'Опубликовано'),
        ('archived', 'В архиве'),
    ]

    # Основная информация
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Содержание")
    excerpt = models.TextField("Краткое описание", max_length=500, blank=True)

    # Визуализация
    cover_image = models.ImageField("Обложка", upload_to='news/covers/', blank=True)

    # Автор и организация
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    nko = models.ForeignKey(
        'organizations.NKO',
        on_delete=models.CASCADE,
        verbose_name="НКО",
        null=True,
        blank=True
    )

    # Мета-информация
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField("Рекомендуемая", default=False)
    allow_comments = models.BooleanField("Разрешить комментарии", default=True)

    # Локация
    city = models.CharField("Город", max_length=100)

    # Даты
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    published_at = models.DateTimeField("Опубликовано", null=True, blank=True)

    # Системные поля
    view_count = models.PositiveIntegerField("Просмотры", default=0)
    slug = models.SlugField("URL", max_length=200, unique=True)

    # Связь с комментариями
    comments = GenericRelation('Comment')

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['city', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == 'published' and self.published_at <= timezone.now()


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('volunteer', 'Волонтерское мероприятие'),
        ('meeting', 'Встреча'),
        ('training', 'Обучение'),
        ('conference', 'Конференция'),
        ('celebration', 'Праздник'),
        ('cleanup', 'Субботник'),
        ('fundraising', 'Сбор средств'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'На модерации'),
        ('published', 'Опубликовано'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    # Основная информация
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    event_type = models.CharField("Тип мероприятия", max_length=20, choices=EVENT_TYPE_CHOICES)

    # Даты и время
    start_date = models.DateTimeField("Начало")
    end_date = models.DateTimeField("Окончание")
    registration_deadline = models.DateTimeField("Дедлайн регистрации", null=True, blank=True)

    # Место проведения
    city = models.CharField("Город", max_length=100)
    address = models.TextField("Адрес")
    online = models.BooleanField("Онлайн мероприятие", default=False)
    online_link = models.URLField("Ссылка для онлайн", blank=True)

    # Организатор
    nko = models.ForeignKey(
        'organizations.NKO',
        on_delete=models.CASCADE,
        verbose_name="Организатор",
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Создатель"
    )

    # Участники
    max_participants = models.PositiveIntegerField("Макс. участников", null=True, blank=True)
    current_participants = models.PositiveIntegerField("Текущее кол-во участников", default=0)

    # Статус и видимость
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField("Рекомендуемое", default=False)

    # Дополнительная информация
    requirements = models.TextField("Требования к участникам", blank=True)
    what_to_bring = models.TextField("Что взять с собой", blank=True)
    contact_info = models.TextField("Контактная информация", blank=True)

    # Даты
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    # Связь с комментариями
    comments = GenericRelation('Comment')

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date', 'status']),
            models.Index(fields=['city', 'event_type']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%d.%m.%Y')})"

    @property
    def is_registration_open(self):
        if self.registration_deadline:
            return timezone.now() < self.registration_deadline and self.status == 'published'
        return self.status == 'published'

    @property
    def has_free_slots(self):
        if not self.max_participants:
            return True
        return self.current_participants < self.max_participants

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now() and self.status == 'published'

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.status == 'published'


class KnowledgeBase(models.Model):
    CATEGORY_CHOICES = [
        ('guide', 'Руководство'),
        ('law', 'Правовые вопросы'),
        ('finance', 'Фандрайзинг'),
        ('volunteer', 'Работа с волонтерами'),
        ('reporting', 'Отчетность'),
        ('success_story', 'История успеха'),
        ('methodology', 'Методические материалы'),
    ]

    # Основная информация
    title = models.CharField("Название", max_length=200)
    content = models.TextField("Содержание")
    excerpt = models.TextField("Краткое описание", blank=True)

    # Категория и тип
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES)
    is_public = models.BooleanField("Публичный материал", default=True)
    difficulty_level = models.CharField("Уровень сложности", max_length=20,
                                        choices=[('beginner', 'Начальный'),
                                                 ('intermediate', 'Средний'),
                                                 ('advanced', 'Продвинутый')],
                                        default='beginner')

    # Автор
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )

    # Файлы
    attached_file = models.FileField(
        "Прикрепленный файл",
        upload_to='knowledgebase/',
        blank=True
    )

    # Мета-информация
    view_count = models.PositiveIntegerField("Просмотры", default=0)
    download_count = models.PositiveIntegerField("Скачивания", default=0)

    # Даты
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    # Связь с комментариями
    comments = GenericRelation('Comment')

    class Meta:
        verbose_name = "Материал базы знаний"
        verbose_name_plural = "Материалы базы знаний"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    # Связь с контентом (полиморфная)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Автор и содержание
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField("Текст комментария")

    # Иерархия (для ответов)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Модерация
    is_approved = models.BooleanField("Одобрено", default=True)
    is_deleted = models.BooleanField("Удалено", default=False)

    # Даты
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"Комментарий от {self.author.username}"


class EventParticipation(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Зарегистрирован'),
        ('confirmed', 'Подтвержден'),
        ('attended', 'Принял участие'),
        ('cancelled', 'Отменил'),
        ('no_show', 'Не явился'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Мероприятие")

    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='registered')

    # Дополнительная информация
    notes = models.TextField("Заметки", blank=True)
    volunteer_hours = models.PositiveIntegerField("Часов волонтерства", null=True, blank=True)

    # Даты
    registered_at = models.DateTimeField("Зарегистрирован", auto_now_add=True)
    status_changed_at = models.DateTimeField("Статус изменен", auto_now=True)

    class Meta:
        unique_together = ['user', 'event']
        verbose_name = "Участие в мероприятии"
        verbose_name_plural = "Участия в мероприятиях"
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class ContentView(models.Model):
    """Модель для отслеживания просмотров контента"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['viewed_at']),
        ]

    def __str__(self):
        return f"Просмотр {self.content_object}"


class ContentLike(models.Model):
    """Модель для лайков контента"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['content_type', 'object_id', 'user']
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"

    def __str__(self):
        return f"Лайк от {self.user.username}"