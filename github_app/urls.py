from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('callback/', views.github_callback, name='github_callback'),
    path('profile/', views.profile, name='profile'),
    path('repo/<str:repo_name>/', views.repo_detail, name='repo_detail'),
    path('contribution_stats/', views.contribution_stats, name='contribution_stats'),
    path('activity_stats/', views.activity_stats_page, name='activity_stats_page'),
    path('language_statistics/', views.language_statistics, name='language_statistics'),
]
