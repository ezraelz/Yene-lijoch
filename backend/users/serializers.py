from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from roles.models import Role
import re

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.role_name", read_only=True)

    class Meta:
        model = Profile
        fields = ["id",'sex', 'age', "first_name",
                  "last_name","username", 'date_of_birth',
                  "role", "role_name", "email", 'contact',
                  "is_active", "is_staff", "is_superuser",
                  'profile_image', 'address', 'created_at',
                  'last_seen', 'bio', 'deactivated_at', 
                  'deactivation_reason', 'is_agreed_to_terms']
        read_only_fields = ["id", "is_staff",
                            "is_superuser",'created_at',
                            'last_seen', 'is_agreed_to_terms']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "username",
            "role", 
            "email",
            'password', 
            'is_agreed_to_terms',
        ]

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = Profile(**validated_data)
        user.set_password(password)
        user.save()

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer): 
    username_field = 'username' 
    
    def validate(self, attrs): 
        data = super().validate(attrs) 
        data['role'] = self.user.role.role_name if self.user.role else None  # Avoid errors if role is null
        return data

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['sex', 'age', "first_name",
                  "last_name","username", 'date_of_birth',
                  "role", "email", 'contact',
                  "is_active", "is_staff", "is_superuser",
                  'profile_image', 'address', 'bio',]     

class EnhancedChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True, 
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long and contain uppercase, lowercase, number and special character"
    )
    confirm_password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        # Use Django's built-in password validation
        validate_password(value)
        
        # Additional custom validation
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        # Check for common patterns
        common_patterns = ['123456', 'password', 'qwerty', 'abc123']
        if value.lower() in common_patterns:
            raise serializers.ValidationError("Password is too common. Please choose a stronger password.")
        
        return value
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'New passwords do not match.'
            })
        
        user = self.context['request'].user
        
        # Check if new password is different from current password
        if user.check_password(data['new_password']):
            raise serializers.ValidationError({
                'new_password': 'New password must be different from current password.'
            })
        
        return data
    