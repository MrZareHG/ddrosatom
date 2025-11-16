from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Новости
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),

    # Мероприятия
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/register/', views.event_register, name='event_register'),

    # База знаний
    path('knowledge/', views.knowledge_base_list, name='knowledge_base_list'),
    path('knowledge/<int:pk>/', views.knowledge_base_detail, name='knowledge_base_detail'),

    # Календарь
    path('calendar/', views.calendar_view, name='calendar'),

    # Лайки
    path('like/<str:content_type>/<int:object_id>/', views.like_content, name='like_content'),
]