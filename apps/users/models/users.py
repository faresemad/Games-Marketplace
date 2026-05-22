from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.users.managers import CustomUserManager
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from apps.users.models.email_history import EmailHistory


class AccountType:
    BUYER: str = "Buyer"
    SELLER: str = "Seller"
    SUPPORT: str = "Support"
    ADMIN: str = "Admin"
    PENDING_SELLER: str = "Pending Seller"
    REJECTED_SELLER: str = "Rejected Seller"
    SUSPENDED: str = "Suspended"

    @classmethod
    def as_choices(cls):
        return [(value, name) for name, value in vars(cls).items() if name.isupper()]


class CustomUser(AbstractUser):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=150, blank=True, unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account_type = models.CharField(
        max_length=16,
        choices=AccountType.as_choices(),
        default=AccountType.BUYER,
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email

    def can_change_email(self):
        last_change = self.email_history.first()

        if not last_change:
            return True

        allowed_date = last_change.changed_at + timedelta(days=90)
        return timezone.now() >= allowed_date

    def change_email(self, new_email: str):
        if self.email == new_email:
            return

        if not self.can_change_email():
            raise ValidationError("You can only change your email once every 3 months.")

        EmailHistory.objects.create(user=self, email=self.email)

        self.email = new_email
        self.save()
