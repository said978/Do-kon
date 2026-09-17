from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = "Xodimlar va Do'konlar"

    def ready(self):
        try:
            from accounts.models import User
            User._meta.get_field('username').verbose_name = "Login (Foydalanuvchi nomi)"
            User._meta.get_field('first_name').verbose_name = "Ism"
            User._meta.get_field('last_name').verbose_name = "Familiya"
            User._meta.get_field('email').verbose_name = "Email manzili"
            User._meta.get_field('is_active').verbose_name = "Faol holatda (Tizimga kira oladi)"
            User._meta.get_field('is_staff').verbose_name = "Xodim (Admin panelga kira oladi)"
            User._meta.get_field('is_superuser').verbose_name = "Bosh Admin (Cheksiz huquq)"
            User._meta.get_field('groups').verbose_name = "Guruhlar"
            User._meta.get_field('user_permissions').verbose_name = "Maxsus ruxsatnomalar"
            User._meta.get_field('last_login').verbose_name = "Oxirgi kirish vaqti"
            User._meta.get_field('date_joined').verbose_name = "Ro'yxatdan o'tgan sana"

            from django.contrib.auth.models import Group
            Group._meta.verbose_name = "Guruh"
            Group._meta.verbose_name_plural = "Guruhlar"
            Group._meta.get_field('name').verbose_name = "Guruh nomi"
            Group._meta.get_field('permissions').verbose_name = "huquqlar"
        except Exception:
            pass
