# core/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('ajax/suggest-skills/', views.suggest_skills, name='suggest-skills'),

    # --- NEW URLS FOR PHASE 3 ---
    path('browse/', views.browse_users, name='browse_users'),
    path('user/<int:user_id>/', views.user_public_profile, name='user_public_profile'),
    path('dashboard/', views.swap_dashboard, name='dashboard'),
    
    # Action URLs
    path('request-swap/<int:user_id>/', views.send_swap_request, name='send_swap_request'),
    path('update-swap/<int:request_id>/<str:new_status>/', views.update_swap_status, name='update_swap_status'),
    path('review/<int:swap_request_id>/', views.leave_review, name='leave_review'),
    path('ai-matchmaker/', views.ai_matchmaker, name='ai_matchmaker'),

    path('quiz/generate/<int:skill_id>/', views.generate_skill_quiz, name='generate_skill_quiz'),
    path('quiz/submit/', views.submit_skill_quiz, name='submit_skill_quiz'),

    path('chatbot/', views.ai_chatbot, name='ai_chatbot'),

]