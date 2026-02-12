from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from typing import Optional, List, Dict, Any
import json
import uuid

from core.crypto.encryption import PasswordEncryption, KeyManager
from core.crypto.exceptions import EncryptionError, DecryptionError

User = get_user_model()


class PasswordEntry(models.Model):
    """Encrypted password entry for users."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_entries')
    title = models.CharField(max_length=255)  # Stored in plaintext for searching
    encrypted_data = models.TextField()  # Base64-encoded encrypted JSON data
    category = models.CharField(max_length=100, blank=True, default='')
    tags = models.JSONField(default=list, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    # Metadata (stored in plaintext for filtering/sorting)
    username_hint = models.CharField(max_length=255, blank=True)  # First few chars only
    url_hint = models.CharField(max_length=255, blank=True)  # Domain only
    has_notes = models.BooleanField(default=False)

    # Custom fields for flexible schema (for imports from other password managers)
    # Stores additional fields that don't fit the standard schema
    custom_fields = models.JSONField(default=dict, blank=True)

    # Source tracking for imports
    source = models.CharField(max_length=50, blank=True, default='')  # e.g., '1password', 'bitwarden', 'lastpass'
    source_id = models.CharField(max_length=255, blank=True, default='')  # Original ID from source
    
    class Meta:
        db_table = 'password_entries'
        indexes = [
            models.Index(fields=['user', 'title']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['tags']),
        ]
        ordering = ['-is_favorite', 'title']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.title}"
    
    def get_encryption_key(self) -> bytes:
        """Get user's encryption key."""
        # The encryption_key is stored as a hex string in the database
        # Decode it to bytes for use with AES-256
        return bytes.fromhex(self.user.encryption_key)
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt password entry data."""
        try:
            key = self.get_encryption_key()
            encryptor = PasswordEncryption(key)
            return encryptor.encrypt_password_entry(
                title=data.get('title', ''),
                username=data.get('username', ''),
                password=data.get('password', ''),
                url=data.get('url', ''),
                notes=data.get('notes', ''),
                username2=data.get('username2'),
                username3=data.get('username3'),
                otp_url=data.get('otp_url'),
                custom_fields=data.get('custom_fields')
            )
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt password entry: {str(e)}")
    
    def decrypt_data(self) -> Dict[str, Any]:
        """Decrypt password entry data."""
        try:
            key = self.get_encryption_key()
            encryptor = PasswordEncryption(key)
            return encryptor.decrypt_password_entry(self.encrypted_data)
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt password entry: {str(e)}")
    
    def get_password(self) -> str:
        """Get decrypted password."""
        data = self.decrypt_data()
        return data.get('password', '')
    
    def get_username(self) -> str:
        """Get decrypted username."""
        data = self.decrypt_data()
        return data.get('username', '')
    
    def get_url(self) -> Optional[str]:
        """Get decrypted URL."""
        data = self.decrypt_data()
        return data.get('url')
    
    def get_notes(self) -> Optional[str]:
        """Get decrypted notes."""
        data = self.decrypt_data()
        return data.get('notes')
    
    def update_hints(self, data: Dict[str, Any]) -> None:
        """Update searchable hints from encrypted data."""
        # Username hint (first 3 characters)
        username = data.get('username', '')
        if len(username) >= 3:
            self.username_hint = username[:3] + '*' * (len(username) - 3)
        else:
            self.username_hint = username + '*' * max(0, 3 - len(username))
        
        # URL hint (domain only)
        url = data.get('url', '')
        if url and ('://' in url):
            domain = url.split('://')[1].split('/')[0]
            self.url_hint = domain
        else:
            self.url_hint = ''
        
        # Notes flag
        notes = data.get('notes', '')
        self.has_notes = bool(notes.strip() if notes else False)
    
    def update_from_data(self, data: Dict[str, Any]) -> None:
        """Update entry from decrypted data."""
        self.title = data.get('title', '')
        self.encrypted_data = self.encrypt_data(data)
        self.category = data.get('category', '')
        self.tags = data.get('tags', [])
        self.is_favorite = data.get('is_favorite', False)
        self.custom_fields = data.get('custom_fields', {})
        self.source = data.get('source', '')
        self.source_id = data.get('source_id', '')
        self.update_hints(data)
        self.save()
    
    def access(self) -> None:
        """Record access to this entry."""
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])
    
    @classmethod
    def create_entry(cls, user: User, title: str, username: str, password: str,
                     url: Optional[str] = None, notes: Optional[str] = None,
                     category: str = '', tags: Optional[List[str]] = None,
                     is_favorite: bool = False, username2: Optional[str] = None,
                     username3: Optional[str] = None, otp_url: Optional[str] = None,
                     custom_fields: Optional[Dict[str, Any]] = None,
                     source: str = '', source_id: str = '') -> 'PasswordEntry':
        """Create a new password entry."""
        data = {
            'title': title,
            'username': username,
            'password': password,
            'url': url,
            'notes': notes,
            'category': category,
            'tags': tags or [],
            'is_favorite': is_favorite,
            'username2': username2,
            'username3': username3,
            'otp_url': otp_url,
            'custom_fields': custom_fields or {},
            'source': source,
            'source_id': source_id
        }

        entry = cls(user=user, title=title, category=category or '',
                    tags=tags or [], is_favorite=is_favorite,
                    custom_fields=custom_fields or {},
                    source=source, source_id=source_id)

        entry.encrypted_data = entry.encrypt_data(data)
        entry.update_hints(data)
        entry.save()

        return entry


class PasswordCategory(models.Model):
    """Password categories for organization."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    icon = models.CharField(max_length=50, default='folder')  # Icon name
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'password_categories'
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.name}"
    
    @classmethod
    def get_default_categories(cls, user: User) -> List['PasswordCategory']:
        """Get or create default categories for user."""
        defaults = [
            {'name': 'Personal', 'color': '#28a745', 'icon': 'user'},
            {'name': 'Work', 'color': '#007bff', 'icon': 'briefcase'},
            {'name': 'Finance', 'color': '#ffc107', 'icon': 'credit-card'},
            {'name': 'Social', 'color': '#17a2b8', 'icon': 'share'},
            {'name': 'Shopping', 'color': '#e83e8c', 'icon': 'shopping-cart'},
        ]
        
        categories = []
        for default in defaults:
            category, created = cls.objects.get_or_create(
                user=user,
                name=default['name'],
                defaults=default
            )
            categories.append(category)
        
        return categories


class PasswordShare(models.Model):
    """Shared password entries between users."""
    
    SHARE_TYPES = [
        ('view', 'View Only'),
        ('edit', 'Can Edit'),
        ('admin', 'Admin'),
    ]
    
    entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_entries')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_entries')
    share_type = models.CharField(max_length=10, choices=SHARE_TYPES, default='view')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'password_shares'
        unique_together = ['entry', 'shared_with']
        indexes = [
            models.Index(fields=['shared_with', 'is_active']),
            models.Index(fields=['shared_by', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.entry.title} shared by {self.shared_by.email} to {self.shared_with.email}"
    
    def is_expired(self) -> bool:
        """Check if share has expired."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if share is valid and active."""
        return self.is_active and not self.is_expired()


class SecurityAudit(models.Model):
    """Security audit log for password operations."""
    
    EVENT_TYPES = [
        ('create', 'Entry Created'),
        ('view', 'Entry Viewed'),
        ('edit', 'Entry Edited'),
        ('delete', 'Entry Deleted'),
        ('share', 'Entry Shared'),
        ('export', 'Data Exported'),
        ('import', 'Data Imported'),
        ('login', 'User Login'),
        ('security_change', 'Security Settings Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_audits')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    entry = models.ForeignKey(PasswordEntry, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_audits'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.event_type} - {self.timestamp}"
    
    @classmethod
    def log_event(cls, user: User, event_type: str, entry: Optional[PasswordEntry] = None,
                  ip_address: str = '', user_agent: str = '', details: Optional[Dict] = None) -> 'SecurityAudit':
        """Log a security event."""
        return cls.objects.create(
            user=user,
            event_type=event_type,
            entry=entry,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
