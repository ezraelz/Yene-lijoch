import csv
import io

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.parsers import (
    JSONParser,
    MultiPartParser,
    FormParser,
    FileUploadParser,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Role, Permission
from .serializers import (
    RoleSerializer,
    PermissionSerializer,
)
from .pagination import RolePagination


# ============================================================
# ROLES
# ============================================================

class RoleView(APIView):
    permission_classes = []

    def get(self, request):
        roles = (
            Role.objects
            .prefetch_related("permissions")
            .all()
            .order_by("role_name")
        )

        search = request.query_params.get("search")

        if search:
            search = search.strip()

            if search:
                roles = roles.filter(
                    Q(role_name__icontains=search)
                    | Q(description__icontains=search)
                )

        paginator = RolePagination()

        page = paginator.paginate_queryset(
            roles,
            request,
            view=self,
        )

        serializer = RoleSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = RoleSerializer(
            data=request.data
        )

        if serializer.is_valid():
            role = serializer.save()

            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class RoleDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        role = get_object_or_404(
            Role.objects.prefetch_related("permissions"),
            id=pk,
        )

        serializer = RoleSerializer(role)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        role = get_object_or_404(
            Role,
            id=pk,
        )

        serializer = RoleSerializer(
            role,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            role = serializer.save()

            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):
        role = get_object_or_404(
            Role,
            id=pk,
        )

        serializer = RoleSerializer(
            role,
            data=request.data,
        )

        if serializer.is_valid():
            role = serializer.save()

            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        role = get_object_or_404(
            Role,
            id=pk,
        )

        role.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class RoleStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_roles = Role.objects.count()

        active_roles = Role.objects.filter(
            is_active=True
        ).count()

        inactive_roles = Role.objects.filter(
            is_active=False
        ).count()

        total_permissions = Permission.objects.count()

        roles_with_permissions = (
            Role.objects
            .filter(permissions__isnull=False)
            .distinct()
            .count()
        )

        roles_without_permissions = (
            total_roles - roles_with_permissions
        )

        return Response(
            {
                "total_roles": total_roles,
                "active_roles": active_roles,
                "inactive_roles": inactive_roles,
                "total_permissions": total_permissions,
                "roles_with_permissions": roles_with_permissions,
                "roles_without_permissions": roles_without_permissions,
            },
            status=status.HTTP_200_OK,
        )


class RoleCopyView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        original_role = get_object_or_404(
            Role.objects.prefetch_related("permissions"),
            id=pk,
        )

        new_name = request.data.get("new_name")

        if not isinstance(new_name, str) or not new_name.strip():
            return Response(
                {
                    "detail": "new_name is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_name = new_name.strip().lower()

        if Role.objects.filter(
            role_name=new_name
        ).exists():
            return Response(
                {
                    "detail": "A role with this name already exists."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_role = Role.objects.create(
            role_name=new_name,
            description=original_role.description,
            is_active=original_role.is_active,
        )

        new_role.permissions.set(
            original_role.permissions.all()
        )

        serializer = RoleSerializer(new_role)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# PERMISSIONS
# ============================================================

class PermissionView(APIView):
    """
    GET:
        List active/inactive permissions with pagination,
        search and category filters.

    POST:
        Create a permission.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        permissions = Permission.objects.all()

        search = request.query_params.get("search")
        category = request.query_params.get("category")
        is_active = request.query_params.get("is_active")

        if search:
            search = search.strip()

            if search:
                permissions = permissions.filter(
                    Q(name__icontains=search)
                    | Q(codename__icontains=search)
                    | Q(category__icontains=search)
                )

        if category:
            permissions = permissions.filter(
                category__iexact=category.strip()
            )

        if is_active is not None:
            if is_active.lower() in {"true", "1"}:
                permissions = permissions.filter(
                    is_active=True
                )

            elif is_active.lower() in {"false", "0"}:
                permissions = permissions.filter(
                    is_active=False
                )

        permissions = permissions.order_by(
            "category",
            "name",
        )

        paginator = RolePagination()

        page = paginator.paginate_queryset(
            permissions,
            request,
            view=self,
        )

        serializer = PermissionSerializer(
            page,
            many=True,
        )

        response = paginator.get_paginated_response(
            serializer.data
        )

        # The frontend expects:
        # response.data.data
        # response.data.total
        # response.data.total_pages
        # response.data.page
        return response

    def post(self, request):
        serializer = PermissionSerializer(
            data=request.data
        )

        if serializer.is_valid():
            permission = serializer.save()

            return Response(
                PermissionSerializer(permission).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PermissionDetailView(APIView):
    """
    GET    /permissions/<id>/
    PATCH  /permissions/<id>/
    PUT    /permissions/<id>/
    DELETE /permissions/<id>/
    """

    permission_classes = [IsAdminUser]

    def get_permission(self, pk):
        return get_object_or_404(
            Permission,
            id=pk,
        )

    def get(self, request, pk):
        permission = self.get_permission(pk)

        serializer = PermissionSerializer(
            permission
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        permission = self.get_permission(pk)

        serializer = PermissionSerializer(
            permission,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            permission = serializer.save()

            return Response(
                PermissionSerializer(permission).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):
        permission = self.get_permission(pk)

        serializer = PermissionSerializer(
            permission,
            data=request.data,
        )

        if serializer.is_valid():
            permission = serializer.save()

            return Response(
                PermissionSerializer(permission).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        permission = self.get_permission(pk)

        permission.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class PermissionCategoryView(APIView):
    """
    GET /permissions/category/

    Returns unique permission categories.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        categories = (
            Permission.objects
            .exclude(category__isnull=True)
            .exclude(category__exact="")
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )

        return Response(
            list(categories),
            status=status.HTTP_200_OK,
        )


class PermissionBulkDeleteView(APIView):
    """
    DELETE /permissions/<ids>/bulk/

    Example:
        DELETE /permissions/1,2,3/bulk/
    """

    permission_classes = [IsAdminUser]

    def delete(self, request, ids):
        raw_ids = ids.split(",")

        permission_ids = []

        for value in raw_ids:
            value = value.strip()

            if not value:
                continue

            if not value.isdigit():
                return Response(
                    {
                        "detail": f"Invalid permission ID: {value}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            permission_ids.append(int(value))

        if not permission_ids:
            return Response(
                {
                    "detail": "At least one permission ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = Permission.objects.filter(
            id__in=permission_ids
        ).delete()

        return Response(
            {
                "detail": (
                    f"{deleted_count} permission(s) "
                    "deleted successfully."
                ),
                "deleted": deleted_count,
            },
            status=status.HTTP_200_OK,
        )


class PermissionValidateView(APIView):
    """
    POST /permissions/validate/

    Supports both:

    {
        "code": "users.view"
    }

    and the raw string sent by the current hook:

        "users.view"
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        code = None

        if isinstance(request.data, dict):
            code = (
                request.data.get("code")
                or request.data.get("codename")
            )

        elif isinstance(request.data, str):
            code = request.data

        if not code:
            return Response(
                {
                    "valid": False,
                    "detail": "Permission code is required.",
                },
                status=status.HTTP_200_OK,
            )

        code = str(code).strip()

        exists = Permission.objects.filter(
            codename__iexact=code
        ).exists()

        return Response(
            {
                "valid": not exists,
                "code": code,
                "detail": (
                    "Permission code is available."
                    if not exists
                    else "Permission code already exists."
                ),
            },
            status=status.HTTP_200_OK,
        )


class PermissionExportView(APIView):
    """
    POST /permissions/export/

    Exports permissions as CSV.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        permissions = (
            Permission.objects
            .all()
            .order_by("category", "name")
        )

        response = HttpResponse(
            content_type="text/csv"
        )

        response[
            "Content-Disposition"
        ] = 'attachment; filename="permissions.csv"'

        writer = csv.writer(response)

        writer.writerow(
            [
                "id",
                "name",
                "codename",
                "category",
                "is_active",
            ]
        )

        for permission in permissions:
            writer.writerow(
                [
                    permission.id,
                    permission.name,
                    permission.codename,
                    permission.category,
                    permission.is_active,
                ]
            )

        return response


class PermissionImportView(APIView):
    """
    POST /permissions/import/

    Imports permissions from CSV.

    Expected columns:

        name,codename,category,is_active
    """

    permission_classes = [IsAdminUser]

    parser_classes = [
        MultiPartParser,
        FormParser,
        FileUploadParser,
        JSONParser,
    ]

    def post(self, request):
        uploaded_file = (
            request.FILES.get("file")
            or request.data.get("file")
        )

        # The current hook sends the File directly:
        #
        # api.post('/permissions/import/', file)
        #
        # Depending on the Axios configuration, it may arrive
        # as the raw request body instead of request.FILES.
        if uploaded_file is None:
            if request.body:
                uploaded_file = io.BytesIO(
                    request.body
                )

        if uploaded_file is None:
            return Response(
                {
                    "imported": 0,
                    "errors": [
                        "No CSV file was provided."
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if hasattr(uploaded_file, "read"):
                raw_content = uploaded_file.read()
            else:
                raw_content = uploaded_file

            if isinstance(raw_content, bytes):
                content = raw_content.decode(
                    "utf-8-sig"
                )
            else:
                content = str(raw_content)

            reader = csv.DictReader(
                io.StringIO(content)
            )

        except (UnicodeDecodeError, csv.Error) as exc:
            return Response(
                {
                    "imported": 0,
                    "errors": [
                        f"Invalid CSV file: {exc}"
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        required_columns = {
            "name",
            "codename",
            "category",
        }

        if not reader.fieldnames:
            return Response(
                {
                    "imported": 0,
                    "errors": [
                        "CSV file has no header row."
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        missing_columns = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:
            return Response(
                {
                    "imported": 0,
                    "errors": [
                        "Missing required columns: "
                        + ", ".join(
                            sorted(missing_columns)
                        )
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        imported = 0
        errors = []

        with transaction.atomic():
            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                name = (
                    row.get("name") or ""
                ).strip()

                codename = (
                    row.get("codename") or ""
                ).strip()

                category = (
                    row.get("category") or ""
                ).strip()

                if not name:
                    errors.append(
                        f"Row {row_number}: name is required."
                    )
                    continue

                if not codename:
                    errors.append(
                        f"Row {row_number}: codename is required."
                    )
                    continue

                if not category:
                    errors.append(
                        f"Row {row_number}: category is required."
                    )
                    continue

                if Permission.objects.filter(
                    codename__iexact=codename
                ).exists():
                    errors.append(
                        f"Row {row_number}: "
                        f"codename '{codename}' already exists."
                    )
                    continue

                is_active = True

                raw_active = row.get(
                    "is_active"
                )

                if raw_active is not None:
                    raw_active = (
                        str(raw_active)
                        .strip()
                        .lower()
                    )

                    if raw_active in {
                        "false",
                        "0",
                        "no",
                        "inactive",
                    }:
                        is_active = False

                    elif raw_active in {
                        "true",
                        "1",
                        "yes",
                        "active",
                    }:
                        is_active = True

                Permission.objects.create(
                    name=name,
                    codename=codename,
                    category=category,
                    is_active=is_active,
                )

                imported += 1

        return Response(
            {
                "imported": imported,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )
    