from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import connection
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Organization, OrganizationMembership
from .permissions import IsSuperUser
from .serializers import (
    OrganizationApprovalSerializer,
    OrganizationCreateSerializer,
    OrganizationJoinSerializer,
    OrganizationMembershipSerializer,
    OrganizationSearchSerializer,
    OrganizationSummarySerializer,
    _find_similar_organizations,
)
from .throttles import OrgCreateThrottle, OrgJoinThrottle, OrgSearchThrottle


class OrganizationSearchView(APIView):
    """
    GET /api/organizations/search/?q=...
    Live search used by the org-picker autocomplete. Only ever returns
    APPROVED organizations — pending/rejected orgs are not joinable and
    aren't exposed here to avoid leaking who's mid-review.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrgSearchThrottle]
    throttle_scope = "org_search"

    def get(self, request):
        serializer = OrganizationSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        q = serializer.validated_data["q"]

        if connection.vendor == "postgresql":
            from django.contrib.postgres.search import TrigramSimilarity

            results = (
                Organization.objects.filter(status=Organization.Status.APPROVED)
                .annotate(similarity=TrigramSimilarity("name", q))
                .filter(similarity__gt=0.15)
                .order_by("-similarity")[:10]
            )
        else:
            results = Organization.objects.filter(
                status=Organization.Status.APPROVED, name__icontains=q
            )[:10]

        return Response(OrganizationSummarySerializer(results, many=True).data)


class OrganizationDuplicateCheckView(APIView):
    """
    GET /api/organizations/check-name/?q=...
    Used while the user is typing a NEW org name, before they submit
    creation — shows near-duplicates across pending + approved orgs
    (not just approved), since the goal here is preventing accidental
    re-creation, not just search relevance.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrgSearchThrottle]
    throttle_scope = "org_search"

    def get(self, request):
        serializer = OrganizationSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        q = serializer.validated_data["q"]

        similar = _find_similar_organizations(q)
        return Response(
            {
                "has_similar": bool(similar),
                "similar_organizations": OrganizationSummarySerializer(
                    [org for org, _ in similar], many=True
                ).data,
            }
        )


class OrganizationsView(APIView):
    """
    GET /api/organizations/
    Retrieves the organization for the authenticated user.
    """
    permission_classes = [IsAdminUser]
    throttle_classes = [OrgSearchThrottle]
    throttle_scope = "org_search"

    def get(self, request):
        organization = Organization.objects.all()
        if organization:
            serializer = OrganizationSummarySerializer(organization, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "No approved organization found for the user."}, status=status.HTTP_404_NOT_FOUND)


class OrganizationCreateView(APIView):
    """
    POST /api/organizations/create/
    Creates an org in PENDING status + a pending OWNER membership for the
    requester. Nothing here is usable until a superuser approves it.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrgCreateThrottle]
    throttle_scope = "org_create"

    def get(self, request):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization:
            return Response(OrganizationSummarySerializer(organization).data)
        return Response({"detail": "No approved organization found for the user."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = OrganizationCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        return Response(
            {
                "organization": OrganizationSummarySerializer(org).data,
                "detail": "Organization submitted for review. You'll be notified once a superuser approves it.",
            },
            status=status.HTTP_201_CREATED,
        )


class OrganizationJoinView(APIView):
    """
    POST /api/organizations/join/  { organization_id, role }
    Regular member roles on an approved org auto-approve. Owner/Admin
    requests always queue for superuser approval, and are blocked
    outright if that seat is already filled.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrgJoinThrottle]
    throttle_scope = "org_join"

    def post(self, request):
        serializer = OrganizationJoinSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(OrganizationMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class MyMembershipsView(ListAPIView):
    """GET /api/organizations/my-memberships/ — so the frontend can show pending-approval state."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationMembershipSerializer

    def get_queryset(self):
        return OrganizationMembership.objects.filter(user=self.request.user).select_related("organization")


# ---- Superuser-only approval queue ----

class PendingOrganizationsView(ListAPIView):
    """GET /api/organizations/pending/ — superuser review queue."""
    permission_classes = [IsSuperUser]
    serializer_class = OrganizationSummarySerializer

    def get_queryset(self):
        return Organization.objects.filter(status=Organization.Status.PENDING).order_by("created_at")


class ApproveOrganizationView(APIView):
    """POST /api/organizations/<id>/review/  { action: 'approve' | 'reject', reason? }"""
    permission_classes = [IsSuperUser]

    def post(self, request, pk):
        try:
            org = Organization.objects.get(pk=pk, status=Organization.Status.PENDING)
        except Organization.DoesNotExist:
            return Response({"detail": "No pending organization with that id."}, status=404)

        serializer = OrganizationApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]
        reason = serializer.validated_data.get("reason", "")

        try:
            if action == "approve":
                org.approve(request.user)
            else:
                org.reject(request.user, reason=reason)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message)

        return Response(OrganizationSummarySerializer(org).data)


class PendingMembershipsView(ListAPIView):
    """GET /api/organizations/pending-memberships/ — superuser queue for owner/admin requests on already-approved orgs."""
    permission_classes = [IsSuperUser]
    serializer_class = OrganizationMembershipSerializer

    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            status=OrganizationMembership.Status.PENDING
        ).select_related("organization", "user").order_by("requested_at")


class ApproveMembershipView(APIView):
    """POST /api/organizations/memberships/<id>/review/  { action: 'approve' | 'reject', reason? }"""
    permission_classes = [IsSuperUser]

    def post(self, request, pk):
        try:
            membership = OrganizationMembership.objects.get(
                pk=pk, status=OrganizationMembership.Status.PENDING
            )
        except OrganizationMembership.DoesNotExist:
            return Response({"detail": "No pending membership with that id."}, status=404)

        serializer = OrganizationApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]
        reason = serializer.validated_data.get("reason", "")

        if action == "approve":
            membership.approve(request.user)
        else:
            membership.reject(request.user, reason=reason)

        return Response(OrganizationMembershipSerializer(membership).data)
    