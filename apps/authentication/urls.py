from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('enable-2fa/', views.enable_2fa, name='enable_2fa'),
    path('verify-2fa-setup/', views.verify_2fa_setup, name='verify_2fa_setup'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('security-status/', views.security_status, name='security_status'),
    path('security-logs/', views.security_logs, name='security_logs'),
]
