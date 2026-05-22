from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q

from apps.users.models import ApplicationStatus, CustomUser, SellerApplication
from apps.users.models.users import AccountType
from apps.users.serializers import (
    AdminUserListSerializer,
    AvatarUploadSerializer,
    EmailHistorySerializer,
    ProfileSerializer,
    SellerApplicationActionSerializer,
    SellerApplicationListSerializer,
    SellerApplicationSerializer,
)


@extend_schema_view(
    get=extend_schema(tags=["users"], summary="Get profile"),
    patch=extend_schema(tags=["users"], summary="Update profile", request=ProfileSerializer),
    delete=extend_schema(tags=["users"], summary="Delete account"),
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = ProfileSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        serializer = ProfileSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["users"], summary="Upload avatar", request=AvatarUploadSerializer)
class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = AvatarUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = AvatarUploadSerializer(
            request.user, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(ProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["users"], summary="View email history", responses={200: EmailHistorySerializer(many=True)})
class EmailHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        history = request.user.email_history.all()
        serializer = EmailHistorySerializer(history, many=True)
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(tags=["sellers"], summary="Submit seller application", request=SellerApplicationSerializer),
    get=extend_schema(tags=["sellers"], summary="View own applications", responses={200: SellerApplicationSerializer(many=True)}),
)
class SubmitSellerApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = SellerApplicationSerializer

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.account_type not in (AccountType.BUYER, AccountType.REJECTED_SELLER):
            return Response(
                {
                    "detail": "Only buyers or previously rejected sellers can submit an application."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if SellerApplication.objects.filter(
            user=user, status=ApplicationStatus.PENDING
        ).exists():
            return Response(
                {"detail": "You already have a pending application."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SellerApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        applications = request.user.seller_applications.all()
        serializer = SellerApplicationSerializer(applications, many=True)
        return Response(serializer.data)


@extend_schema(tags=["sellers"], summary="List all applications (admin/support)", responses={200: SellerApplicationListSerializer(many=True)})
class ListSellerApplicationsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SellerApplicationListSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.account_type not in (AccountType.ADMIN, AccountType.SUPPORT):
            return Response(
                {"detail": "You do not have permission to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        status_filter = request.query_params.get("status")
        applications = SellerApplication.objects.all()
        if status_filter:
            applications = applications.filter(status=status_filter)

        serializer = SellerApplicationListSerializer(applications, many=True)
        return Response(serializer.data)


@extend_schema(tags=["sellers"], summary="Approve application (admin/support)", request=None)
class ApproveSellerApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request, application_id, *args, **kwargs):
        user = request.user
        if user.account_type not in (AccountType.ADMIN, AccountType.SUPPORT):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            application = SellerApplication.objects.get(
                id=application_id, status=ApplicationStatus.PENDING
            )
        except SellerApplication.DoesNotExist:
            return Response(
                {"detail": "Application not found or already processed."},
                status=status.HTTP_404_NOT_FOUND,
            )

        application.status = ApplicationStatus.APPROVED
        application.save()
        return Response(
            {"detail": "Seller application approved.", "application_id": application.id}
        )


@extend_schema(tags=["sellers"], summary="Reject application (admin/support)", request=SellerApplicationActionSerializer)
class RejectSellerApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SellerApplicationActionSerializer

    def post(self, request, application_id, *args, **kwargs):
        user = request.user
        if user.account_type not in (AccountType.ADMIN, AccountType.SUPPORT):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            application = SellerApplication.objects.get(
                id=application_id, status=ApplicationStatus.PENDING
            )
        except SellerApplication.DoesNotExist:
            return Response(
                {"detail": "Application not found or already processed."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerApplicationActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        application.status = ApplicationStatus.REJECTED
        application.rejection_reason = serializer.validated_data.get(
            "rejection_reason", ""
        )
        application.save()
        return Response(
            {
                "detail": "Seller application rejected.",
                "application_id": application.id,
                "rejection_reason": application.rejection_reason,
            }
        )


@extend_schema_view(
    get=extend_schema(tags=["admin"], summary="List all users (admin/support)"),
)
class AdminUsersListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminUserListSerializer

    def get(self, request, *args, **kwargs):
        if request.user.account_type not in (AccountType.ADMIN, AccountType.SUPPORT):
            return Response(
                {"detail": "You do not have permission to view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        users = CustomUser.objects.all().order_by("-date_joined")

        account_type = request.query_params.get("account_type")
        if account_type:
            users = users.filter(account_type=account_type)

        search = request.query_params.get("search")
        if search:
            users = users.filter(
                Q(email__icontains=search)
                | Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            users = users.filter(is_active=is_active.lower() == "true")

        serializer = AdminUserListSerializer(users, many=True)
        return Response(serializer.data)


@extend_schema_view(
    patch=extend_schema(
        tags=["admin"],
        summary="Update user account type (admin only)",
        request=AdminUserListSerializer,
    ),
)
class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminUserListSerializer

    def patch(self, request, public_id, *args, **kwargs):
        if request.user.account_type != AccountType.ADMIN:
            return Response(
                {"detail": "Only admins can update user account types."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            target_user = CustomUser.objects.get(public_id=public_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        account_type = request.data.get("account_type")
        if account_type:
            valid_types = [v for v, _ in AccountType.as_choices()]
            if account_type not in valid_types:
                return Response(
                    {"detail": f"Invalid account type. Valid types: {', '.join(valid_types)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            target_user.account_type = account_type

        is_active = request.data.get("is_active")
        if is_active is not None:
            target_user.is_active = bool(is_active)

        target_user.save(update_fields=["account_type", "is_active"])
        serializer = AdminUserListSerializer(target_user)
        return Response(serializer.data)
