from rest_framework import serializers
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from .models import UserProfile
from .utils import validate_phone_number, generate_username_from_phone

User = get_user_model()

class CustomUserCreateSerializer(BaseUserCreateSerializer):
    phone = serializers.CharField(max_length=20, required=True, write_only=True)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
            'password',
            'phone',
            'first_name',
            'last_name',
            'email',
        )

    def validate_phone(self, value):
        cleaned = validate_phone_number(value)
        if UserProfile.objects.filter(phone=cleaned).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return cleaned

    def validate(self, attrs):
        if not attrs.get('username') or not str(attrs.get('username')).strip():
            phone = attrs.get('phone')
            if phone:
                attrs['username'] = generate_username_from_phone(phone)
            else:
                attrs['username'] = f"user_{User.objects.count() + 1}"

        user_attrs = {k: v for k, v in attrs.items() if k != 'phone'}
        user = User(**user_attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        user = super().create(validated_data)
        if phone:
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        profile = getattr(instance, 'profile', None)
        ret['phone'] = profile.phone if profile and profile.phone else ""
        return ret


class CustomUserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone')

    def get_phone(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone if profile and profile.phone else ""
