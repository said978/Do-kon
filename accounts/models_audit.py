from django.db import models
from accounts.models import Company, User


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
        return f"[{self.action}] {self.model_name} #{self.object_id} by {self.user}"
