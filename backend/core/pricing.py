from enum import StrEnum


class ServiceType(StrEnum):
    VERIFICATION = "VERIFICATION"
    DECLARATION = "DECLARATION"
    TRANSPARENCY_REQUEST = "TRANSPARENCY_REQUEST"
    ALLIANCE_VIP = "ALLIANCE_VIP"


SERVICE_PRICES: dict[ServiceType, int] = {
    ServiceType.VERIFICATION: 200,
    ServiceType.DECLARATION: 300,
    ServiceType.TRANSPARENCY_REQUEST: 550,
    ServiceType.ALLIANCE_VIP: 1200,
}

SERVICE_CATALOG = [
    {
        "code": ServiceType.VERIFICATION,
        "label": "Vérification",
        "price_fcfa": SERVICE_PRICES[ServiceType.VERIFICATION],
        "billing": "per_action",
        "description": "Consultez un statut certifié uniquement si son titulaire l'a rendu consultable.",
    },
    {
        "code": ServiceType.DECLARATION,
        "label": "Déclaration",
        "price_fcfa": SERVICE_PRICES[ServiceType.DECLARATION],
        "billing": "per_action",
        "description": "Officialisez votre statut amoureux via double validation OTP.",
    },
    {
        "code": ServiceType.TRANSPARENCY_REQUEST,
        "label": "Demande de Transparence",
        "price_fcfa": SERVICE_PRICES[ServiceType.TRANSPARENCY_REQUEST],
        "billing": "per_action",
        "description": "Invitation officielle, identifiable et volontaire à clarifier son statut.",
    },
    {
        "code": ServiceType.ALLIANCE_VIP,
        "label": "Alliance Digitale VIP",
        "price_fcfa": SERVICE_PRICES[ServiceType.ALLIANCE_VIP],
        "billing": "monthly",
        "description": "Badge optionnel, forfait mensuel et notification neutre de fin d'Alliance.",
    },
]
