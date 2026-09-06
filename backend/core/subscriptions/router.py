from ninja import Router

from core.auth.deps import jwt_verified_auth

from .quotas import build_vip_quota_status
from .schemas import VipQuotaStatusSchema

router = Router(tags=["Abonnement"])


@router.get("/vip-quota/", response=VipQuotaStatusSchema, auth=jwt_verified_auth)
def vip_quota_status(request):
    status = build_vip_quota_status(request.auth)
    return VipQuotaStatusSchema(
        active=status["active"],
        period_start=status["period_start"],
        period_end=status["period_end"],
        quotas=[
            {
                "service_type": item.service_type,
                "limit": item.limit,
                "used": item.used,
                "remaining": item.remaining,
            }
            for item in status["quotas"]
        ],
    )
