import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if not username:
            return None
            
        username_str = str(username).strip()
        cleaned_digits = re.sub(r'[\s\-\(\)]', '', username_str)
        
        try:
            # Allow login with username, email, or phone number
            q_filter = (
                Q(username__iexact=username_str) |
                Q(email__iexact=username_str) |
                Q(profile__phone=username_str)
            )
            if cleaned_digits and cleaned_digits != username_str:
                q_filter |= Q(profile__phone=cleaned_digits)
                
            user = User.objects.filter(q_filter).first()
            if not user:
                return None
        except Exception:
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
