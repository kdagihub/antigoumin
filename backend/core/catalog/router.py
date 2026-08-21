from ninja import Router

from core.pricing import SERVICE_CATALOG

from .schemas import ServiceCatalogItemSchema, ServiceCatalogSchema

router = Router(tags=["Catalogue"])


@router.get("/", response=ServiceCatalogSchema)
def get_catalog(request):
    return {
        "currency": "FCFA",
        "services": [ServiceCatalogItemSchema(**item) for item in SERVICE_CATALOG],
    }
