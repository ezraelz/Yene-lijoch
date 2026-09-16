from django.db import models

from users.models import Profile


class Teacher(models.Model):

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    employment_date = models.DateField(
        "Employment Date",
        auto_now_add=True,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["id"]

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}"

    # ------------------------------------------------------------------
    # Helpers — the API needs these even though they're not DB fields.
    # ------------------------------------------------------------------
    @property
    def full_name(self):
        return self.profile.get_full_name() if self.profile_id else ""

    @property
    def organization(self):
        """
        Teacher has no direct organization FK. Resolve through
        Profile.organization (an OrganizationMembership).
        """
        membership = getattr(self.profile, "organization", None)
        if not membership:
            return None
        return getattr(membership, "organization", membership)

    @property
    def organization_id(self):
        org = self.organization
        return org.id if org else None
    