from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    path('', views.nko_list, name='nko_list'),
    path('create/', views.nko_create, name='nko_create'),
    path('my/', views.my_organizations, name='my_organizations'),
    path('<int:pk>/', views.nko_detail, name='nko_detail'),
    path('<int:pk>/edit/', views.nko_edit, name='nko_edit'),
    path('<int:pk>/join/', views.nko_join, name='nko_join'),
]