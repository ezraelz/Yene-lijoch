from django.shortcuts import render,redirect
from .serializers import UserSerializer,UserProfileUpdateSerializer,CustomTokenObtainPairSerializer
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

class userView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = Profile.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_profile = request.user
        serializer = UserSerializer(user_profile, context={"request": request})
        return Response(serializer.data)
    
class StaffView(APIView):
    def get(self, request):
        try:
            # Get all profiles except students and parents
            staff = Profile.objects.exclude(role__role_name__in=["student", "parent"])
        except Exception as e:
            return Response(
                {"error": "Something went wrong! Please try again."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserSerializer(staff, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileDetailView(APIView):
    def get(self, request, pk):
        profile = Profile.objects.get(id=pk)

        serializer = UserSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        profile = Profile.objects.get(id=pk)

        serializer = UserSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            profile = Profile.objects.get(id=pk)
            profile.delete()
            return Response(status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView): 
    permission_classes = [AllowAny]

    def post(self, request): 
        username = request.data.get('username') 
        password = request.data.get('password') 
        user = authenticate(username=username, password=password) 
        profile_image = None
        if hasattr(user, "profile_image") and user.profile_image:
            profile_image = request.build_absolute_uri(user.profile_image)

        if user is not None: 
            login(request, user) 
            refresh = RefreshToken.for_user(user) 
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role.role_name,  # assuming you have a related role model
                "is_superuser": user.is_superuser,
                "id": user.id,
                "username": user.username,
                "profile_image": profile_image,
        })
        else: return Response({'error': 'Invalid credentials'}, status=400)

class EnhancedChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EnhancedChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            
            # Check current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {'error': 'Current password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_password = serializer.validated_data['new_password']
            
            # Check password history (prevent reusing recent passwords)
            if self.is_password_in_history(user, new_password):
                return Response(
                    {'error': 'You cannot reuse a recently used password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Save to password history
            self.save_password_history(user, new_password)
            
            # Update session auth hash to keep user logged in
            update_session_auth_hash(request, user)
            
            # Log the password change (optional)
            self.log_password_change(user, request)
            
            return Response(
                {
                    'message': 'Password changed successfully.',
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def is_password_in_history(self, user, new_password):
        """
        Check if the new password was used in the last 6 months
        """
        six_months_ago = timezone.now() - timedelta(days=180)
        
        recent_passwords = PasswordHistory.objects.filter(
            user=user,
            created_at__gte=six_months_ago
        )
        
        for password_history in recent_passwords:
            if password_history.check_password(new_password):
                return True
        
        return False
    
    def save_password_history(self, user, password):
        """
        Save the new password to history
        """
        PasswordHistory.objects.create(user=user, password=password)
        
        # Keep only last 10 passwords
        passwords_to_keep = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        PasswordHistory.objects.filter(user=user).exclude(
            id__in=passwords_to_keep.values_list('id', flat=True)
        ).delete()
    
    def log_password_change(self, user, request):
        """
        Log password change activity
        """
        # You can integrate with your logging system here
        print(f"Password changed for user: {user.username} at {timezone.now()}")
        # Or use Django's logging
        import logging
        logger = logging.getLogger('security')
        logger.info(f"Password changed for user: {user.username}", extra={
            'user_id': user.id,
            'ip_address': self.get_client_ip(request)
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LogoutView(APIView):   
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('login')

class SendResetCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if user exists
            user = Profile.objects.get(email=email)
        except Profile.DoesNotExist:
            # For security, don't reveal if email exists or not
            return Response(
                {'message': 'If the email exists, a reset code has been sent.'},
                status=status.HTTP_200_OK
            )
        
        # Generate 6-digit code
        reset_code = get_random_string(6, '0123456789')
        
        # Store code in Django cache with expiration (10 minutes)
        reset_data = {
            'user_id': user.id,
            'code': reset_code,
            'created_at': timezone.now().isoformat(),
            'attempts': 0  # Track verification attempts
        }
        
        cache_key = f"password_reset:{email}"
        cache.set(cache_key, reset_data, 600)  # 10 minutes
        
        # Send email
        try:
            self.send_reset_email(email, reset_code, user.first_name or user.username)
            
            # For development, print code to console
            print(f"🔐 Password reset code for {email}: {reset_code}")
            
            return Response(
                {'message': 'Reset code sent to your email.'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return Response(
                {'error': 'Failed to send reset code. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

        