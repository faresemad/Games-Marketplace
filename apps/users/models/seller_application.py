from django.db import models

from apps.users.models import CustomUser


class ApplicationStatus:
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

    @classmethod
    def as_choices(cls):
        return [(value, name) for name, value in vars(cls).items() if name.isupper()]


class SellerApplication(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="seller_applications",
    )
    front_id_image = models.ImageField(upload_to="seller_docs/")
    back_id_image = models.ImageField(upload_to="seller_docs/")
    selfie_image = models.ImageField(upload_to="seller_docs/")
    status = models.CharField(
        max_length=16,
        choices=ApplicationStatus.as_choices(),
        default=ApplicationStatus.PENDING,
    )
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.status}"
