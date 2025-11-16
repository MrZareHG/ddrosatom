from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import News, Event, KnowledgeBase, Comment, EventParticipation, ContentView, ContentLike


class CommentInline(GenericTabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'city', 'status', 'published_at', 'view_count']
    list_filter = ['status', 'city', 'created_at', 'is_featured']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]

    actions = ['publish_news', 'archive_news']

    def publish_news(self, request, queryset):
        queryset.update(status='published', published_at=timezone.now())

    publish_news.short_description = "Опубликовать выбранные новости"

    def archive_news(self, request, queryset):
        queryset.update(status='archived')

    archive_news.short_description = "Архивировать выбранные новости"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'city', 'start_date', 'status', 'current_participants']
    list_filter = ['status', 'event_type', 'city', 'start_date']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'current_participants']
    date_hierarchy = 'start_date'

    actions = ['publish_events', 'cancel_events']

    def publish_events(self, request, queryset):
        queryset.update(status='published')

    publish_events.short_description = "Опубликовать выбранные мероприятия"

    def cancel_events(self, request, queryset):
        queryset.update(status='cancelled')

    cancel_events.short_description = "Отменить выбранные мероприятия"


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'difficulty_level', 'is_public', 'view_count']
    list_filter = ['category', 'difficulty_level', 'is_public', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'download_count']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_type', 'object_id', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at', 'content_type']
    search_fields = ['author__username', 'text']
    readonly_fields = ['created_at', 'updated_at']

    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = "Одобрить выбранные комментарии"

    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)

    reject_comments.short_description = "Отклонить выбранные комментарии"


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registered_at']
    list_filter = ['status', 'registered_at']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['registered_at', 'status_changed_at']


@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'content_type']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['viewed_at']


@admin.register(ContentLike)
class ContentLikeAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'user', 'created_at']
    list_filter = ['created_at', 'content_type']
    search_fields = ['user__username']
    readonly_fields = ['created_at']