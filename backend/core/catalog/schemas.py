from ninja import Schema


class ServiceCatalogItemSchema(Schema):
    code: str
    label: str
    price_fcfa: int
    billing: str
    description: str


class ServiceCatalogSchema(Schema):
    currency: str = "FCFA"
    services: list[ServiceCatalogItemSchema]
