from django.urls import path

from apps.users.views import (
    AdminUserDetailView,
    AdminUsersListView,
    ApproveSellerApplicationView,
    AvatarUploadView,
    EmailHistoryView,
    ListSellerApplicationsView,
    ProfileView,
    RejectSellerApplicationView,
    SubmitSellerApplicationView,
)

app_name = "users"

urlpatterns = [
    path("me/", ProfileView.as_view(), name="profile"),
    path("me/avatar/", AvatarUploadView.as_view(), name="avatar-upload"),
    path("me/email-history/", EmailHistoryView.as_view(), name="email-history"),
    path(
        "me/seller-application/",
        SubmitSellerApplicationView.as_view(),
        name="seller-application",
    ),
    path(
        "seller-applications/",
        ListSellerApplicationsView.as_view(),
        name="list-seller-applications",
    ),
    path(
        "seller-applications/<int:application_id>/approve/",
        ApproveSellerApplicationView.as_view(),
        name="approve-seller-application",
    ),
    path(
        "seller-applications/<int:application_id>/reject/",
        RejectSellerApplicationView.as_view(),
        name="reject-seller-application",
    ),
    path("", AdminUsersListView.as_view(), name="admin-users-list"),
    path(
        "<uuid:public_id>/",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),
]
