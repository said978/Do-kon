from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import AuditLog


def get_company(request):
    return getattr(request, 'company', None)


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', default='System')

    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'model_name', 'object_id', 'object_repr',
                  'changes', 'ip_address', 'username', 'created_at']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_list(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    logs = AuditLog.objects.filter(company=company)

    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)

    model_name = request.GET.get('model')
    if model_name:
        logs = logs.filter(model_name=model_name)

    logs = logs[:100]

    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)
