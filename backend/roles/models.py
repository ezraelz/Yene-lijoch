from django.db import models

class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.role_name:
            self.role_name = self.role_name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.role_name.capitalize()
        