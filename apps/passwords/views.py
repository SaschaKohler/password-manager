from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.http import JsonResponse
import csv
import json
import io
from typing import Dict, Any, List, Optional

from .models import PasswordEntry, PasswordCategory, PasswordShare, SecurityAudit
from .serializers import (
    PasswordEntrySerializer, PasswordEntryDetailSerializer,
    PasswordCategorySerializer, PasswordShareSerializer,
    PasswordGeneratorSerializer, PasswordImportSerializer,
    PasswordExportSerializer, SecurityAuditSerializer,
    BulkPasswordOperationSerializer
)
from core.crypto.encryption import PasswordGenerator, validate_password_strength
from core.crypto.exceptions import EncryptionError, DecryptionError


class PasswordPagination(PageNumberPagination):
    """Custom pagination for password entries."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def password_entries(request: Request) -> Response:
    """List or create password entries."""
    user = request.user
    
    if request.method == 'GET':
        # Filter and search
        queryset = PasswordEntry.objects.filter(user=user)
        
        # Search
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(username_hint__icontains=search) |
                Q(url_hint__icontains=search) |
                Q(tags__contains=[search])
            )
        
        # Category filter
        category = request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # Favorites filter
        favorites_only = request.GET.get('favorites', 'false').lower() == 'true'
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        
        # Sort
        sort_by = request.GET.get('sort', 'title')
        sort_order = request.GET.get('order', 'asc')
        if sort_by in ['title', 'created_at', 'updated_at', 'last_accessed']:
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'
            queryset = queryset.order_by(sort_by)
        
        # Paginate
        paginator = PasswordPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = PasswordEntrySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PasswordEntrySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            entry = serializer.save()
            
            # Log creation
            SecurityAudit.log_event(
                user=user,
                event_type='create',
                entry=entry,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'title': entry.title}
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def password_entry_detail(request: Request, pk: int) -> Response:
    """Retrieve, update or delete a password entry."""
    user = request.user
    entry = get_object_or_404(PasswordEntry, pk=pk, user=user)
    
    if request.method == 'GET':
        serializer = PasswordEntryDetailSerializer(entry)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PasswordEntrySerializer(
            entry, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            entry = serializer.save()
            
            # Log update
            SecurityAudit.log_event(
                user=user,
                event_type='edit',
                entry=entry,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'title': entry.title}
            )
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        title = entry.title
        entry.delete()
        
        # Log deletion
        SecurityAudit.log_event(
            user=user,
            event_type='delete',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'title': title}
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def password_categories(request: Request) -> Response:
    """List password categories."""
    user = request.user
    
    # Get default categories if none exist
    if not user.password_categories.exists():
        PasswordCategory.get_default_categories(user)
    
    categories = PasswordCategory.objects.filter(user=user)
    serializer = PasswordCategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request: Request) -> Response:
    """Create a new password category."""
    user = request.user
    serializer = PasswordCategorySerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_password(request: Request) -> Response:
    """Generate a secure password."""
    serializer = PasswordGeneratorSerializer(data=request.GET)
    
    if serializer.is_valid():
        password, strength = serializer.generate_password()
        return Response({
            'password': password,
            'strength': strength
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_password(request: Request) -> Response:
    """Validate password strength."""
    password = request.GET.get('password', '')
    
    if not password:
        return Response({'error': 'Password parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    validation = validate_password_strength(password)
    return Response(validation)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_password(request: Request, pk: int) -> Response:
    """Share a password entry with another user."""
    user = request.user
    entry = get_object_or_404(PasswordEntry, pk=pk, user=user)
    
    serializer = PasswordShareSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        share = serializer.save(entry=entry, shared_by=user)
        
        # Log sharing
        SecurityAudit.log_event(
            user=user,
            event_type='share',
            entry=entry,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={
                'shared_with': share.shared_with.email,
                'share_type': share.share_type
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shared_with_me(request: Request) -> Response:
    """List passwords shared with the current user."""
    user = request.user
    
    shares = PasswordShare.objects.filter(
        shared_with=user,
        is_active=True
    ).select_related('entry', 'shared_by')
    
    # Filter out expired shares
    valid_shares = [share for share in shares if share.is_valid()]
    
    serializer = PasswordShareSerializer(valid_shares, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shared_by_me(request: Request) -> Response:
    """List passwords shared by the current user."""
    user = request.user
    
    shares = PasswordShare.objects.filter(
        shared_by=user
    ).select_related('entry', 'shared_with')
    
    serializer = PasswordShareSerializer(shares, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_operations(request: Request) -> Response:
    """Perform bulk operations on password entries."""
    user = request.user
    serializer = BulkPasswordOperationSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    entry_ids = serializer.validated_data['entry_ids']
    operation = serializer.validated_data['operation']
    entries = PasswordEntry.objects.filter(user=user, id__in=entry_ids)
    
    if operation == 'delete':
        titles = [entry.title for entry in entries]
        entries.delete()
        
        # Log bulk deletion
        for title in titles:
            SecurityAudit.log_event(
                user=user,
                event_type='delete',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'title': title}
            )
        
        return Response({'message': f'Deleted {len(titles)} entries'})
    
    elif operation == 'move':
        category = serializer.validated_data['category']
        entries.update(category=category)
        return Response({'message': f'Moved {len(entry_ids)} entries to {category}'})
    
    elif operation == 'tag':
        tags = serializer.validated_data['tags']
        for entry in entries:
            current_tags = entry.tags
            entry.tags = list(set(current_tags + tags))
            entry.save()
        return Response({'message': f'Added tags to {len(entry_ids)} entries'})
    
    elif operation == 'share':
        # This would require more complex implementation
        return Response({'error': 'Bulk sharing not implemented yet'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    return Response({'error': 'Unknown operation'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_audit(request: Request) -> Response:
    """Get security audit logs for the user."""
    user = request.user
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    audits = SecurityAudit.objects.filter(user=user)
    
    if date_from:
        audits = audits.filter(timestamp__gte=date_from)
    if date_to:
        audits = audits.filter(timestamp__lte=date_to)
    
    # Filter by event type
    event_type = request.GET.get('event_type')
    if event_type:
        audits = audits.filter(event_type=event_type)
    
    # Order by timestamp (most recent first)
    audits = audits.order_by('-timestamp')
    
    # Paginate
    paginator = PasswordPagination()
    page = paginator.paginate_queryset(audits, request)
    
    serializer = SecurityAuditSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_passwords(request: Request) -> Response:
    """Import passwords from file."""
    user = request.user
    serializer = PasswordImportSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    file = serializer.validated_data['file']
    import_format = serializer.validated_data['format']
    merge_strategy = serializer.validated_data['merge_strategy']
    
    try:
        if import_format == 'csv':
            imported_count = _import_csv(file, user, merge_strategy)
        elif import_format == 'json':
            imported_count = _import_json(file, user, merge_strategy)
        else:
            return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log import
        SecurityAudit.log_event(
            user=user,
            event_type='import',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'format': import_format, 'count': imported_count}
        )
        
        return Response({
            'message': f'Successfully imported {imported_count} passwords',
            'count': imported_count
        })
        
    except Exception as e:
        return Response({'error': f'Import failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_passwords(request: Request) -> Response:
    """Export passwords to file."""
    user = request.user
    serializer = PasswordExportSerializer(data=request.GET)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    export_format = serializer.validated_data['format']
    include_passwords = serializer.validated_data['include_passwords']
    categories = serializer.validated_data.get('categories', [])
    date_from = serializer.validated_data.get('date_from')
    date_to = serializer.validated_data.get('date_to')
    
    # Filter entries
    entries = PasswordEntry.objects.filter(user=user)
    
    if categories:
        entries = entries.filter(category__in=categories)
    if date_from:
        entries = entries.filter(created_at__gte=date_from)
    if date_to:
        entries = entries.filter(created_at__lte=date_to)
    
    try:
        if export_format == 'csv':
            response = _export_csv(entries, include_passwords)
        elif export_format == 'json':
            response = _export_json(entries, include_passwords)
        else:
            return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log export
        SecurityAudit.log_event(
            user=user,
            event_type='export',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'format': export_format, 'count': entries.count()}
        )
        
        return response
        
    except Exception as e:
        return Response({'error': f'Export failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


def _import_csv(file, user, merge_strategy: str) -> int:
    """Import passwords from CSV file."""
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    imported_count = 0
    
    for row in reader:
        try:
            # Check if entry already exists
            existing = PasswordEntry.objects.filter(
                user=user, title=row.get('title', '')
            ).first()
            
            if existing and merge_strategy == 'skip':
                continue
            
            password_data = {
                'title': row.get('title', ''),
                'username': row.get('username', ''),
                'password': row.get('password', ''),
                'url': row.get('url', ''),
                'notes': row.get('notes', ''),
                'category': row.get('category', ''),
                'tags': row.get('tags', '').split(',') if row.get('tags') else []
            }
            
            if existing and merge_strategy == 'overwrite':
                existing.update_from_data(password_data)
            else:
                PasswordEntry.create_entry(user, **password_data)
            
            imported_count += 1
            
        except Exception:
            # Skip invalid rows
            continue
    
    return imported_count


def _import_json(file, user, merge_strategy: str) -> int:
    """Import passwords from JSON file."""
    data = json.loads(file.read().decode('utf-8'))
    
    if not isinstance(data, list):
        data = [data]
    
    imported_count = 0
    
    for item in data:
        try:
            # Check if entry already exists
            existing = PasswordEntry.objects.filter(
                user=user, title=item.get('title', '')
            ).first()
            
            if existing and merge_strategy == 'skip':
                continue
            
            password_data = {
                'title': item.get('title', ''),
                'username': item.get('username', ''),
                'password': item.get('password', ''),
                'url': item.get('url', ''),
                'notes': item.get('notes', ''),
                'category': item.get('category', ''),
                'tags': item.get('tags', [])
            }
            
            if existing and merge_strategy == 'overwrite':
                existing.update_from_data(password_data)
            else:
                PasswordEntry.create_entry(user, **password_data)
            
            imported_count += 1
            
        except Exception:
            # Skip invalid items
            continue
    
    return imported_count


def _export_csv(entries, include_passwords: bool) -> Response:
    """Export passwords to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    headers = ['title', 'username', 'url', 'notes', 'category', 'tags', 'created_at']
    if include_passwords:
        headers.insert(2, 'password')
    writer.writerow(headers)
    
    # Data rows
    for entry in entries:
        try:
            data = entry.decrypt_data()
            row = [
                data.get('title', ''),
                data.get('username', ''),
                data.get('url', ''),
                data.get('notes', ''),
                entry.category,
                ','.join(entry.tags),
                entry.created_at.isoformat()
            ]
            
            if include_passwords:
                row.insert(2, data.get('password', ''))
            
            writer.writerow(row)
            
        except Exception:
            # Skip entries that can't be decrypted
            continue
    
    response = Response(output.getvalue())
    response['Content-Type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename="passwords.csv"'
    return response


def _export_json(entries, include_passwords: bool) -> Response:
    """Export passwords to JSON format."""
    export_data = []
    
    for entry in entries:
        try:
            data = entry.decrypt_data()
            entry_data = {
                'title': data.get('title', ''),
                'username': data.get('username', ''),
                'url': data.get('url', ''),
                'notes': data.get('notes', ''),
                'category': entry.category,
                'tags': entry.tags,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat()
            }
            
            if include_passwords:
                entry_data['password'] = data.get('password', '')
            
            export_data.append(entry_data)
            
        except Exception:
            # Skip entries that can't be decrypted
            continue
    
    response = Response(json.dumps(export_data, indent=2))
    response['Content-Type'] = 'application/json'
    response['Content-Disposition'] = 'attachment; filename="passwords.json"'
    return response


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip or '0.0.0.0'
