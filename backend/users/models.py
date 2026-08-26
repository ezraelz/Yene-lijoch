from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from roles.models import Role
from django.contrib.auth.hashers import check_password, make_password

class ProfileManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(username=username, email=email, password=password, **extra_fields)

class Profile(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField("First Name", max_length=150, null=True, blank=True)
    last_name = models.CharField("Last Name", max_length=150, null=True, blank=True)
    username = models.CharField("Username", max_length=50, unique=True, null=True, blank=True)
    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField('Sex', max_length=10, blank=True, null=True)
    email = models.EmailField("Email", max_length=254, unique=True, null=True, blank=True)
    contact = models.CharField('Contact', max_length=100, null=True, blank=True)
    address = models.CharField('Address', blank=True, null=True)
    date_of_birth = models.DateField("Date of Birth", null=True, blank=True)
    profile_image = models.ImageField("Profile Picture", upload_to="profile/", default="fun.jpg", null=True, blank=True)
    bio = models.CharField("Bio", max_length=250, blank=True, null=True)
    role = models.ForeignKey(Role, verbose_name="Role", on_delete=models.SET_NULL, blank=True, null=True)
    last_seen = models.DateField("Last seen", auto_now=True, null=True, blank=True)
    created_at = models.DateField("Created at", auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email",]

    objects = ProfileManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]

    def has_perm(self, perm, obj=None):
        if self.role and self.role.role_name == "admin":
            return True  # Admins have all permissions
        if self.role and self.role.role_name == "teacher" and perm in ["view_class", "edit_class"]:
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        if self.role and self.role.role_name == "admin":
            return True
        return super().has_module_perms(app_label)
    
    def get_full_name(self):
        """Return the full name of the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif hasattr(self, 'username'):
            return self.username
        elif hasattr(self, 'email'):
            return self.email.split('@')[0]
        else:
            return "Unknown User"
    

class PasswordHistory(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='password_history')
    password = models.CharField(max_length=128)  # Store hashed password
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Password Histories"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Hash the password before saving
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    