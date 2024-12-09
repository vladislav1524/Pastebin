from django.urls import path
from . import views


app_name = 'app'

urlpatterns = [
    path('', views.paste_create, name='paste_create'),
    path('<str:unique_hash>/', views.paste_detail, name='paste_detail'),
    path('<str:unique_hash>/edit/', views.paste_edit, name='paste_edit'),
    path('<str:unique_hash>/delete/', views.paste_delete, name='paste_delete'),
]
