from django.db.models import Count
from .models import NKO


class NKOService:
    @staticmethod
    def get_popular_nkos(limit=5):
        """Получить популярные НКО по просмотрам"""
        return NKO.objects.filter(status='approved', is_active=True).order_by('-view_count')[:limit]

    @staticmethod
    def get_nko_stats():
        """Статистика по НКО"""
        return {
            'total_nkos': NKO.objects.filter(status='approved', is_active=True).count(),
            'by_category': dict(NKO.objects.filter(status='approved')
                                .values('category')
                                .annotate(count=Count('id'))
                                .values_list('category', 'count')),
            'by_city': dict(NKO.objects.filter(status='approved')
                            .values('city')
                            .annotate(count=Count('id'))
                            .values_list('city', 'count')),
        }

    @staticmethod
    def get_nkos_by_city(city):
        """Получить НКО по городу"""
        return NKO.objects.filter(city=city, status='approved', is_active=True)