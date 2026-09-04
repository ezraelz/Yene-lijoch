from django.urls import path

from . import views

urlpatterns = [
    path("organizations/search/", views.OrganizationSearchView.as_view(), name="org-search"),
    path("organizations/check-name/", views.OrganizationDuplicateCheckView.as_view(), name="org-check-name"),
    path("organizations/", views.OrganizationsView.as_view(), name="org-organizations"),
    path("organizations/create/", views.OrganizationCreateView.as_view(), name="org-create"),
    path("organizations/join/", views.OrganizationJoinView.as_view(), name="org-join"),
    path("organizations/my-memberships/", views.MyMembershipsView.as_view(), name="org-my-memberships"),

    # Superuser-only
    path("organizations/pending/", views.PendingOrganizationsView.as_view(), name="org-pending"),
    path("organizations/<int:pk>/review/", views.ApproveOrganizationView.as_view(), name="org-review"),
    path("organizations/pending-memberships/", views.PendingMembershipsView.as_view(), name="org-pending-memberships"),
    path("organizations/memberships/<int:pk>/review/", views.ApproveMembershipView.as_view(), name="org-membership-review"),
]
