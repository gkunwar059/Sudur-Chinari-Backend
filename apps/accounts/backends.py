import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()
NEPALI_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if not username:
            return None
            
        username_str = str(username).strip().translate(NEPALI_DIGITS)
        cleaned_digits = re.sub(r'[\s\-\(\)]', '', username_str)
        
        phone_10 = cleaned_digits
        if phone_10.startswith('+977'):
            phone_10 = phone_10[4:]
        elif phone_10.startswith('977') and len(phone_10) == 13:
            phone_10 = phone_10[3:]

        try:
            # Allow login with username, email, or phone number (with or without +977)
            q_filter = (
                Q(username__iexact=username_str) |
                Q(email__iexact=username_str) |
                Q(profile__phone=username_str)
            )
            if cleaned_digits and cleaned_digits != username_str:
                q_filter |= Q(profile__phone=cleaned_digits)
            if phone_10 and phone_10 != username_str and phone_10 != cleaned_digits:
                q_filter |= Q(profile__phone=phone_10)
                
            user = User.objects.filter(q_filter).first()
            if not user:
                return None
        except Exception:
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
