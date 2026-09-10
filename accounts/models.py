from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Do'kon / Kompaniya nomi")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")

    # Obuna sozlamalari
    is_active = models.BooleanField(default=True, verbose_name="Obuna faolmi?")
    subscription_end_date = models.DateField(default=timezone.now, verbose_name="Obuna tugash sanasi")
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=200000,
                                      verbose_name="Oylik to'lov summasi")

    # Sozlamalar
    currency = models.CharField(max_length=10, default='UZS', verbose_name="Valyuta")
    timezone = models.CharField(max_length=50, default='Asia/Tashkent', verbose_name="Vaqt belgisi")
    language = models.CharField(max_length=10, default='uz', verbose_name="Til")

    created_at = models.DateTimeField(auto_now_add=True)

    def is_subscription_valid(self):
        return self.is_active and self.subscription_end_date >= timezone.now().date()

    def __str__(self):
        return self.name


class Branch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255, verbose_name="Filial nomi")

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CASHIER', 'Kassir'),
        ('VIEWER', 'Ko\'ruvchi'),
    )
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CASHIER')

    def __str__(self):
        return f"{self.username} ({self.role})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Yaratish'),
        ('UPDATE', 'Tahrirlash'),
        ('DELETE', 'O\'chirish'),
        ('LOGIN', 'Kirish'),
        ('LOGOUT', 'Chiqish'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Firma")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Foydalanuvchi")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Amal")
    model_name = models.CharField(max_length=100, verbose_name="Model")
    object_id = models.CharField(max_length=50, blank=True, verbose_name="Obyekt ID")
    object_repr = models.CharField(max_length=255, verbose_name="Obyekt nomi")
    changes = models.JSONField(default=dict, verbose_name="O'zgarishlar")
    ip_address = models.GenericIPAddressField(null=True, verbose_name="IP manzil")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqt")

    class Meta:
        verbose_name = "Audit log"
        verbose_name_plural = "Audit loglar"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.action}] {self.model_name} #{self.object_id}"