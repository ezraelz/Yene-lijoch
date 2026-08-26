# serializers.py
from rest_framework import serializers
from .models import Church

class ChurchSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    service_times_display = serializers.SerializerMethodField()
    social_media_display = serializers.SerializerMethodField()
    is_approved_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Church
        fields = [
            'id', 
            'name', 
            'denomination', 
            'status', 
            'status_display',
            'address', 
            'region',
            'phone', 
            'email', 
            'website',
            'pastor',
            'founded',
            'total_members',
            'total_services',
            'is_approved',
            'is_approved_display',
            'approved_at',
            'approved_by',
            'service_times',
            'service_times_display',
            'social_media',
            'social_media_display',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_service_times_display(self, obj):
        return obj.get_service_times_display()
    
    def get_social_media_display(self, obj):
        return obj.get_social_media_display()
    
    def get_is_approved_display(self, obj):
        return "Yes" if obj.is_approved else "No"
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value and not self.instance._is_valid_phone(value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def validate_founded(self, value):
        """Validate founded year"""
        if value:
            try:
                year = int(value)
                current_year = 2024
                if year < 1000 or year > current_year:
                    raise serializers.ValidationError(
                        f"Year must be between 1000 and {current_year}"
                    )
            except ValueError:
                raise serializers.ValidationError("Please enter a valid year")
        return value
    
    def validate_service_times(self, value):
        """Validate service times format"""
        if value:
            valid_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            for day in value.keys():
                if day.lower() not in valid_days:
                    raise serializers.ValidationError(
                        f"Invalid day: {day}. Must be one of {valid_days}"
                    )
        return value