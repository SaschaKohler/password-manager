from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PasswordEntry, PasswordCategory, PasswordShare, SecurityAudit
from core.crypto.encryption import PasswordGenerator, validate_password_strength
from typing import Dict, Any, List, Optional

User = get_user_model()


class PasswordEntrySerializer(serializers.ModelSerializer):
    """Serializer for password entries."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)
    url = serializers.URLField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    is_favorite = serializers.BooleanField(default=False)
    
    # Read-only fields from encrypted data
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    last_accessed = serializers.DateTimeField(read_only=True)
    username_hint = serializers.CharField(read_only=True)
    url_hint = serializers.CharField(read_only=True)
    has_notes = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PasswordEntry
        fields = [
            'id', 'title', 'password', 'username', 'url', 'notes',
            'category', 'tags', 'is_favorite', 'created_at', 'updated_at',
            'last_accessed', 'username_hint', 'url_hint', 'has_notes'
        ]
    
    def validate_password(self, value: str) -> str:
        """Validate password strength."""
        validation = validate_password_strength(value)
        if validation['score'] < 3:
            raise serializers.ValidationError(
                f"Password is too weak: {', '.join(validation['feedback'])}"
            )
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> PasswordEntry:
        """Create encrypted password entry."""
        user = self.context['request'].user
        
        return PasswordEntry.create_entry(
            user=user,
            title=validated_data['title'],
            username=validated_data.get('username', ''),
            password=validated_data['password'],
            url=validated_data.get('url'),
            notes=validated_data.get('notes'),
            category=validated_data.get('category', ''),
            tags=validated_data.get('tags', []),
            is_favorite=validated_data.get('is_favorite', False)
        )
    
    def update(self, instance: PasswordEntry, validated_data: Dict[str, Any]) -> PasswordEntry:
        """Update encrypted password entry."""
        # Get current encrypted data
        current_data = instance.decrypt_data()
        
        # Update with new data
        for field in ['username', 'url', 'notes', 'category', 'tags', 'is_favorite']:
            if field in validated_data:
                current_data[field] = validated_data[field]
        
        if 'password' in validated_data:
            current_data['password'] = validated_data['password']
        
        if 'title' in validated_data:
            current_data['title'] = validated_data['title']
        
        instance.update_from_data(current_data)
        return instance


class PasswordEntryDetailSerializer(PasswordEntrySerializer):
    """Detailed serializer including decrypted data for viewing."""
    
    decrypted_password = serializers.CharField(read_only=True)
    decrypted_username = serializers.CharField(read_only=True)
    decrypted_url = serializers.CharField(read_only=True, allow_blank=True)
    decrypted_notes = serializers.CharField(read_only=True, allow_blank=True)
    
    class Meta(PasswordEntrySerializer.Meta):
        fields = PasswordEntrySerializer.Meta.fields + [
            'decrypted_password', 'decrypted_username', 'decrypted_url', 'decrypted_notes'
        ]
    
    def to_representation(self, instance: PasswordEntry) -> Dict[str, Any]:
        """Add decrypted fields to representation."""
        data = super().to_representation(instance)
        
        # Add decrypted fields
        try:
            data['decrypted_password'] = instance.get_password()
            data['decrypted_username'] = instance.get_username()
            data['decrypted_url'] = instance.get_url() or ''
            data['decrypted_notes'] = instance.get_notes() or ''
            
            # Log access
            instance.access()
            
        except Exception:
            # If decryption fails, don't expose error
            data['decrypted_password'] = '***'
            data['decrypted_username'] = '***'
            data['decrypted_url'] = '***'
            data['decrypted_notes'] = '***'
        
        return data


class PasswordCategorySerializer(serializers.ModelSerializer):
    """Serializer for password categories."""
    
    entry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordCategory
        fields = ['id', 'name', 'color', 'icon', 'created_at', 'entry_count']
    
    def get_entry_count(self, obj: PasswordCategory) -> int:
        """Get number of entries in this category."""
        return obj.user.password_entries.filter(category=obj.name).count()


class PasswordShareSerializer(serializers.ModelSerializer):
    """Serializer for password sharing."""
    
    entry_title = serializers.CharField(source='entry.title', read_only=True)
    shared_by_email = serializers.CharField(source='shared_by.email', read_only=True)
    shared_with_email = serializers.CharField(source='shared_with.email', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PasswordShare
        fields = [
            'id', 'entry', 'entry_title', 'shared_by', 'shared_by_email',
            'shared_with', 'shared_with_email', 'share_type', 'message',
            'created_at', 'expires_at', 'is_active', 'is_expired', 'is_valid'
        ]
        read_only_fields = ['shared_by', 'created_at']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate share data."""
        # Check if user is trying to share with themselves
        if 'shared_with' in attrs:
            shared_with = attrs['shared_with']
            request_user = self.context['request'].user
            
            if shared_with == request_user:
                raise serializers.ValidationError("You cannot share entries with yourself")
        
        # Validate expiration date
        if 'expires_at' in attrs and attrs['expires_at']:
            if attrs['expires_at'] <= timezone.now():
                raise serializers.ValidationError("Expiration date must be in the future")
        
        return attrs


class PasswordGeneratorSerializer(serializers.Serializer):
    """Serializer for password generation."""
    
    length = serializers.IntegerField(min_value=8, max_value=128, default=16)
    use_symbols = serializers.BooleanField(default=True)
    use_lowercase = serializers.BooleanField(default=True)
    use_uppercase = serializers.BooleanField(default=True)
    use_digits = serializers.BooleanField(default=True)
    
    password = serializers.CharField(read_only=True)
    strength = serializers.DictField(read_only=True)
    
    def generate_password(self) -> tuple[str, Dict[str, Any]]:
        """Generate password and validate strength."""
        password = PasswordGenerator.generate(
            length=self.validated_data['length'],
            use_symbols=self.validated_data['use_symbols'],
            use_lowercase=self.validated_data['use_lowercase'],
            use_uppercase=self.validated_data['use_uppercase'],
            use_digits=self.validated_data['use_digits']
        )
        
        strength = validate_password_strength(password)
        return password, strength
    
    def to_representation(self, instance: Any) -> Dict[str, Any]:
        """Generate password and return with strength info."""
        password, strength = self.generate_password()
        return {
            'password': password,
            'strength': strength
        }


class PasswordImportSerializer(serializers.Serializer):
    """Serializer for importing passwords from other managers."""
    
    file = serializers.FileField()
    format = serializers.ChoiceField(choices=['csv', 'json', '1password'])
    merge_strategy = serializers.ChoiceField(
        choices=['skip', 'overwrite', 'merge'],
        default='skip'
    )
    
    def validate_file(self, value) -> Any:
        """Validate uploaded file."""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Check file extension
        allowed_extensions = ['.csv', '.json']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError("Only CSV and JSON files are allowed")
        
        return value


class PasswordExportSerializer(serializers.Serializer):
    """Serializer for exporting passwords."""
    
    format = serializers.ChoiceField(choices=['csv', 'json'])
    include_passwords = serializers.BooleanField(default=True)
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)


class SecurityAuditSerializer(serializers.ModelSerializer):
    """Serializer for security audit logs."""
    
    entry_title = serializers.CharField(source='entry.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = SecurityAudit
        fields = [
            'id', 'event_type', 'entry', 'entry_title', 'user', 'user_email',
            'ip_address', 'user_agent', 'details', 'timestamp'
        ]


class BulkPasswordOperationSerializer(serializers.Serializer):
    """Serializer for bulk operations on passwords."""
    
    entry_ids = serializers.ListField(child=serializers.IntegerField())
    operation = serializers.ChoiceField(choices=['delete', 'move', 'tag', 'share'])
    
    # Operation-specific fields
    category = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    share_with = serializers.EmailField(required=False)
    share_type = serializers.ChoiceField(
        choices=['view', 'edit', 'admin'],
        required=False
    )
    
    def validate_entry_ids(self, value: List[int]) -> List[int]:
        """Validate entry IDs belong to user."""
        user = self.context['request'].user
        user_entry_ids = user.password_entries.filter(id__in=value).values_list('id', flat=True)
        
        if len(user_entry_ids) != len(value):
            raise serializers.ValidationError("Some entries don't exist or don't belong to you")
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation-specific requirements."""
        operation = attrs.get('operation')
        
        if operation == 'move' and 'category' not in attrs:
            raise serializers.ValidationError("Category is required for move operation")
        
        if operation == 'tag' and 'tags' not in attrs:
            raise serializers.ValidationError("Tags are required for tag operation")
        
        if operation == 'share':
            if 'share_with' not in attrs:
                raise serializers.ValidationError("Share recipient is required")
            if 'share_type' not in attrs:
                raise serializers.ValidationError("Share type is required")
        
        return attrs
