from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
import json
import io
import csv
from typing import Dict, Any, List

from .models import PasswordEntry, PasswordCategory, PasswordShare, SecurityAudit
from core.crypto.encryption import PasswordEncryption, PasswordGenerator, validate_password_strength

User = get_user_model()


class PasswordEncryptionTests(TestCase):
    """Test password encryption functionality."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.master_key = b'test_key_32_bytes_long_123456789'  # 32 bytes
        self.encryptor = PasswordEncryption(self.master_key)
    
    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Test encryption and decryption roundtrip."""
        plaintext = "Test password 123!"
        
        # Encrypt
        encrypted = self.encryptor.encrypt(plaintext)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(plaintext, encrypted)
        
        # Decrypt
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertEqual(plaintext, decrypted)
    
    def test_encrypt_password_entry(self) -> None:
        """Test password entry encryption."""
        data = {
            'title': 'Test Entry',
            'username': 'testuser',
            'password': 'Secret123!',
            'url': 'https://example.com',
            'notes': 'Test notes'
        }
        
        encrypted = self.encryptor.encrypt_password_entry(**data)
        self.assertIsInstance(encrypted, str)
        
        # Decrypt and verify
        decrypted_data = self.encryptor.decrypt_password_entry(encrypted)
        self.assertEqual(decrypted_data['title'], data['title'])
        self.assertEqual(decrypted_data['username'], data['username'])
        self.assertEqual(decrypted_data['password'], data['password'])
    
    def test_invalid_key_error(self) -> None:
        """Test error handling for invalid key."""
        with self.assertRaises(Exception):
            PasswordEncryption(b'short_key')
    
    def test_decrypt_invalid_data(self) -> None:
        """Test decryption of invalid data."""
        with self.assertRaises(Exception):
            self.encryptor.decrypt("invalid_base64_data")


class PasswordGeneratorTests(TestCase):
    """Test password generation functionality."""
    
    def test_generate_password(self) -> None:
        """Test password generation."""
        password = PasswordGenerator.generate(length=16)
        
        self.assertEqual(len(password), 16)
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in PasswordGenerator.SYMBOLS for c in password))
    
    def test_generate_password_no_symbols(self) -> None:
        """Test password generation without symbols."""
        password = PasswordGenerator.generate(length=12, use_symbols=False)
        
        self.assertEqual(len(password), 12)
        self.assertFalse(any(c in PasswordGenerator.SYMBOLS for c in password))
    
    def test_generate_passphrase(self) -> None:
        """Test passphrase generation."""
        passphrase = PasswordGenerator.generate_passphrase(word_count=4)
        
        words = passphrase.split('-')
        self.assertEqual(len(words), 4)
        self.assertTrue(all(word.isalpha() for word in words))
    
    def test_password_strength_validation(self) -> None:
        """Test password strength validation."""
        # Strong password
        strong = validate_password_strength("StrongP@ssw0rd123!")
        self.assertGreaterEqual(strong['score'], 4)
        
        # Weak password
        weak = validate_password_strength("123456")
        self.assertLess(weak['score'], 3)
        self.assertTrue(len(weak['feedback']) > 0)


class PasswordEntryModelTests(TestCase):
    """Test PasswordEntry model functionality."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!'
        )
        # Set proper 32-byte encryption key for user
        self.user.encryption_key = 'test_key_32_bytes_long_123456789'  # 32 bytes
        self.user.save()
    
    def test_create_password_entry(self) -> None:
        """Test creating a password entry."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!',
            url='https://example.com',
            notes='Test notes',
            category='Personal',
            tags=['test', 'example']
        )
        
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.title, 'Test Entry')
        self.assertEqual(entry.category, 'Personal')
        self.assertEqual(entry.tags, ['test', 'example'])
        self.assertTrue(entry.has_notes)
        self.assertEqual(entry.username_hint, 'tes*****')
        self.assertEqual(entry.url_hint, 'example.com')
    
    def test_decrypt_password_entry(self) -> None:
        """Test decrypting password entry."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        # Test decryption methods
        password = entry.get_password()
        username = entry.get_username()
        
        self.assertEqual(password, 'Secret123!')
        self.assertEqual(username, 'testuser')
    
    def test_update_password_entry(self) -> None:
        """Test updating password entry."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        # Update data
        new_data = {
            'title': 'Updated Entry',
            'username': 'newuser',
            'password': 'NewSecret456!',
            'category': 'Work'
        }
        
        entry.update_from_data(new_data)
        
        # Verify updates
        self.assertEqual(entry.title, 'Updated Entry')
        self.assertEqual(entry.category, 'Work')
        self.assertEqual(entry.get_username(), 'newuser')
        self.assertEqual(entry.get_password(), 'NewSecret456!')
    
    def test_access_logging(self) -> None:
        """Test access logging."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        # Initially no access time
        self.assertIsNone(entry.last_accessed)
        
        # Access entry
        entry.access()
        
        # Should have access time
        self.assertIsNotNone(entry.last_accessed)


class PasswordCategoryTests(TestCase):
    """Test PasswordCategory model functionality."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!'
        )
    
    def test_create_category(self) -> None:
        """Test creating a password category."""
        category = PasswordCategory.objects.create(
            user=self.user,
            name='Personal',
            color='#28a745',
            icon='user'
        )
        
        self.assertEqual(category.user, self.user)
        self.assertEqual(category.name, 'Personal')
        self.assertEqual(category.color, '#28a745')
        self.assertEqual(category.icon, 'user')
    
    def test_get_default_categories(self) -> None:
        """Test getting default categories."""
        categories = PasswordCategory.get_default_categories(self.user)
        
        self.assertEqual(len(categories), 5)
        category_names = [cat.name for cat in categories]
        self.assertIn('Personal', category_names)
        self.assertIn('Work', category_names)
        self.assertIn('Finance', category_names)
        self.assertIn('Social', category_names)
        self.assertIn('Shopping', category_names)


class PasswordAPITests(APITestCase):
    """Test password API endpoints."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!'
        )
        # Set proper 32-byte encryption key for user
        self.user.encryption_key = 'test_key_32_bytes_long_123456789'  # 32 bytes
        self.user.save()
        
        # Force authentication
        self.client.force_authenticate(user=self.user)
    
    def test_create_password_entry_api(self) -> None:
        """Test creating password entry via API."""
        url = reverse('passwords:password_entries')
        data = {
            'title': 'Test Entry',
            'username': 'testuser',
            'password': 'Secret123!',
            'url': 'https://example.com',
            'notes': 'Test notes',
            'category': 'Personal',
            'tags': ['test', 'example']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PasswordEntry.objects.count(), 1)
        
        entry = PasswordEntry.objects.first()
        self.assertEqual(entry.title, 'Test Entry')
        self.assertEqual(entry.user, self.user)
    
    def test_list_password_entries_api(self) -> None:
        """Test listing password entries via API."""
        # Create test entries
        PasswordEntry.create_entry(
            user=self.user,
            title='Entry 1',
            username='user1',
            password='Pass1!'
        )
        PasswordEntry.create_entry(
            user=self.user,
            title='Entry 2',
            username='user2',
            password='Pass2!'
        )
        
        url = reverse('passwords:password_entries')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_password_entries_api(self) -> None:
        """Test searching password entries via API."""
        # Create test entries
        PasswordEntry.create_entry(
            user=self.user,
            title='GitHub',
            username='githubuser',
            password='Pass1!'
        )
        PasswordEntry.create_entry(
            user=self.user,
            title='Google',
            username='googleuser',
            password='Pass2!'
        )
        
        url = reverse('passwords:password_entries')
        response = self.client.get(url, {'search': 'GitHub'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'GitHub')
    
    def test_get_password_entry_detail_api(self) -> None:
        """Test getting password entry details via API."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        url = reverse('passwords:password_entry_detail', kwargs={'pk': entry.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('decrypted_password', response.data)
        self.assertEqual(response.data['decrypted_password'], 'Secret123!')
    
    def test_update_password_entry_api(self) -> None:
        """Test updating password entry via API."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        url = reverse('passwords:password_entry_detail', kwargs={'pk': entry.pk})
        data = {
            'title': 'Updated Entry',
            'username': 'newuser',
            'password': 'NewSecret456!'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertEqual(entry.title, 'Updated Entry')
        self.assertEqual(entry.get_username(), 'newuser')
        self.assertEqual(entry.get_password(), 'NewSecret456!')
    
    def test_delete_password_entry_api(self) -> None:
        """Test deleting password entry via API."""
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        url = reverse('passwords:password_entry_detail', kwargs={'pk': entry.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PasswordEntry.objects.count(), 0)
    
    def test_generate_password_api(self) -> None:
        """Test password generation API."""
        url = reverse('passwords:generate_password')
        response = self.client.get(url, {
            'length': 16,
            'use_symbols': True
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('password', response.data)
        self.assertIn('strength', response.data)
        self.assertEqual(len(response.data['password']), 16)
    
    def test_validate_password_api(self) -> None:
        """Test password validation API."""
        url = reverse('passwords:validate_password')
        
        # Strong password
        response = self.client.get(url, {'password': 'StrongP@ssw0rd123!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['score'], 4)
        
        # Weak password
        response = self.client.get(url, {'password': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response.data['score'], 3)
    
    def test_password_categories_api(self) -> None:
        """Test password categories API."""
        url = reverse('passwords:password_categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return default categories
        self.assertGreater(len(response.data), 0)
    
    def test_bulk_operations_api(self) -> None:
        """Test bulk operations API."""
        # Create test entries
        entry1 = PasswordEntry.create_entry(
            user=self.user,
            title='Entry 1',
            username='user1',
            password='Pass1!'
        )
        entry2 = PasswordEntry.create_entry(
            user=self.user,
            title='Entry 2',
            username='user2',
            password='Pass2!'
        )
        
        url = reverse('passwords:bulk_operations')
        
        # Test bulk delete
        data = {
            'entry_ids': [entry1.pk, entry2.pk],
            'operation': 'delete'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PasswordEntry.objects.count(), 0)
    
    def test_security_audit_api(self) -> None:
        """Test security audit API."""
        # Create some audit logs
        entry = PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        SecurityAudit.log_event(
            user=self.user,
            event_type='create',
            entry=entry,
            ip_address='127.0.0.1',
            details={'title': 'Test Entry'}
        )
        
        url = reverse('passwords:security_audit')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)


class PasswordImportExportTests(APITestCase):
    """Test password import/export functionality."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!'
        )
        # Set proper 32-byte encryption key for user
        self.user.encryption_key = 'test_key_32_bytes_long_123456789'  # 32 bytes
        self.user.save()
        
        # Force authentication
        self.client.force_authenticate(user=self.user)
    
    def test_export_csv_api(self) -> None:
        """Test CSV export API."""
        # Create test entry
        PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!',
            url='https://example.com',
            notes='Test notes'
        )
        
        url = reverse('passwords:export_passwords')
        response = self.client.get(url, {
            'format': 'csv',
            'include_passwords': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="passwords.csv"', response['Content-Disposition'])
    
    def test_export_json_api(self) -> None:
        """Test JSON export API."""
        # Create test entry
        PasswordEntry.create_entry(
            user=self.user,
            title='Test Entry',
            username='testuser',
            password='Secret123!'
        )
        
        url = reverse('passwords:export_passwords')
        response = self.client.get(url, {
            'format': 'json',
            'include_passwords': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment; filename="passwords.json"', response['Content-Disposition'])
    
    def test_import_csv_api(self) -> None:
        """Test CSV import API."""
        # Create CSV file
        csv_content = """title,username,password,url,notes,category
Test Entry,testuser,Secret123!,https://example.com,Test notes,Personal
Another Entry,anotheruser,Another456!,https://test.com,Another notes,Work"""
        
        csv_file = io.StringIO(csv_content)
        csv_file.name = 'test.csv'
        
        url = reverse('passwords:import_passwords')
        response = self.client.post(url, {
            'file': csv_file,
            'format': 'csv',
            'merge_strategy': 'skip'
        }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(PasswordEntry.objects.count(), 2)
    
    def test_import_json_api(self) -> None:
        """Test JSON import API."""
        # Create JSON file
        json_content = [
            {
                'title': 'Test Entry',
                'username': 'testuser',
                'password': 'Secret123!',
                'url': 'https://example.com',
                'notes': 'Test notes',
                'category': 'Personal'
            }
        ]
        
        json_file = io.StringIO(json.dumps(json_content))
        json_file.name = 'test.json'
        
        url = reverse('passwords:import_passwords')
        response = self.client.post(url, {
            'file': json_file,
            'format': 'json',
            'merge_strategy': 'skip'
        }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(PasswordEntry.objects.count(), 1)
