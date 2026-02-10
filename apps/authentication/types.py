"""
Type definitions for authentication app.

This module provides type hints for better code clarity and IDE support.
"""

from typing import TypedDict, Dict, List, Optional, Any, Union
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from rest_framework.request import Request


class UserRegistrationData(TypedDict):
    """Type definition for user registration data."""
    email: str
    username: str
    password: str
    password_confirm: str


class LoginData(TypedDict):
    """Type definition for login data."""
    email: str
    password: str
    totp_code: Optional[str]


class TOTPSetupData(TypedDict):
    """Type definition for TOTP setup data."""
    totp_code: str


class PasswordChangeData(TypedDict):
    """Type definition for password change data."""
    current_password: str
    new_password: str
    new_password_confirm: str


class BackupCodeData(TypedDict):
    """Type definition for backup code data."""
    backup_code: str


class SecurityStatusResponse(TypedDict):
    """Type definition for security status response."""
    totp_enabled: bool
    backup_codes_count: int
    last_password_change: datetime
    failed_login_attempts: int
    is_locked: bool
    locked_until: Optional[datetime]


class SecurityLogResponse(TypedDict):
    """Type definition for security log response."""
    event_type: str
    description: str
    ip_address: str
    timestamp: datetime


class UserSessionData(TypedDict):
    """Type definition for user session data."""
    user_id: int
    session_key: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool


class APIResponse(TypedDict, total=False):
    """Generic API response type."""
    message: str
    error: str
    user_id: Optional[int]
    email: Optional[str]
    totp_enabled: Optional[bool]
    require_2fa: Optional[bool]
    totp_secret: Optional[str]
    totp_uri: Optional[str]
    backup_codes: Optional[List[str]]


class SecurityEventType:
    """Constants for security event types."""
    LOGIN = 'login'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    TWO_FA_ENABLED = '2fa_enabled'
    TWO_FA_DISABLED = '2fa_disabled'
    BACKUP_CODE_USED = 'backup_code_used'
    ACCOUNT_LOCKED = 'account_locked'
    FAILED_LOGIN = 'failed_login'
    PASSWORD_RESET = 'password_reset'


class UserPreferences(TypedDict):
    """Type definition for user preferences."""
    password_generator_length: int
    password_generator_symbols: bool


class AuthenticationResult(TypedDict):
    """Type definition for authentication result."""
    success: bool
    user: Optional[AbstractUser]
    error: Optional[str]
    requires_2fa: bool


class TOTPVerificationResult(TypedDict):
    """Type definition for TOTP verification result."""
    valid: bool
    error: Optional[str]


class SessionInfo(TypedDict):
    """Type definition for session information."""
    session_key: str
    ip_address: str
    user_agent: str
    is_active: bool
    created_at: datetime
    last_activity: datetime


class SecurityContext(TypedDict):
    """Type definition for security context."""
    ip_address: str
    user_agent: str
    request: Request


class ValidationErrorDict(TypedDict):
    """Type definition for validation errors."""
    [field_name: str]: List[str]


class DatabaseFieldTypes:
    """Constants for database field types."""
    
    class User:
        EMAIL = 'email'
        USERNAME = 'username'
        MASTER_PASSWORD_HASH = 'master_password_hash'
        MASTER_PASSWORD_SALT = 'master_password_salt'
        ENCRYPTION_KEY = 'encryption_key'
        TOTP_SECRET = 'totp_secret'
        TOTP_ENABLED = 'totp_enabled'
        BACKUP_CODES = 'backup_codes'
        LAST_PASSWORD_CHANGE = 'last_password_change'
        FAILED_LOGIN_ATTEMPTS = 'failed_login_attempts'
        LOCKED_UNTIL = 'locked_until'
        PASSWORD_GENERATOR_LENGTH = 'password_generator_length'
        PASSWORD_GENERATOR_SYMBOLS = 'password_generator_symbols'
    
    class UserSession:
        USER = 'user'
        SESSION_KEY = 'session_key'
        IP_ADDRESS = 'ip_address'
        USER_AGENT = 'user_agent'
        CREATED_AT = 'created_at'
        LAST_ACTIVITY = 'last_activity'
        IS_ACTIVE = 'is_active'
    
    class SecurityLog:
        USER = 'user'
        EVENT_TYPE = 'event_type'
        IP_ADDRESS = 'ip_address'
        USER_AGENT = 'user_agent'
        DESCRIPTION = 'description'
        TIMESTAMP = 'timestamp'


class APIEndpoints:
    """Constants for API endpoints."""
    
    class Authentication:
        REGISTER = 'register'
        LOGIN = 'login'
        LOGOUT = 'logout'
        ENABLE_2FA = 'enable_2fa'
        VERIFY_2FA_SETUP = 'verify_2fa_setup'
        DISABLE_2FA = 'disable_2fa'
        SECURITY_STATUS = 'security_status'
        SECURITY_LOGS = 'security_logs'


class HTTPStatus:
    """Constants for HTTP status codes."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    LOCKED = 423
    INTERNAL_SERVER_ERROR = 500


class ConfigKeys:
    """Constants for configuration keys."""
    
    class Environment:
        SECRET_KEY = 'SECRET_KEY'
        DEBUG = 'DEBUG'
        ALLOWED_HOSTS = 'ALLOWED_HOSTS'
        DATABASE_URL = 'DATABASE_URL'
        REDIS_URL = 'REDIS_URL'
        ENCRYPTION_KEY = 'ENCRYPTION_KEY'
        JWT_SECRET_KEY = 'JWT_SECRET_KEY'
        CORS_ALLOWED_ORIGINS = 'CORS_ALLOWED_ORIGINS'
        LOG_LEVEL = 'LOG_LEVEL'
        LOG_FILE = 'LOG_FILE'
    
    class Security:
        SECURE_SSL_REDIRECT = 'SECURE_SSL_REDIRECT'
        SECURE_HSTS_SECONDS = 'SECURE_HSTS_SECONDS'
        SESSION_COOKIE_SECURE = 'SESSION_COOKIE_SECURE'
        SESSION_COOKIE_HTTPONLY = 'SESSION_COOKIE_HTTPONLY'


# Generic type aliases for better readability
JSONDict = Dict[str, Any]
OptionalStr = Optional[str]
OptionalInt = Optional[int]
OptionalBool = Optional[bool]
OptionalDateTime = Optional[datetime]
ListOfStr = List[str]
DictOfStr = Dict[str, str]
