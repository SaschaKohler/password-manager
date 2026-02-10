from django.db.models.signals import post_save, user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.signals import user_login_failed
from django.utils import timezone
from .models import User, UserSession, SecurityLog
import ipaddress


@receiver(post_save, sender=User)
def create_user_security_settings(sender, instance, created, **kwargs):
    """Initialize security settings for new users."""
    if created:
        # Generate backup codes for new user
        instance.generate_backup_codes()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login and create session."""
    # Log security event
    SecurityLog.objects.create(
        user=user,
        event_type='login',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        description='User logged in successfully'
    )
    
    # Create or update session
    UserSession.objects.update_or_create(
        session_key=request.session.session_key,
        defaults={
            'user': user,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'is_active': True
        }
    )
    
    # Reset failed login attempts
    user.reset_failed_login()


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout and deactivate session."""
    if user:
        # Log security event
        SecurityLog.objects.create(
            user=user,
            event_type='logout',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description='User logged out'
        )
        
        # Deactivate session
        UserSession.objects.filter(
            session_key=request.session.session_key,
            user=user
        ).update(is_active=False)


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    try:
        user = User.objects.get(email=credentials.get('username', ''))
        user.increment_failed_login()
        
        # Log security event
        SecurityLog.objects.create(
            user=user,
            event_type='failed_login',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=f'Failed login attempt #{user.failed_login_attempts}'
        )
    except User.DoesNotExist:
        # Log failed attempt for non-existent user
        SecurityLog.objects.create(
            user=None,
            event_type='failed_login',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=f'Failed login attempt for unknown user: {credentials.get("username", "")}'
        )


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Validate IP address
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return '0.0.0.0'  # Invalid IP fallback
