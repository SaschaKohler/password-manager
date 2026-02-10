from django.urls import path
from . import views

app_name = 'passwords'

urlpatterns = [
    # Password entries
    path('', views.password_entries, name='password_entries'),
    path('<int:pk>/', views.password_entry_detail, name='password_entry_detail'),
    
    # Categories
    path('categories/', views.password_categories, name='password_categories'),
    path('categories/create/', views.create_category, name='create_category'),
    
    # Password generation
    path('generate/', views.generate_password, name='generate_password'),
    path('validate/', views.validate_password, name='validate_password'),
    
    # Sharing
    path('<int:pk>/share/', views.share_password, name='share_password'),
    path('shared-with-me/', views.shared_with_me, name='shared_with_me'),
    path('shared-by-me/', views.shared_by_me, name='shared_by_me'),
    
    # Bulk operations
    path('bulk/', views.bulk_operations, name='bulk_operations'),
    
    # Security audit
    path('audit/', views.security_audit, name='security_audit'),
    
    # Import/Export
    path('import/', views.import_passwords, name='import_passwords'),
    path('export/', views.export_passwords, name='export_passwords'),
]
