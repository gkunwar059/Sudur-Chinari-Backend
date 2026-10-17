from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile
from .utils import validate_phone_number, generate_username_from_phone

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone', 'user__email')

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True, help_text="10-digit mobile number starting with 98 or 97")

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        cleaned = validate_phone_number(phone)
        if UserProfile.objects.filter(phone=cleaned).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return cleaned

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username or not str(username).strip():
            phone = self.cleaned_data.get('phone')
            if phone:
                return generate_username_from_phone(phone)
            return f"user_{User.objects.count() + 1}"
        return username

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone = self.cleaned_data.get('phone')
        if commit:
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user


class CustomUserChangeForm(UserChangeForm):
    phone = forms.CharField(max_length=20, required=False, help_text="Mobile number associated with user")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile') and self.instance.profile:
            self.fields['phone'].initial = self.instance.profile.phone

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return ""
        cleaned = validate_phone_number(phone)
        existing = UserProfile.objects.filter(phone=cleaned).exclude(user=self.instance)
        if existing.exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone = self.cleaned_data.get('phone')
        if commit and phone:
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_phone', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'username', 'email', 'password', 'password_2'),
        }),
    )

    @admin.display(description="Phone Number", ordering='profile__phone')
    def get_phone(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone if profile and profile.phone else "-"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
