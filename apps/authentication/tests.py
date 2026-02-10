from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
import pyotp
import json
from typing import Any, Dict

User = get_user_model()


class UserModelTests(TestCase):
    """Test cases for User model."""
    
    def setUp(self) -> None:
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
    
    def test_create_user(self) -> None:
        """Test user creation with master password."""
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertIsNotNone(user.master_password_hash)
        self.assertIsNotNone(user.master_password_salt)
        self.assertIsNotNone(user.encryption_key)
        self.assertFalse(user.totp_enabled)
        self.assertEqual(len(user.backup_codes), 10)
    
    def test_totp_functionality(self) -> None:
        """Test TOTP generation and verification."""
        user = User.objects.create_user(
            email='totp@example.com',
            username='totpuser',
            password='SecurePass123!'
        )
        
        # Generate TOTP secret
        secret = user.generate_totp_secret()
        self.assertIsNotNone(secret)
        self.assertEqual(user.totp_secret, secret)
        
        # Get TOTP URI
        uri = user.get_totp_uri()
        self.assertIsNotNone(uri)
        self.assertIn('totp%40example.com', uri)  # URL-encoded email
        
        # Verify TOTP token
        totp = pyotp.TOTP(secret)
        token = totp.now()
        self.assertTrue(user.verify_totp(token))
        self.assertFalse(user.verify_totp('invalid'))
    
    def test_backup_codes(self) -> None:
        """Test backup code generation and usage."""
        user = User.objects.create_user(
            email='backup@example.com',
            username='backupuser',
            password='SecurePass123!'
        )
        
        # Generate backup codes
        codes = user.generate_backup_codes()
        self.assertEqual(len(codes), 10)
        self.assertEqual(len(user.backup_codes), 10)
        
        # Use backup code
        code_to_use = codes[0]
        self.assertTrue(user.use_backup_code(code_to_use))
        self.assertEqual(len(user.backup_codes), 9)
        self.assertFalse(user.use_backup_code(code_to_use))  # Already used
    
    def test_account_lockout(self) -> None:
        """Test account lockout functionality."""
        user = User.objects.create_user(
            email='lockout@example.com',
            username='lockoutuser',
            password='SecurePass123!'
        )
        
        # Initially not locked
        self.assertFalse(user.is_account_locked())
        
        # Increment failed attempts
        for i in range(4):
            user.increment_failed_login()
            self.assertFalse(user.is_account_locked())
        
        # 5th attempt should lock account
        user.increment_failed_login()
        self.assertTrue(user.is_account_locked())
        self.assertEqual(user.failed_login_attempts, 5)
        self.assertIsNotNone(user.locked_until)
        
        # Reset failed login
        user.reset_failed_login()
        self.assertFalse(user.is_account_locked())
        self.assertEqual(user.failed_login_attempts, 0)
        self.assertIsNone(user.locked_until)


class AuthenticationAPITests(APITestCase):
    """Test cases for authentication API endpoints."""
    
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {
            'email': 'api@example.com',
            'username': 'apiuser',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
    
    def test_user_registration(self) -> None:
        """Test user registration endpoint."""
        url = reverse('authentication:register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        
        # Verify user was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.email, self.user_data['email'])
    
    def test_user_registration_invalid_data(self) -> None:
        """Test registration with invalid data."""
        url = reverse('authentication:register')
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self) -> None:
        """Test user login endpoint."""
        # Create user first
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        url = reverse('authentication:login')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
    
    def test_user_login_invalid_credentials(self) -> None:
        """Test login with invalid credentials."""
        url = reverse('authentication:login')
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'WrongPass123!'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_with_2fa(self) -> None:
        """Test login with 2FA enabled."""
        # Create user with 2FA
        user = User.objects.create_user(
            email='2fa@example.com',
            username='twofauser',
            password='SecurePass123!'
        )
        user.generate_totp_secret()
        user.totp_enabled = True
        user.save()
        
        url = reverse('authentication:login')
        login_data = {
            'email': '2fa@example.com',
            'password': 'SecurePass123!'
        }
        
        # Login without 2FA code should require 2FA
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['require_2fa'])
        
        # Login with valid 2FA code
        totp = pyotp.TOTP(user.totp_secret)
        login_data['totp_code'] = totp.now()
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_enable_2fa(self) -> None:
        """Test enabling 2FA."""
        # Create and login user
        user = User.objects.create_user(
            email='enable2fa@example.com',
            username='enable2fa',
            password='SecurePass123!'
        )
        self.client.force_login(user)
        
        url = reverse('authentication:enable_2fa')
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totp_secret', response.data)
        self.assertIn('totp_uri', response.data)
        self.assertIn('backup_codes', response.data)
        
        # Verify user has TOTP secret but not enabled yet
        user.refresh_from_db()
        self.assertIsNotNone(user.totp_secret)
        self.assertFalse(user.totp_enabled)
    
    def test_verify_2fa_setup(self) -> None:
        """Test verifying 2FA setup."""
        # Create and login user
        user = User.objects.create_user(
            email='verify2fa@example.com',
            username='verify2fa',
            password='SecurePass123!'
        )
        self.client.force_login(user)
        
        # Enable 2FA first
        user.generate_totp_secret()
        user.save()
        
        # Verify with valid TOTP code
        totp = pyotp.TOTP(user.totp_secret)
        url = reverse('authentication:verify_2fa_setup')
        data = {'totp_code': totp.now()}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify 2FA is now enabled
        user.refresh_from_db()
        self.assertTrue(user.totp_enabled)
    
    def test_disable_2fa(self) -> None:
        """Test disabling 2FA."""
        # Create user with 2FA enabled
        user = User.objects.create_user(
            email='disable2fa@example.com',
            username='disable2fa',
            password='SecurePass123!'
        )
        user.generate_totp_secret()
        user.totp_enabled = True
        user.save()
        
        self.client.force_login(user)
        
        url = reverse('authentication:disable_2fa')
        data = {'password': 'SecurePass123!'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify 2FA is disabled
        user.refresh_from_db()
        self.assertFalse(user.totp_enabled)
        self.assertIsNone(user.totp_secret)
        self.assertEqual(len(user.backup_codes), 0)
    
    def test_security_status(self) -> None:
        """Test security status endpoint."""
        user = User.objects.create_user(
            email='security@example.com',
            username='security',
            password='SecurePass123!'
        )
        self.client.force_login(user)
        
        url = reverse('authentication:security_status')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totp_enabled', response.data)
        self.assertIn('backup_codes_count', response.data)
        self.assertIn('failed_login_attempts', response.data)
    
    def test_security_logs(self) -> None:
        """Test security logs endpoint."""
        user = User.objects.create_user(
            email='logs@example.com',
            username='logs',
            password='SecurePass123!'
        )
        self.client.force_login(user)
        
        url = reverse('authentication:security_logs')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('logs', response.data)
        self.assertIsInstance(response.data['logs'], list)


class SecurityTests(TestCase):
    """Test security-related functionality."""
    
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='security@example.com',
            username='security',
            password='SecurePass123!'
        )
    
    def test_password_validation(self) -> None:
        """Test password validation requirements."""
        from django.core.exceptions import ValidationError
        
        weak_passwords = [
            '123456',  # Too short
            'password',  # Common password
            '111111111111',  # All numbers
            'aaaaaaaaaaaa',  # All letters
        ]
        
        for weak_pass in weak_passwords:
            with self.assertRaises(ValidationError):
                User.objects.create_user(
                    email=f'test_{weak_pass}@example.com',
                    username=f'test_{weak_pass}',
                    password=weak_pass
                )
    
    def test_session_tracking(self) -> None:
        """Test session creation and tracking."""
        from apps.authentication.models import UserSession
        
        # Simulate session creation
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)
    
    def test_security_logging(self) -> None:
        """Test security event logging."""
        from apps.authentication.models import SecurityLog
        
        # Create security log entry
        log = SecurityLog.objects.create(
            user=self.user,
            event_type='login',
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            description='Test login event'
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.event_type, 'login')
        self.assertIsNotNone(log.timestamp)
