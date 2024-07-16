from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('callback/', views.github_callback, name='github_callback'),
    path('profile/', views.profile, name='profile'),
    path('repo/<str:repo_name>/', views.repo_detail, name='repo_detail'),
    path('stats/', views.activity_stats, name='activity_stats'),
]
