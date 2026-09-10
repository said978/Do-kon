import time
from django.core.cache import cache
from rest_framework.response import Response


class TenantRateThrottle:
    RATE_LIMIT = 100
    WINDOW = 60

    def __init__(self, request):
        self.request = request
        self.company = getattr(request, 'company', None)

    def allow_request(self):
        if not self.company:
            return True

        cache_key = f'throttle_{self.company.id}_{int(time.time() // self.WINDOW)}'
        current = cache.get(cache_key, 0)

        if current >= self.RATE_LIMIT:
            return False

        cache.set(cache_key, current + 1, self.WINDOW)
        return True

    def get_retry_after(self):
        return self.WINDOW - (int(time.time()) % self.WINDOW)
