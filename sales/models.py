from django.db import models
from accounts.models import Company, Branch, User
from inventory.models import Product
from core.managers import TenantManager, TenantManagerViaBranch


class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    name = models.CharField(max_length=255, verbose_name="Mijoz F.I.Sh")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    debt_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Qarzdorlik balansi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    objects = TenantManager()

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar bazasi"

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Sale(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Filial")
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mijoz")
    is_debt = models.BooleanField(default=False, verbose_name="Nasiya savdomi?")
    payment_method = models.CharField(max_length=20, default='CASH', verbose_name="To'lov turi")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Jami summa")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Jami tannarx")
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Sof foyda")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Savdo vaqti")

    objects = TenantManager()

    class Meta:
        verbose_name = "Savdo (Chek)"
        verbose_name_plural = "Savdolar (Xaridlar)"

    def __str__(self):
        return f"Chek #{self.id} - {self.total_amount} so'm"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name="Savdo (Chek)")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Tovar")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1.00, verbose_name="Sotilgan soni")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tannarxi")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sotilish narxi")

    class Meta:
        verbose_name = "Savdo tarkibidagi tovar"
        verbose_name_plural = "Savdo tarkibidagi tovarlar"

    def __str__(self):
        return f"{self.product.name} ({self.quantity} dona)"


class DebtPayment(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Naqd pul'),
        ('CARD', 'Plastik karta'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="Filial")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments', verbose_name="Mijoz")
    cashier = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Qabul qilgan kassir")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="To'langan summa")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='CASH', verbose_name="To'lov turi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="To'lov vaqti")

    objects = TenantManager()

    class Meta:
        verbose_name = "Qarz to'lovi"
        verbose_name_plural = "Qarz to'lovlari"

    def __str__(self):
        return f"{self.customer.name} - {self.amount} so'm ({self.get_payment_method_display()})"


class SaleReturn(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="Filial")
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='returns', verbose_name="Savdo (Chek)")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Tovar")
    cashier = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kassir")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Qaytarilgan soni")
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Qaytarilgan pul")
    reason = models.TextField(blank=True, null=True, verbose_name="Qaytarish sababi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qaytarilgan vaqt")

    objects = TenantManager()

    class Meta:
        verbose_name = "Tovar qaytarilishi"
        verbose_name_plural = "Tovarlarni qaytarish"

    def __str__(self):
        return f"Qaytarilgan #{self.id} - {self.product.name} ({self.quantity} dona)"