from accounts.models import Company


def company_context(request):
    try:
        if request.user.is_authenticated and hasattr(request.user, 'company') and request.user.company:
            company_name = request.user.company.name
        else:
            company = Company.objects.first()
            company_name = company.name if company else "DO'KON"
    except Exception:
        company_name = "DO'KON"
    return {
        'company_name': company_name
    }
