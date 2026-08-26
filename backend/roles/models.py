from django.db import models


class Permission(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
    )
    category = models.CharField(
        max_length=100,
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip()

        if self.codename:
            self.codename = self.codename.strip().lower()

        if self.category:
            self.category = self.category.strip().lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Role(models.Model):
    role_name = models.CharField(
        max_length=50,
        unique=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    permissions = models.ManyToManyField(
        Permission,
         blank=True,
         null=True,
        related_name="roles",
    )
    is_active = models.BooleanField(
        default=True,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["role_name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def save(self, *args, **kwargs):
        if self.role_name:
            self.role_name = self.role_name.strip().lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.role_name.capitalize()
    