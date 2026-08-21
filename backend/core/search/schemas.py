from ninja import Schema


class SearchResponseSchema(Schema):
    class Config:
        json_schema_extra = {
            "description": (
                "Réponse volontairement minimale : elle ne permet pas de distinguer "
                "un numéro absent d'un numéro non consultable."
            )
        }

    phone: str
    certified_status: str
    price_fcfa: int
