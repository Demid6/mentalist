from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('cases/', views.cases, name='cases'),
    path('academy/', views.academy, name='academy'),
    path('operations/', views.operations, name='operations'),
    path('news/', views.news, name='news_legacy'),
    path('matches/', views.matches, name='matches_legacy'),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('feedback/', views.feedback, name='feedback'),
    path('comments/', views.comments_page, name='comments'),
    path('api/comments/', views.api_comments, name='api_comments'),
    path('api/comments/add/', views.api_add_comment, name='api_add_comment'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/feedback/', views.api_feedback, name='api_feedback'),
]