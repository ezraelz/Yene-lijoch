from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils import timezone

from .utils import normalize_org_name


class Organization(models.Model):
    class OrgType(models.TextChoices):
        SCHOOL = "school", "School"
        CHURCH = "church", "Church"
        BOTH = "both", "School & Church"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=150)
    # Comparison key used for duplicate detection. Not shown to users.
    normalized_name = models.CharField(max_length=150, db_index=True)
    org_type = models.CharField(max_length=10, choices=OrgType.choices, default=OrgType.SCHOOL)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    address = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organizations_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Approval audit trail
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizations_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            # Hard duplicate-prevention constraint. Only enforced across
            # non-rejected orgs, so a rejected duplicate doesn't permanently
            # block a legitimate resubmission under the same name.
            UniqueConstraint(
                fields=["normalized_name"],
                condition=~Q(status="rejected"),
                name="unique_active_normalized_org_name",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_org_name(self.name)
        super().save(*args, **kwargs)

    def approve(self, approving_user):
        if self.created_by_id == getattr(approving_user, "id", None):
            raise ValidationError("A superuser cannot approve an organization they created themselves.")
        self.status = Organization.Status.APPROVED
        self.approved_by = approving_user
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_by", "approved_at"])

        # The creator's own membership request (as owner) is approved
        # alongside the org itself.
        owner_membership = self.memberships.filter(
            role=OrganizationMembership.Role.OWNER,
            status=OrganizationMembership.Status.PENDING,
        ).first()
        if owner_membership:
            owner_membership.approve(approving_user)

    def reject(self, approving_user, reason=""):
        self.status = Organization.Status.REJECTED
        self.approved_by = approving_user
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=["status", "approved_by", "approved_at", "rejection_reason"])
        self.memberships.filter(status=OrganizationMembership.Status.PENDING).update(
            status=OrganizationMembership.Status.REJECTED,
            reviewed_by=approving_user,
            reviewed_at=timezone.now(),
            rejection_reason=reason or "Organization was not approved.",
        )

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "Teacher"
        PARENT = "parent", "Parent / Guardian"
        STUDENT = "student", "Student"
        CLERGY = "clergy", "Clergy / Pastor"

    # Roles that are capped at one approved holder per organization and
    # always require superuser sign-off, even on an already-approved org.
    LEADERSHIP_ROLES = {Role.OWNER, Role.ADMIN}

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_memberships")
    role = models.CharField(max_length=10, choices=Role.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memberships_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            # A user can only have one active (pending or approved) request
            # per org — stops duplicate-request spam.
            UniqueConstraint(
                fields=["organization", "user"],
                condition=Q(status__in=["pending", "approved"]),
                name="unique_active_membership_per_user_org",
            ),
            # THE key rule: at most one APPROVED owner, and separately at
            # most one APPROVED admin, per organization.
            UniqueConstraint(
                fields=["organization", "role"],
                condition=Q(status="approved", role="owner"),
                name="unique_approved_owner_per_org",
            ),
            UniqueConstraint(
                fields=["organization", "role"],
                condition=Q(status="approved", role="admin"),
                name="unique_approved_admin_per_org",
            ),
        ]

    def approve(self, approving_user):
        self.status = OrganizationMembership.Status.APPROVED
        self.reviewed_by = approving_user
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    def reject(self, approving_user, reason=""):
        self.status = OrganizationMembership.Status.REJECTED
        self.reviewed_by = approving_user
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])

    def __str__(self):
        return f"{self.user} -> {self.organization} ({self.role}, {self.status})"
    