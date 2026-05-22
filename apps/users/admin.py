from django.contrib import admin
from django.contrib import messages

from apps.users.models import (
    ApplicationStatus,
    CustomUser,
    EmailHistory,
    SellerApplication,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "account_type",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "account_type")


@admin.register(EmailHistory)
class EmailHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "email")
    search_fields = ("user__email", "email")


@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_applications", "reject_applications"]

    @admin.action(description="Approve selected applications")
    def approve_applications(self, request, queryset):
        pending = queryset.filter(status=ApplicationStatus.PENDING)
        count = pending.count()
        for application in pending:
            application.status = ApplicationStatus.APPROVED
            application.save()
        self.message_user(
            request, f"{count} application(s) approved.", messages.SUCCESS
        )

    @admin.action(description="Reject selected applications")
    def reject_applications(self, request, queryset):
        pending = queryset.filter(status=ApplicationStatus.PENDING)
        count = pending.count()
        for application in pending:
            application.status = ApplicationStatus.REJECTED
            application.rejection_reason = "Rejected by admin."
            application.save()
        self.message_user(
            request, f"{count} application(s) rejected.", messages.WARNING
        )
