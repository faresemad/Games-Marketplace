from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import ApplicationStatus, SellerApplication
from apps.users.models.users import AccountType


@receiver(post_save, sender=SellerApplication)
def handle_seller_application_status(sender, instance, created, **kwargs):
    user = instance.user

    if created and user.account_type == AccountType.BUYER:
        user.account_type = AccountType.PENDING_SELLER
        user.save(update_fields=["account_type"])
    elif not created:
        if instance.status == ApplicationStatus.APPROVED:
            user.account_type = AccountType.SELLER
            user.save(update_fields=["account_type"])
        elif instance.status == ApplicationStatus.REJECTED:
            user.account_type = AccountType.REJECTED_SELLER
            user.save(update_fields=["account_type"])
