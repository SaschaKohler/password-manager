from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User
import secrets
import hashlib
import os


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration and profile."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    master_password = serializers.CharField(write_only=True, min_length=12)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'password_confirm', 'master_password',
            'totp_enabled', 'password_generator_length', 'password_generator_symbols'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'totp_enabled': {'read_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        master_password = validated_data.pop('master_password')
        
        # Generate salt and hash master password
        salt = os.urandom(16).hex()
        master_password_hash = hashlib.pbkdf2_hmac('sha256', 
                                           master_password.encode('utf-8'), 
                                           salt.encode('utf-8'), 
                                           100000).hex()
        
        # Generate encryption key (in production, this should be derived from master password)
        encryption_key = secrets.token_urlsafe(48)
        
        user = User.objects.create_user(
            password=password,
            master_password_hash=master_password_hash,
            master_password_salt=salt,
            encryption_key=encryption_key,
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    totp_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                             username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates."""
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'totp_enabled', 
            'password_generator_length', 'password_generator_symbols',
            'last_password_change', 'failed_login_attempts'
        ]
        read_only_fields = ['email', 'totp_enabled', 'last_password_change', 'failed_login_attempts']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password changes."""
    
    current_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value


class TOTPSetupSerializer(serializers.Serializer):
    """Serializer for TOTP setup verification."""
    
    totp_code = serializers.CharField(max_length=6)
    
    def validate_totp_code(self, value):
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("TOTP code must be 6 digits")
        return value


class BackupCodeSerializer(serializers.Serializer):
    """Serializer for backup code usage."""
    
    backup_code = serializers.CharField(max_length=8)
    
    def validate_backup_code(self, value):
        if len(value) != 8:
            raise serializers.ValidationError("Invalid backup code format")
        return value
