# models.py
from django.db import models
from django.core.validators import EmailValidator, URLValidator
from django.core.exceptions import ValidationError

class Church(models.Model):
    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, verbose_name="Church Name")
    denomination = models.CharField(max_length=200, blank=True, null=True, verbose_name="Denomination")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name="Status"
    )
    # Approval
    is_approved = models.BooleanField(default=False,blank=True, null=True ,verbose_name="Is Approved")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Approved At")
    approved_by = models.CharField(max_length=200, blank=True, null=True, verbose_name="Approved By")
    
    # Contact Information
    address = models.TextField(blank=True, verbose_name="Address")
    region = models.CharField(max_length=100, blank=True, null=True,verbose_name="Region")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Phone Number")
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    website = models.URLField(blank=True, null=True, verbose_name="Website", validators=[URLValidator()])
    
    # Leadership & Statistics
    pastor = models.CharField(max_length=200, blank=True, null=True, verbose_name="Pastor/Lead Minister")
    founded = models.CharField(max_length=20, blank=True, null=True, verbose_name="Founded Year")
    total_members = models.PositiveIntegerField(default=0,blank=True, null=True, verbose_name="Total Members")
    total_services = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name="Total Services")
    
    # Service Times (stored as JSON)
    service_times = models.JSONField(
        default=dict, 
        blank=True, null=True,
        verbose_name="Service Times",
        help_text="Format: {'sunday': '10:00 AM', 'wednesday': '7:00 PM', 'friday': '6:00 PM'}"
    )
    
    # Social Media (stored as JSON)
    social_media = models.JSONField(
        default=dict, 
        blank=True, null=True,
        verbose_name="Social Media",
        help_text="Format: {'facebook': 'url', 'instagram': 'url', 'youtube': 'url'}"
    )
    
    # Description
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", blank=True, null=True)
    
    class Meta:
        db_table = 'churches'
        verbose_name = 'Church'
        verbose_name_plural = 'Churches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['denomination']),
            models.Index(fields=['region']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate the model data"""
        super().clean()
        
        # Validate phone number format (optional)
        if self.phone and not self._is_valid_phone(self.phone):
            raise ValidationError({'phone': 'Please enter a valid phone number.'})
        
        # Validate founded year
        if self.founded:
            try:
                year = int(self.founded)
                current_year = 2024
                if year < 1000 or year > current_year:
                    raise ValidationError({'founded': f'Please enter a valid year between 1000 and {current_year}.'})
            except ValueError:
                raise ValidationError({'founded': 'Please enter a valid year.'})
    
    def _is_valid_phone(self, phone):
        """Validate phone number format"""
        import re
        # Allow: +1 (555) 000-0000, 555-000-0000, (555) 000-0000, etc.
        pattern = r'^[\+\d\s\-\(\)]{10,}$'
        return bool(re.match(pattern, phone.replace(' ', '')))
    
    def get_service_times_display(self):
        """Get formatted service times for display"""
        if not self.service_times:
            return {}
        return {
            day: time 
            for day, time in self.service_times.items() 
            if time
        }
    
    def get_social_media_display(self):
        """Get formatted social media for display"""
        if not self.social_media:
            return {}
        return {
            platform: url 
            for platform, url in self.social_media.items() 
            if url
        }
    
    def get_status_display(self):
        """Get human-readable status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    