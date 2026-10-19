from typing import Optional

from .models import (
    VposCreateRequest,
    VposSubmerchantCreateRequest,
    VposSubmerchantUpdateRequest,
    VposUpdateRequest,
)


class VposMixin:
    """VPOS configurations, VPOS submerchants and acquirer lookups.

    Updates replace the stored configuration: read the record first and send
    every field back.
    """

    def list_vpos(
        self, page: int = 1, per_page: int = 10, suborganization_id: Optional[str] = None
    ) -> dict:
        params = {"page": page, "per_page": per_page}
        if suborganization_id:
            params["suborganization_id"] = suborganization_id
        return self._make_request("GET", "/vpos", params=params)

    def create_vpos(self, request: VposCreateRequest) -> dict:
        return self._make_request("POST", "/vpos", json_payload=request.to_dict())

    def get_vpos(self, vpos_id: str) -> dict:
        return self._make_request("GET", f"/vpos/{self._path_id(vpos_id, 'vpos_id')}")

    def update_vpos(self, vpos_id: str, request: VposUpdateRequest) -> dict:
        """Replace a VPOS configuration; fields left out are stored as empty or false"""
        endpoint = f"/vpos/{self._path_id(vpos_id, 'vpos_id')}"
        return self._make_request("PATCH", endpoint, json_payload=request.to_dict())

    def delete_vpos(self, vpos_id: str) -> dict:
        return self._make_request("DELETE", f"/vpos/{self._path_id(vpos_id, 'vpos_id')}")

    def list_vpos_acquirers(self) -> dict:
        return self._make_request("GET", "/vpos/acquirers")

    def list_card_schemes(self) -> dict:
        return self._make_request("GET", "/vpos/card-schemes")

    def list_vpos_acquirer_templates(self) -> dict:
        return self._make_request("GET", "/vpos/acquirer-templates")

    def list_vpos_submerchants(
        self,
        page: int = 1,
        per_page: int = 10,
        vpos_id: Optional[str] = None,
        external_reference_id: Optional[str] = None,
    ) -> dict:
        params = {"page": page, "per_page": per_page}
        if vpos_id:
            params["vpos_id"] = vpos_id
        if external_reference_id:
            params["external_reference_id"] = external_reference_id
        return self._make_request("GET", "/vpos-submerchant", params=params)

    def create_vpos_submerchant(self, request: VposSubmerchantCreateRequest) -> dict:
        return self._make_request("POST", "/vpos-submerchant", json_payload=request.to_dict())

    def get_vpos_submerchant(self, vpos_submerchant_id: str) -> dict:
        endpoint = f"/vpos-submerchant/{self._path_id(vpos_submerchant_id, 'vpos_submerchant_id')}"
        return self._make_request("GET", endpoint)

    def update_vpos_submerchant(
        self, vpos_submerchant_id: str, request: VposSubmerchantUpdateRequest
    ) -> dict:
        endpoint = f"/vpos-submerchant/{self._path_id(vpos_submerchant_id, 'vpos_submerchant_id')}"
        return self._make_request("PATCH", endpoint, json_payload=request.to_dict())

    def delete_vpos_submerchant(self, vpos_submerchant_id: str) -> dict:
        endpoint = f"/vpos-submerchant/{self._path_id(vpos_submerchant_id, 'vpos_submerchant_id')}"
        return self._make_request("DELETE", endpoint)
