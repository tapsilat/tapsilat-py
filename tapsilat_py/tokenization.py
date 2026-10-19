from .models import CardTokenizeRequest


class TokenizationMixin:
    """Card tokenization and saved cards"""

    def tokenize_card(self, request: CardTokenizeRequest) -> dict:
        """Tokenize a card; returns 3D secure form details when verification is required"""
        return self._make_request(
            "POST", "/tokenization/card/tokenize", json_payload=request.to_dict()
        )

    def list_saved_cards(self, page: int = 1, per_page: int = 10) -> dict:
        return self._make_request(
            "GET", "/tokenization/card/list", params={"page": page, "per_page": per_page}
        )

    def delete_saved_card(self, card_id: str) -> dict:
        return self._make_request(
            "DELETE", f"/tokenization/card/{self._path_id(card_id, 'card_id')}"
        )
