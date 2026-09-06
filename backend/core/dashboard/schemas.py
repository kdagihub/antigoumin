from datetime import datetime

from ninja import Schema


class DashboardStatSchema(Schema):
    key: str
    value: int


class DashboardActivitySchema(Schema):
    type: str
    label: str
    occurred_at: datetime
    route: str


class DashboardNextActionSchema(Schema):
    code: str
    title: str
    description: str
    route: str


class DashboardSummarySchema(Schema):
    stats: list[DashboardStatSchema]
    activity: list[DashboardActivitySchema]
    next_action: DashboardNextActionSchema | None = None
