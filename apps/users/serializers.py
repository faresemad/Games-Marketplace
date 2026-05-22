from django.conf import settings

from rest_framework import serializers

from apps.users.models import CustomUser, EmailHistory, SellerApplication


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "public_id",
            "email",
            "first_name",
            "last_name",
            "username",
            "avatar",
            "bio",
            "date_of_birth",
            "country",
            "phone_number",
            "is_verified",
            "balance",
            "account_type",
            "date_joined",
        ]
        read_only_fields = [
            "public_id",
            "email",
            "is_verified",
            "balance",
            "account_type",
            "date_joined",
        ]

    def get_avatar(self, obj):
        if obj.avatar:
            url = obj.avatar.url
            base = getattr(settings, "BASE_URL", None)
            if base:
                return f'{base.rstrip("/")}{url}'
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["avatar"]

    def get_avatar(self, obj):
        if obj.avatar:
            url = obj.avatar.url
            base = getattr(settings, "BASE_URL", None)
            if base:
                return f'{base.rstrip("/")}{url}'
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "public_id",
            "email",
            "first_name",
            "last_name",
            "username",
            "avatar",
            "bio",
            "is_verified",
            "is_active",
            "account_type",
            "date_joined",
            "last_login",
        ]
        read_only_fields = fields


class EmailHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailHistory
        fields = ["email", "changed_at"]


class SellerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerApplication
        fields = [
            "id",
            "front_id_image",
            "back_id_image",
            "selfie_image",
            "status",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "rejection_reason", "created_at", "updated_at"]


class SellerApplicationListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_public_id = serializers.UUIDField(source="user.public_id", read_only=True)

    class Meta:
        model = SellerApplication
        fields = [
            "id",
            "user_email",
            "user_public_id",
            "front_id_image",
            "back_id_image",
            "selfie_image",
            "status",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SellerApplicationActionSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
