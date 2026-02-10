from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User, SecurityLog
from .serializers import UserSerializer, LoginSerializer
import pyotp
import secrets


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register(request):
    """Register new user with enhanced security."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Log registration
        SecurityLog.objects.create(
            user=user,
            event_type='login',  # Using login event type for registration
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description='User account created'
        )
        
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """Enhanced login with security monitoring."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        totp_code = serializer.validated_data.get('totp_code', '')
        
        try:
            user = User.objects.get(email=email)
            
            # Check if account is locked
            if user.is_account_locked():
                return Response({
                    'error': 'Account is temporarily locked due to failed login attempts'
                }, status=status.HTTP_423_LOCKED)
            
            # Authenticate user
            auth_user = authenticate(request, username=email, password=password)
            if not auth_user:
                # Increment failed attempts
                user.increment_failed_login()
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check 2FA if enabled
            if user.totp_enabled:
                if not totp_code:
                    return Response({
                        'error': '2FA code required',
                        'require_2fa': True
                    }, status=status.HTTP_202_ACCEPTED)
                
                if not user.verify_totp(totp_code):
                    user.increment_failed_login()
                    return Response({
                        'error': 'Invalid 2FA code'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Login user
            login(request, auth_user)
            
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'email': user.email,
                'totp_enabled': user.totp_enabled
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user and invalidate session."""
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable 2FA for user account."""
    user = request.user
    
    # Generate TOTP secret
    totp_secret = user.generate_totp_secret()
    user.save()
    
    # Get provisioning URI for QR code
    totp_uri = user.get_totp_uri()
    
    # Generate backup codes
    backup_codes = user.generate_backup_codes()
    
    # Log security event
    SecurityLog.objects.create(
        user=user,
        event_type='2fa_enabled',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        description='2FA enabled for user account'
    )
    
    return Response({
        'totp_secret': totp_secret,
        'totp_uri': totp_uri,
        'backup_codes': backup_codes
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa_setup(request):
    """Verify 2FA setup with test code."""
    totp_code = request.data.get('totp_code')
    
    if not totp_code:
        return Response({
            'error': 'TOTP code required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    if not user.totp_secret:
        return Response({
            'error': '2FA setup not initiated'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if user.verify_totp(totp_code):
        user.totp_enabled = True
        user.save()
        
        return Response({
            'message': '2FA enabled successfully'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid TOTP code'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Disable 2FA for user account."""
    password = request.data.get('password')
    
    if not password:
        return Response({
            'error': 'Password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Verify password
    if not user.check_password(password):
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Disable 2FA
    user.totp_enabled = False
    user.totp_secret = None
    user.backup_codes = []
    user.save()
    
    # Log security event
    SecurityLog.objects.create(
        user=user,
        event_type='2fa_disabled',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        description='2FA disabled for user account'
    )
    
    return Response({
        'message': '2FA disabled successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_status(request):
    """Get user security status."""
    user = request.user
    
    return Response({
        'totp_enabled': user.totp_enabled,
        'backup_codes_count': len(user.backup_codes),
        'last_password_change': user.last_password_change,
        'failed_login_attempts': user.failed_login_attempts,
        'is_locked': user.is_account_locked(),
        'locked_until': user.locked_until
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_logs(request):
    """Get user security logs."""
    logs = SecurityLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'event_type': log.event_type,
            'description': log.description,
            'ip_address': log.ip_address,
            'timestamp': log.timestamp
        })
    
    return Response({
        'logs': logs_data
    }, status=status.HTTP_200_OK)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip
