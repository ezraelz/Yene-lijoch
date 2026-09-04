import difflib

from django.conf import settings
from django.db import connection
from rest_framework import serializers

from .models import Organization, OrganizationMembership
from .utils import normalize_org_name, sanitize_org_name

SIMILARITY_THRESHOLD = 0.35  # tune based on false-positive rate in practice
MAX_SIMILAR_RESULTS = 6


def _find_similar_organizations(name: str):
    """
    Returns a list of (organization, score) for names similar to `name`,
    across pending + approved orgs (rejected orgs excluded — they're free
    to be resubmitted). Uses Postgres trigram similarity when available;
    falls back to difflib for local/sqlite dev so this doesn't hard-fail
    outside production.
    """
    candidates = Organization.objects.exclude(status=Organization.Status.REJECTED)

    if connection.vendor == "postgresql":
        from django.contrib.postgres.search import TrigramSimilarity

        results = (
            candidates.annotate(similarity=TrigramSimilarity("name", name))
            .filter(similarity__gt=SIMILARITY_THRESHOLD)
            .order_by("-similarity")[:MAX_SIMILAR_RESULTS]
        )
        return [(org, org.similarity) for org in results]

    # Fallback (dev/sqlite): compute in Python. Fine at small scale only —
    # do not rely on this path in production with a large orgs table.
    scored = []
    for org in candidates.only("id", "name", "status", "created_by_id"):
        score = difflib.SequenceMatcher(None, name.lower(), org.name.lower()).ratio()
        if score > SIMILARITY_THRESHOLD:
            scored.append((org, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:MAX_SIMILAR_RESULTS]


class OrganizationSummarySerializer(serializers.ModelSerializer):
    """
    Public-facing summary used in search/dup-check results. Deliberately
    omits created_by and other internal fields so we don't leak who
    submitted a pending org to every other user searching by name.
    """
    similarity = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Organization
        fields = ["id", "name", "org_type", "status", "similarity"]
        read_only_fields = fields


class OrganizationSearchSerializer(serializers.Serializer):
    q = serializers.CharField(min_length=2, max_length=150)

    def validate_q(self, value):
        return sanitize_org_name(value)


class OrganizationCreateSerializer(serializers.ModelSerializer):
    # If the frontend already showed the user near-duplicates and they
    # explicitly chose "create anyway", it sends confirm=true. Without it,
    # a close match blocks creation and returns the matches instead.
    confirm_despite_similar = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Organization
        fields = ["id", "name", "org_type", "address", "contact", "confirm_despite_similar"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = sanitize_org_name(value)
        if len(value) < 3:
            raise serializers.ValidationError("Organization name must be at least 3 characters.")
        if len(value) > 150:
            raise serializers.ValidationError("Organization name is too long.")
        return value

    def validate(self, attrs):
        name = attrs.get("name", "")
        normalized = normalize_org_name(name)

        exact = Organization.objects.exclude(status=Organization.Status.REJECTED).filter(
            normalized_name=normalized
        ).first()
        if exact:
            raise serializers.ValidationError(
                {"name": "An organization with this name already exists. Try joining it instead."}
            )

        if not attrs.pop("confirm_despite_similar", False):
            similar = _find_similar_organizations(name)
            if similar:
                # Surface the matches via a structured error the frontend
                # can render as "did you mean...?" instead of a plain
                # validation message.
                raise serializers.ValidationError(
                    {
                        "similar_organizations": OrganizationSummarySerializer(
                            [org for org, _ in similar], many=True
                        ).data,
                        "detail": "Similar organizations already exist. Confirm to create a new one anyway.",
                    }
                )
        else:
            attrs.pop("confirm_despite_similar", None)

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data.pop("confirm_despite_similar", None)
        org = Organization.objects.create(
            **validated_data,
            created_by=request.user,
            status=Organization.Status.PENDING,
        )
        OrganizationMembership.objects.create(
            organization=org,
            user=request.user,
            role=OrganizationMembership.Role.OWNER,
            status=OrganizationMembership.Status.PENDING,
        )
        return org


class OrganizationJoinSerializer(serializers.Serializer):
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(status=Organization.Status.APPROVED),
        source="organization",
    )
    role = serializers.ChoiceField(choices=OrganizationMembership.Role.choices)

    def validate(self, attrs):
        request = self.context["request"]
        org = attrs["organization"]
        role = attrs["role"]

        existing = OrganizationMembership.objects.filter(
            organization=org, user=request.user, status__in=["pending", "approved"]
        ).first()
        if existing:
            raise serializers.ValidationError(
                f"You already have a {existing.get_status_display().lower()} "
                f"request for this organization."
            )

        if role in OrganizationMembership.LEADERSHIP_ROLES:
            seat_taken = OrganizationMembership.objects.filter(
                organization=org, role=role, status=OrganizationMembership.Status.APPROVED
            ).exists()
            if seat_taken:
                raise serializers.ValidationError(
                    f"This organization already has an approved {role}. "
                    "Ask them to add you, or choose a different role."
                )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        role = validated_data["role"]
        # Leadership roles always need superuser sign-off, even on an
        # already-approved org. Regular member roles on an approved org
        # are auto-approved — the org itself was already vetted.
        auto_approve = role not in OrganizationMembership.LEADERSHIP_ROLES

        membership = OrganizationMembership.objects.create(
            organization=validated_data["organization"],
            user=request.user,
            role=role,
            status=OrganizationMembership.Status.APPROVED if auto_approve else OrganizationMembership.Status.PENDING,
        )
        if auto_approve:
            membership.reviewed_at = membership.requested_at
            membership.save(update_fields=["reviewed_at"])
        return membership


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    user_display = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMembership
        fields = [
            "id", "organization", "organization_name", "user", "user_display",
            "role", "status", "requested_at", "reviewed_by", "reviewed_at",
            "rejection_reason",
        ]
        read_only_fields = fields

    def get_user_display(self, obj):
        full_name = f"{getattr(obj.user, 'first_name', '')} {getattr(obj.user, 'last_name', '')}".strip()
        return full_name or getattr(obj.user, "username", str(obj.user))


class OrganizationApprovalSerializer(serializers.Serializer):
    """Used by the superuser-only approve/reject endpoint."""
    action = serializers.ChoiceField(choices=["approve", "reject"])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    