from django.urls import path

from . import views

urlpatterns = [
    path("organizations/search/", views.OrganizationSearchView.as_view(), name="org-search"),
    path("organizations/check-name/", views.OrganizationDuplicateCheckView.as_view(), name="org-check-name"),
    path("organizations/", views.OrganizationsView.as_view(), name="org-organizations"),
    path("organizations/create/", views.OrganizationCreateView.as_view(), name="org-create"),

    # Superuser-only
    path("organizations/pending/", views.PendingOrganizationsView.as_view(), name="org-pending"),
    path("organizations/<int:pk>/review/", views.ApproveOrganizationView.as_view(), name="org-review"),
]
