import random
from django.db import models
from accounts.models import Company, Branch
from core.managers import TenantManager, TenantManagerViaBranch

class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Firma", null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="Kategoriya nomi")

    objects = TenantManager()

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Firma", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya")
    name = models.CharField(max_length=255, verbose_name="Tovar nomi")
    barcode = models.CharField(max_length=50, verbose_name="Shtrix-kod")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tannarxi (Kirish)")
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sotish narxi")

    objects = TenantManager()

    class Meta:
        verbose_name = "Tovar"
        verbose_name_plural = "Tovarlar (Mahsulotlar)"
        unique_together = ['company', 'barcode']

    def __str__(self):
        return f"{self.name} - {self.selling_price} so'm"


class Stock(models.Model):
    branch = models.ForeignKey('accounts.Branch', on_delete=models.CASCADE, verbose_name="Filial")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Tovar")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ombor qoldig'i")

    objects = TenantManagerViaBranch()

    class Meta:
        verbose_name = "Ombor qoldig'i"
        verbose_name_plural = "Ombor qoldiqlari"

    def __str__(self):
        return f"{self.branch.name} | {self.product.name}: {self.quantity} dona"