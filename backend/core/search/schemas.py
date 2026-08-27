from ninja import Schema


class SearchResponseSchema(Schema):
    phone: str
    certified_status: str
    price_fcfa: int
