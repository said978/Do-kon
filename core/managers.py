from django.db import models


class TenantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def for_company(self, company):
        if company:
            return self.get_queryset().filter(company=company)
        return self.none()


class TenantManagerViaBranch(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def for_company(self, company):
        if company:
            return self.get_queryset().filter(branch__company=company)
        return self.none()
