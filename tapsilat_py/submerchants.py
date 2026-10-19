from .models import (
    MarketplaceSubmerchantCreateRequest,
    SubmerchantCreateRequest,
    SubmerchantPayoutEventRequest,
    SubmerchantUpdateRequest,
)


class SubmerchantMixin:
    """Submerchant management, item payout events and marketplace seller creation"""

    def create_submerchant(self, request: SubmerchantCreateRequest) -> dict:
        """Create a submerchant; the response carries only code and message"""
        return self._make_request("POST", "/submerchants", json_payload=request.to_dict())

    def get_submerchant(self, submerchant_id: str) -> dict:
        endpoint = f"/submerchants/{self._path_id(submerchant_id, 'submerchant_id')}"
        return self._make_request("GET", endpoint)

    def list_submerchants(self, page: int = 1, per_page: int = 10) -> dict:
        """List submerchants; rows are returned under ``row``"""
        return self._make_request(
            "GET", "/submerchants", params={"page": page, "per_page": per_page}
        )

    def update_submerchant(self, submerchant_id: str, request: SubmerchantUpdateRequest) -> dict:
        """Replace the submerchant profile; send every field"""
        endpoint = f"/submerchants/{self._path_id(submerchant_id, 'submerchant_id')}"
        return self._make_request("PATCH", endpoint, json_payload=request.to_dict())

    def delete_submerchant(self, submerchant_id: str) -> dict:
        endpoint = f"/submerchants/{self._path_id(submerchant_id, 'submerchant_id')}"
        return self._make_request("DELETE", endpoint)

    def get_suborganization_by_submerchant(self, submerchant_id: str) -> dict:
        endpoint = f"/submerchants/{self._path_id(submerchant_id, 'submerchant_id')}/suborganization"
        return self._make_request("GET", endpoint)

    def record_submerchant_payout_event(self, request: SubmerchantPayoutEventRequest) -> dict:
        """Record an item business event; time gates, approval and settlement remain separate"""
        return self._make_request(
            "POST", "/submerchant-payout-events", json_payload=request.to_dict()
        )

    def create_marketplace_submerchant(self, request: MarketplaceSubmerchantCreateRequest) -> dict:
        """Create a logical marketplace seller; inspect ``provisionings`` for each VPOS account's readiness"""
        return self._make_request(
            "POST", "/submerchants", json_payload=request.to_dict(), version="v2"
        )
