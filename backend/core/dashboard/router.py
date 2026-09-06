from ninja import Router

from core.auth.deps import jwt_auth

from .schemas import DashboardSummarySchema
from .services import build_dashboard_summary

router = Router(tags=["Dashboard"])


@router.get("/summary/", response=DashboardSummarySchema, auth=jwt_auth)
def dashboard_summary(request):
    summary = build_dashboard_summary(request.auth)
    return DashboardSummarySchema(
        stats=[
            {"key": item.key, "value": item.value}
            for item in summary["stats"]
        ],
        activity=[
            {
                "type": item.type,
                "label": item.label,
                "occurred_at": item.occurred_at,
                "route": item.route,
            }
            for item in summary["activity"]
        ],
        next_action=(
            {
                "code": summary["next_action"].code,
                "title": summary["next_action"].title,
                "description": summary["next_action"].description,
                "route": summary["next_action"].route,
            }
            if summary["next_action"]
            else None
        ),
    )
