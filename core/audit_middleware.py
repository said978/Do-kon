import json
from django.utils.deprecation import MiddlewareMixin
from accounts.models import AuditLog


class AuditLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._audit_changes = {}

    def process_response(self, request, response):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response

        if not hasattr(request, 'company') or not request.company:
            return response

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return response

        action_map = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }

        action = action_map.get(request.method)
        if not action:
            return response

        model_name = request.path.split('/')[-2] if len(request.path.split('/')) > 2 else 'unknown'

        try:
            AuditLog.objects.create(
                company=request.company,
                user=request.user,
                action=action,
                model_name=model_name,
                object_repr=request.path,
                changes={'path': request.path, 'method': request.method},
                ip_address=self.get_client_ip(request),
            )
        except Exception:
            pass

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
