from django.db import models
from django.utils import timezone


class EmailHistory(models.Model):
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="email_history"
    )
    email = models.EmailField()
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-changed_at"]
        indexes = [
            models.Index(fields=["user", "-changed_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.email} ({self.changed_at})"

    def __repr__(self):
        return f"EmailHistory(user={self.user.email}, email={self.email}, changed_at={self.changed_at})"
