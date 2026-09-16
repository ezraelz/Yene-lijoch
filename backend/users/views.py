from django.shortcuts import render,redirect,get_object_or_404
from .serializers import UserSerializer,UserProfileUpdateSerializer,CustomTokenObtainPairSerializer,UserCreateSerializer
from rest_framework import viewsets,status
from .models import Profile
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from roles.models import Role
from django.contrib.auth import update_session_auth_hash
from .models import PasswordHistory
from .serializers import EnhancedChangePasswordSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache
import json
import logging
from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
)

def scoped_profiles(user):
    """
    Superusers   → all profiles.
    Org admins   → only profiles whose organization is their org.
    Others       → only themselves.
    """
    qs = Profile.objects.select_related("role", "organization")

    if is_superuser(user):
        return qs

    if is_admin(user):
        org = get_user_organization(user)
        if not org:
            return qs.none()
        # Profile.organization is a FK to OrganizationMembership.
        return qs.filter(organization__organization=org)

    # Regular users see only themselves.
    return qs.filter(pk=user.pk)

# ======================================================================
# User list (admin) — scoped
# ======================================================================

class userView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Admin access required.")

        users = scoped_profiles(request.user)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ======================================================================
# User create (open registration or admin-driven)
# ======================================================================

class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# ======================================================================
# Deactivated users (scoped)
# ======================================================================

class DeactivatedUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Admin access required.")

        qs = scoped_profiles(request.user).filter(is_active=False)
        return Response(UserSerializer(qs, many=True).data)
    
# ======================================================================
# Reactivate
# ======================================================================

class ReactivateUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Admin access required.")

        # Scope the lookup so admins can't reactivate users outside their org.
        profile = get_object_or_404(scoped_profiles(request.user), pk=pk)
        profile.is_active = True
        profile.save(update_fields=["is_active"])
        return Response(UserSerializer(profile).data, status=status.HTTP_200_OK)
    
# ======================================================================
# JWT login
# ======================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    
# ======================================================================
# Current user's own profile
# ======================================================================

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user IS the Profile (AUTH_USER_MODEL = users.Profile).
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)
    
# ======================================================================
# Staff list (scoped)
# ======================================================================

class StaffView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = scoped_profiles(request.user).exclude(
            role__role_name__in=["student", "parent"]
        )
        return Response(UserSerializer(qs, many=True).data, status=status.HTTP_200_OK)
    

# ======================================================================
# Profile detail — scoped + permission-checked
# ======================================================================

class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, request, pk):
        return get_object_or_404(scoped_profiles(request.user), pk=pk)

    def get(self, request, pk):
        profile = self._get_object(request, pk)
        return Response(
            UserSerializer(profile, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Admin access required.")
        profile = self._get_object(request, pk)
        serializer = UserProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                UserSerializer(profile, context={"request": request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not is_superuser(request.user):
            raise PermissionDenied("Only superusers can delete profiles.")
        self._get_object(request, pk).is_active = False
        self._get_object(request, pk).save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# ======================================================================
# Login (session + JWT)
# ======================================================================

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile_image = None
        if getattr(user, "profile_image", None):
            profile_image = request.build_absolute_uri(user.profile_image.url)

        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_superuser": user.is_superuser,
            "id": user.id,
            "username": user.username,
            "profile_image": profile_image,
        })
    

# ======================================================================
# Change password (unchanged except cleanup)
# ======================================================================

class EnhancedChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EnhancedChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if not user.check_password(serializer.validated_data["current_password"]):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = serializer.validated_data["new_password"]

        if self.is_password_in_history(user, new_password):
            return Response(
                {"error": "You cannot reuse a recently used password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        self.save_password_history(user, new_password)
        update_session_auth_hash(request, user)
        self.log_password_change(user, request)

        return Response(
            {
                "message": "Password changed successfully.",
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_200_OK,
        )

    def is_password_in_history(self, user, new_password):
        six_months_ago = timezone.now() - timedelta(days=180)
        recent = PasswordHistory.objects.filter(
            user=user, created_at__gte=six_months_ago
        )
        return any(p.check_password(new_password) for p in recent)

    def save_password_history(self, user, password):
        PasswordHistory.objects.create(user=user, password=password)
        keep = PasswordHistory.objects.filter(user=user).order_by("-created_at")[:10]
        PasswordHistory.objects.filter(user=user).exclude(
            id__in=keep.values_list("id", flat=True)
        ).delete()

    def log_password_change(self, user, request):
        logger = logging.getLogger("security")
        logger.info(
            f"Password changed for user: {user.username}",
            extra={"user_id": user.id, "ip_address": self.get_client_ip(request)},
        )

    def get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR")
    
# ======================================================================
# Logout — JSON response, with refresh token blacklist
# ======================================================================

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Optionally blacklist the refresh token if the client sends it.
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                # Token already expired or blacklisted — ignore.
                pass

        logout(request)
        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )
    

# ======================================================================
# Password reset flow — unchanged except minor polish
# ======================================================================

class SendResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = Profile.objects.get(email=email)
        except Profile.DoesNotExist:
            return Response(
                {"message": "If the email exists, a reset code has been sent."},
                status=status.HTTP_200_OK,
            )

        reset_code = get_random_string(6, "0123456789")
        reset_data = {
            "user_id": user.id,
            "code": reset_code,
            "created_at": timezone.now().isoformat(),
            "attempts": 0,
        }
        cache.set(f"password_reset:{email}", reset_data, 600)

        try:
            self.send_reset_email(email, reset_code, user.first_name or user.username)
            if settings.DEBUG:
                print(f"🔐 Password reset code for {email}: {reset_code}")
            return Response(
                {"message": "Reset code sent to your email."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
            return Response(
                {"error": "Failed to send reset code. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    def send_reset_email(self, email, code, username):
        subject = 'Password Reset Code'
        
        message = f"""
        Hello {username},
        
        You requested a password reset for your account.
        
        Your reset code is: {code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Developers Team
        """
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #667eea; text-align: center; letter-spacing: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1></h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello {username},</h2>
                    <p>You requested a password reset for your account.</p>
                    
                    <div class="code">{code}</div>
                    
                    <p><strong>This code will expire in 10 minutes.</strong></p>
                    
                    <p>If you didn't request this reset, please ignore this email. Your account remains secure.</p>
                    
                    <p>Best regards</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Developers Team. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # For development, use console backend
        if settings.DEBUG:
            print(f"📧 Email would be sent to {email}")
            print(f"📝 Code: {code}")
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        code = request.data.get('code', '').strip()
        
        if not email or not code:
            return Response(
                {'error': 'Email and code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f"password_reset:{email}"
        reset_data = cache.get(cache_key)
        
        if not reset_data:
            return Response(
                {'error': 'Reset code has expired or is invalid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if code matches
            if reset_data['code'] != code:
                # Increment attempts
                reset_data['attempts'] += 1
                cache.set(cache_key, reset_data, 600)  # Reset timer
                
                # Check if too many attempts
                if reset_data['attempts'] >= 5:
                    cache.delete(cache_key)
                    return Response(
                        {'error': 'Too many failed attempts. Please request a new code.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response(
                    {'error': 'Invalid reset code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Code is valid - mark as verified
            reset_data['verified'] = True
            cache.set(cache_key, reset_data, 1800)  # Extend to 30 minutes
            
            return Response(
                {'message': 'Code verified successfully.'},
                status=status.HTTP_200_OK
            )
            
        except (KeyError) as e:
            print(f"Error parsing reset data: {str(e)}")
            return Response(
                {'error': 'Invalid reset data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password', '')
        
        if not email or not code or not new_password:
            return Response(
                {'error': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password strength
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f"password_reset:{email}"
        reset_data = cache.get(cache_key)
        
        if not reset_data:
            return Response(
                {'error': 'Reset session has expired. Please start over.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify code and check if it's marked as verified
            if reset_data.get('code') != code or not reset_data.get('verified'):
                return Response(
                    {'error': 'Invalid or unverified reset code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user and update password
            try:
                user = Profile.objects.get(id=reset_data['user_id'])
                user.set_password(new_password)
                user.save()
                
                # Clear the reset data
                cache.delete(cache_key)
                
                # Send confirmation email
                self.send_confirmation_email(email, user.first_name or user.username)
                
                return Response(
                    {'message': 'Password reset successfully.'},
                    status=status.HTTP_200_OK
                )
                
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'User not found.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except (KeyError) as e:
            print(f"Error parsing reset data: {str(e)}")
            return Response(
                {'error': 'Invalid reset data.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def send_confirmation_email(self, email, username):
        subject = 'Password Reset Successful'
        
        message = f"""
        Hello {username},
        
        Your password has been successfully reset.
        
        If you didn't make this change, please contact support immediately.
        
        Best regards,
        Developers Team
        """
        
        if settings.DEBUG:
            print(f"📧 Password reset confirmation for {username}")
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

        