from django.utils import timezone
from django.db.models import Count
from datetime import datetime, timedelta
import calendar

from .models import News, Event, KnowledgeBase, ContentView, ContentLike


class ContentService:
    @staticmethod
    def record_view(content_object, request):
        """Запись просмотра контента"""
        content_type = ContentType.objects.get_for_model(content_object)

        # Увеличиваем счетчик просмотров у объекта
        content_object.view_count += 1
        content_object.save(update_fields=['view_count'])

        # Создаем запись о просмотре
        ContentView.objects.create(
            content_type=content_type,
            object_id=content_object.id,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ContentService.get_client_ip(request)
        )

    @staticmethod
    def get_client_ip(request):
        """Получить IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_calendar_data(date, events):
        """Формирование данных для календаря"""
        cal = calendar.Calendar()
        month_days = cal.monthdatescalendar(date.year, date.month)

        calendar_data = []
        for week in month_days:
            week_data = []
            for day in week:
                day_events = [
                    event for event in events
                    if event.start_date.date() <= day <= event.end_date.date()
                ]
                week_data.append({
                    'date': day,
                    'events': day_events,
                    'events_count': len(day_events),
                    'is_current_month': day.month == date.month
                })
            calendar_data.append(week_data)

        return calendar_data

    @staticmethod
    def get_popular_content(limit=5):
        """Получить популярный контент"""
        return {
            'news': News.objects.filter(status='published').order_by('-view_count')[:limit],
            'events': Event.objects.filter(status='published').order_by('-view_count')[:limit],
            'knowledge': KnowledgeBase.objects.filter(is_public=True).order_by('-view_count')[:limit],
        }

    @staticmethod
    def get_content_stats():
        """Статистика по контенту"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        return {
            'total_news': News.objects.filter(status='published').count(),
            'total_events': Event.objects.filter(status='published').count(),
            'total_knowledge': KnowledgeBase.objects.filter(is_public=True).count(),
            'news_this_week': News.objects.filter(
                status='published',
                created_at__date__gte=week_ago
            ).count(),
            'events_this_week': Event.objects.filter(
                status='published',
                created_at__date__gte=week_ago
            ).count(),
            'upcoming_events': Event.objects.filter(
                status='published',
                start_date__gte=timezone.now()
            ).count(),
        }

    @staticmethod
    def search_content(query, content_types=None):
        """Поиск по контенту"""
        if content_types is None:
            content_types = ['news', 'events', 'knowledge']

        results = {}

        if 'news' in content_types:
            results['news'] = News.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                status='published'
            )[:10]

        if 'events' in content_types:
            results['events'] = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
                status='published'
            )[:10]

        if 'knowledge' in content_types:
            results['knowledge'] = KnowledgeBase.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                is_public=True
            )[:10]

        return results


class EventService:
    @staticmethod
    def get_upcoming_events(limit=10):
        """Получить ближайшие мероприятия"""
        return Event.objects.filter(
            status='published',
            start_date__gte=timezone.now()
        ).order_by('start_date')[:limit]

    @staticmethod
    def get_events_by_city(city, limit=5):
        """Получить мероприятия по городу"""
        return Event.objects.filter(
            status='published',
            city=city,
            start_date__gte=timezone.now()
        ).order_by('start_date')[:limit]

    @staticmethod
    def get_user_events(user, status=None):
        """Получить мероприятия пользователя"""
        participations = EventParticipation.objects.filter(user=user)
        if status:
            participations = participations.filter(status=status)

        return [participation.event for participation in participations.select_related('event')]

    @staticmethod
    def cancel_registration(user, event):
        """Отмена регистрации на мероприятие"""
        try:
            participation = EventParticipation.objects.get(user=user, event=event)
            participation.status = 'cancelled'
            participation.save()

            # Уменьшаем счетчик участников
            event.current_participants = max(0, event.current_participants - 1)
            event.save()

            return True
        except EventParticipation.DoesNotExist:
            return False


class NewsService:
    @staticmethod
    def get_latest_news(limit=5):
        """Получить последние новости"""
        return News.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:limit]

    @staticmethod
    def get_featured_news(limit=3):
        """Получить рекомендованные новости"""
        return News.objects.filter(
            status='published',
            is_featured=True,
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:limit]

    @staticmethod
    def get_news_by_city(city, limit=5):
        """Получить новости по городу"""
        return News.objects.filter(
            status='published',
            city=city,
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:limit]


class KnowledgeBaseService:
    @staticmethod
    def get_popular_materials(limit=5):
        """Получить популярные материалы"""
        return KnowledgeBase.objects.filter(is_public=True).order_by('-view_count')[:limit]

    @staticmethod
    def get_materials_by_category(category, limit=10):
        """Получить материалы по категории"""
        return KnowledgeBase.objects.filter(
            is_public=True,
            category=category
        ).order_by('-created_at')[:limit]

    @staticmethod
    def get_categories_with_counts():
        """Получить категории с количеством материалов"""
        return KnowledgeBase.objects.filter(is_public=True).values(
            'category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')