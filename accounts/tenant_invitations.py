from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Company, Branch

User = get_user_model()


def get_company(request):
    return getattr(request, 'company', None)


class InvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['ADMIN', 'CASHIER', 'VIEWER'])
    branch_id = serializers.IntegerField(required=False, allow_null=True)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_invitation(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    serializer = InvitationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    email = serializer.validated_data['email']
    role = serializer.validated_data['role']
    branch_id = serializer.validated_data.get('branch_id')

    if User.objects.filter(email=email, company=company).exists():
        return Response({'detail': 'Bu email allaqachon taklif qilingan!'}, status=400)

    branch = None
    if branch_id:
        branch = Branch.objects.filter(id=branch_id, company=company).first()

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
            'company': company,
            'branch': branch,
            'role': role,
            'is_active': True,
        }
    )

    if created:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        invite_link = f"{request.scheme}://{request.get_host()}/invite/{uid}/{token}/"

        try:
            send_mail(
                subject=f"{company.name} ga taklif",
                message=f"Sizni {company.name} ga taklif qilishdi.\n\n"
                        f"Bosing: {invite_link}\n\n"
                        f"Lavozim: {role}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({
            'detail': f'{email} ga taklif yuborildi!',
            'invite_link': invite_link,
        })
    else:
        return Response({'detail': 'Foydalanuvchi allaqachon mavjud!'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_create_user(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role', 'CASHIER')
    branch_id = request.data.get('branch_id')

    if not username or not password:
        return Response({'detail': 'Login va parol kiritish shart!'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Bu login allaqachon mavjud!'}, status=400)

    branch = None
    if branch_id:
        branch = Branch.objects.filter(id=branch_id, company=company).first()

    user = User.objects.create_user(
        username=username,
        password=password,
        company=company,
        branch=branch,
        role=role,
    )

    return Response({
        'detail': f'{username} muvaffaqiyatli yaratildi!',
        'user_id': user.id,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_users(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    users = User.objects.filter(company=company)
    data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'branch': u.branch.name if u.branch else None,
        'is_active': u.is_active,
        'last_login': str(u.last_login) if u.last_login else None,
    } for u in users]
    return Response(data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    user = User.objects.filter(id=user_id, company=company).first()
    if not user:
        return Response({'detail': 'Foydalanuvchi topilmadi!'}, status=404)

    if user == request.user:
        return Response({'detail': 'O\'zingizni o\'chira olmaysiz!'}, status=400)

    user.delete()
    return Response({'detail': 'Foydalanuvchi o\'chirildi!'})
