from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import pyotp


class User(AbstractUser):
    """Custom user model with enhanced security features."""
    
    email = models.EmailField(unique=True)
    master_password_hash = models.CharField(max_length=255)
    master_password_salt = models.CharField(max_length=32)
    encryption_key = models.CharField(max_length=64)  # Encrypted at rest
    
    # 2FA settings
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    totp_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Security settings
    last_password_change = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    password_generator_length = models.IntegerField(default=16)
    password_generator_symbols = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return self.email
    
    def generate_totp_secret(self):
        """Generate new TOTP secret for 2FA."""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code generation."""
        if not self.totp_secret:
            return None
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name="Password Manager"
        )
    
    def verify_totp(self, token):
        """Verify TOTP token."""
        if not self.totp_secret or not self.totp_enabled:
            return False
        return pyotp.totp.TOTP(self.totp_secret).verify(token)
    
    def generate_backup_codes(self):
        """Generate 10 backup codes."""
        self.backup_codes = [secrets.token_hex(4) for _ in range(10)]
        self.save()
        return self.backup_codes
    
    def use_backup_code(self, code):
        """Use and remove a backup code."""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
    
    def is_account_locked(self):
        """Check if account is locked due to failed attempts."""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if necessary."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def reset_failed_login(self):
        """Reset failed login attempts on successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save()


class UserSession(models.Model):
    """Track user sessions for security monitoring."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class SecurityLog(models.Model):
    """Log security events for audit trail."""
    
    EVENT_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('backup_code_used', 'Backup Code Used'),
        ('account_locked', 'Account Locked'),
        ('failed_login', 'Failed Login'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_security_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.event_type} - {self.timestamp}"
