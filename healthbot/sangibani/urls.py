from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Page routes
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('health_game/', views.health_game, name='health_game'),
    path('sort_the_food/', views.sort_the_food, name='sort_the_food'),
    path('myth_vs_fact/', views.myth_vs_fact, name='myth_vs_fact'),
    path('meditation/', views.meditation, name='meditation'),
    path('Safety_Simon/', views.Safety_Simon, name='Safety_Simon'),
    path('entertainment/', views.entertainment, name='entertainment'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/delete-account/', views.delete_account, name='delete_account'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),

    # API routes
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/register/', views.register_api, name='register_api'),
    path('api/health/', views.health_check, name='health_check'),
    path('api/test-chatbot/', views.test_chatbot_connection, name='test_chatbot'),


    # WhatsApp routes
    path('whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    path('whatsapp/send-message/', views.send_whatsapp_message_view, name='send_whatsapp_message'),
    path('whatsapp/test/', views.whatsapp_test, name='whatsapp_test'),
    path('whatsapp/broadcast/', views.whatsapp_broadcast, name='whatsapp_broadcast'),
]
