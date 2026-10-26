from typing import Any, Dict, List, Optional, Union

import hmac
import re
import time
import warnings
import hashlib
from urllib.parse import quote, urlsplit, urlunsplit

import requests

from .elements import ElementsMixin
from .exceptions import APIException
from .models import (
    OrderAccountingRequest,
    OrderChargeRequest,
    CreateOrganizationCurrencyPayload,
    OrderCreateDTO,
    OrderPaymentTermCreateDTO,
    OrderPostAuthRequest,
    OrderResponse,
    OrderTermRefundRequest,
    RefundOrderDTO,
    CancelOrderDTO,
    RefundAllOrderDTO,
    OrderPaymentDetailDTO,
    TerminateRequest,
    OrderRelatedReferenceDTO,
    OrderPaymentTermDeleteDTO,
    OrderPaymentTermUpdateDTO,
    OrgCreateBusinessRequest,
    GetUserLimitRequest,
    SetLimitUserRequest,
    GetVposRequest,
    OrgCreateUserReq,
    OrgUserVerifyReq,
    OrgUserMobileVerifyReq,
    OrderManualCallbackDTO,
    SubscriptionCancelRequest,
    SubscriptionCreateRequest,
    SubscriptionGetRequest,
    SubscriptionRedirectRequest,
    AddBasketItemRequest,
    RemoveBasketItemRequest,
    UpdateBasketItemRequest,
    CallbackURLDTO,
    CardInstallmentsRequest,
    GetOrderPaymentsRequest,
    InstallmentTableRequest,
    OrgUserTokenCreateRequest,
    SubmerchantPaymentAction,
    SubmerchantPaymentItemUpdate,
    OrderPaymentOptionsUpdateDTO,
    SplitOrderItemPaymentDTO,
    OrderOIPDTO,
    OrgUserTokenCreateReq,
    FileResponse,
)
from .marketplace import MarketplaceMixin
from .submerchants import SubmerchantMixin
from .tokenization import TokenizationMixin
from .validators import validate_gsm_number, validate_installments
from .vpos import VposMixin
from .webhooks import WEBHOOK_TOLERANCE

_UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_SIGNATURE_TIMESTAMP_PATTERN = re.compile(r"[0-9]+")


class TapsilatAPI(
    SubmerchantMixin, VposMixin, TokenizationMixin, MarketplaceMixin, ElementsMixin
):
    def __init__(
        self,
        api_key: str = "",
        timeout: int = 10,
        base_url: str = "https://panel.tapsilat.dev/api/v1",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._currency_ids_by_unit: Optional[Dict[str, str]] = None

    def _get_headers(self):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        raw_response: bool = False,
    ) -> Any:
        base_url = self._versioned_base_url(version) if version else self.base_url
        url = f"{base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=json_payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise APIException(0, -1, str(e)) from e

        status_code = getattr(response, "status_code", 200)
        if raw_response and not (isinstance(status_code, int) and status_code >= 400):
            filename = "download"
            disposition = response.headers.get("Content-Disposition")
            if isinstance(disposition, str) and "filename=" in disposition:
                filename = disposition.split("filename=")[-1].strip('"')
            return FileResponse(response.content, filename)
        return self._parse_response(response)

    def _parse_response(self, response: Any) -> Any:
        status_code = getattr(response, "status_code", 200)
        if not isinstance(status_code, int):
            status_code = 200
        content = response.content or b""
        raw_body = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)

        if status_code >= 400:
            raise self._api_error(response, status_code, raw_body)

        if not raw_body.strip():
            return {}

        content_type = response.headers.get("Content-Type", "") if hasattr(response, "headers") else ""
        if not isinstance(content_type, str):
            content_type = ""
        # A deployment serving the panel UI answers unknown routes with its HTML page and status 200
        if "text/html" in content_type.lower() or raw_body.lstrip().startswith("<"):
            raise APIException(
                status_code,
                -1,
                f"unexpected non-JSON response (Content-Type {content_type!r}); "
                "check that the endpoint URL and route are correct",
                raw_body=raw_body,
            )

        try:
            return response.json()
        except ValueError:
            error = APIException(status_code, -1, "failed to parse response body", raw_body=raw_body)
        raise error

    @staticmethod
    def _api_error(response: Any, status_code: int, raw_body: str) -> APIException:
        reason = getattr(response, "reason", "") or "HTTP error with no content"
        if not raw_body.strip():
            return APIException(status_code, -1, reason, raw_body=raw_body)
        try:
            body = response.json()
        except ValueError:
            return APIException(status_code, -1, raw_body, raw_body=raw_body)
        if not isinstance(body, dict):
            return APIException(status_code, -1, raw_body, raw_body=raw_body)

        message = body.get("message")
        code = body.get("code", -1)
        retryable = False
        nested = body.get("error")
        if isinstance(nested, dict):
            # Elements routes nest the error: {"error": {"code": ..., "message": ..., "retryable": ...}}
            if "code" not in body and "code" in nested:
                code = nested["code"]
            if message is None:
                message = nested.get("message", raw_body)
            retryable = nested.get("retryable") is True
        elif message is None:
            message = body.get("error", raw_body)
        status = body.get("status")
        errors = body.get("errors")
        return APIException(
            status_code,
            code,
            str(message),
            status=str(status) if status is not None else None,
            errors=errors if isinstance(errors, dict) else None,
            raw_body=raw_body,
            retryable=retryable,
        )

    def _versioned_base_url(self, version: str) -> str:
        """Returns the base URL for another API version, replacing a trailing /api/vN segment"""
        parsed = urlsplit(self.base_url)
        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) >= 2 and segments[-2] == "api" and segments[-1].startswith("v"):
            segments[-1] = version
        else:
            segments += ["api", version]
        return urlunsplit(parsed._replace(path="/" + "/".join(segments))).rstrip("/")

    @staticmethod
    def _path_id(value: str, name: str = "id") -> str:
        """URL-encodes a path identifier, rejecting empty values"""
        if not value:
            raise ValueError(f"{name} is required")
        return quote(str(value), safe="")

    def create_order(self, order: OrderCreateDTO) -> OrderResponse:
        endpoint = "/order/create"

        # Validate GSM number if provided
        if order.buyer and order.buyer.gsm_number:
            order.buyer.gsm_number = validate_gsm_number(order.buyer.gsm_number)

        # Validate installments if provided as string (convert from legacy format)
        if hasattr(order, "enabled_installments") and order.enabled_installments:
            order.enabled_installments = str(order.enabled_installments)  # type: ignore
            order.enabled_installments = (
                order.enabled_installments.replace("[", "")
                .replace("]", "")
                .replace(" ", "")
            )  # type: ignore
            order.enabled_installments = validate_installments(
                order.enabled_installments
            )  # type: ignore

        payload = order.to_dict()
        response_data = self._make_request("POST", endpoint, json_payload=payload)
        response = OrderResponse(response_data)

        # The create response has no checkout URL; read it from the order, ignoring failures
        if response.reference_id and not response.checkout_url:
            try:
                checkout_url = self.get_order(response.reference_id).checkout_url
            except (APIException, ValueError):
                checkout_url = None
            if checkout_url:
                response["checkout_url"] = checkout_url

        return response

    def order_accounting(self, request: OrderAccountingRequest) -> dict:
        endpoint = "/order/accounting"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def order_postauth(self, request: OrderPostAuthRequest) -> dict:
        endpoint = "/order/postauth"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_system_order_statuses(self) -> dict:
        endpoint = "/system/order-statuses"
        return self._make_request("GET", endpoint)

    def get_system_basket_item_types(self) -> dict:
        endpoint = "/system/basket-item-types"
        return self._make_request("GET", endpoint)

    def get_system_error_codes(self) -> dict:
        endpoint = "/system/error-codes"
        return self._make_request("GET", endpoint)

    def get_system_payment_term_statuses(self) -> dict:
        endpoint = "/system/payment-term-statuses"
        return self._make_request("GET", endpoint)

    def get_system_product_types(self) -> dict:
        endpoint = "/system/product-types"
        return self._make_request("GET", endpoint)

    def get_system_shortcut_types(self) -> dict:
        endpoint = "/system/shortcut-types"
        return self._make_request("GET", endpoint)

    def get_system_transaction_payment_types(self) -> dict:
        endpoint = "/system/transaction-payment-types"
        return self._make_request("GET", endpoint)

    def get_system_transaction_purposes(self) -> dict:
        endpoint = "/system/transaction-purposes"
        return self._make_request("GET", endpoint)

    def get_system_transaction_statuses(self) -> dict:
        endpoint = "/system/transaction-statuses"
        return self._make_request("GET", endpoint)

    def get_order(self, reference_id: str) -> OrderResponse:
        endpoint = f"/order/{quote(reference_id, safe='')}"
        response = self._make_request("GET", endpoint)
        return OrderResponse(response)

    def get_order_by_conversation_id(self, conversation_id: str) -> OrderResponse:
        endpoint = f"/order/conversation/{quote(conversation_id, safe='')}"
        response = self._make_request("GET", endpoint)
        return OrderResponse(response)

    def get_order_list(
        self,
        page: int = 1,
        per_page: int = 10,
        start_date: str = "",
        end_date: str = "",
        organization_id: str = "",
        related_reference_id: str = "",
        conversation_id: str = "",
        buyer_id: str = "",
        status: Optional[int] = None,
    ) -> dict:
        endpoint = "/order/list"
        raw_params = {
            "page": page,
            "per_page": per_page,
            "start_date": start_date,
            "end_date": end_date,
            "organization_id": organization_id,
            "related_reference_id": related_reference_id,
            "conversation_id": conversation_id,
            "buyer_id": buyer_id,
            "status": status,
        }
        params = {k: v for k, v in raw_params.items() if v not in ("", None)}
        return self._make_request("GET", endpoint, params=params)

    def get_order_submerchants(self, page: int = 1, per_page: int = 10) -> dict:
        endpoint = "/order/submerchants"
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", endpoint, params=params)

    def get_checkout_url(self, reference_id: str) -> str:
        response = self.get_order(reference_id)
        return response.checkout_url

    def cancel_order(self, request: CancelOrderDTO) -> dict:
        endpoint = "/order/cancel"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def refund_order(self, refund_data: RefundOrderDTO) -> dict:
        endpoint = "/order/refund"
        payload = refund_data.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def refund_all_order(self, request: RefundAllOrderDTO) -> dict:
        endpoint = "/order/refund-all"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_order_payment_details(self, request: OrderPaymentDetailDTO) -> dict:
        endpoint = "/order/payment-details"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_order_payment_details_by_id(self, reference_id: str) -> dict:
        endpoint = f"/order/{quote(reference_id, safe='')}/payment-details"
        return self._make_request("GET", endpoint)

    def get_order_payment_details_by_conversation_id(self, conversation_id: str) -> dict:
        """Get an order's payment details looked up by its conversation ID"""
        return self._make_request(
            "POST", "/order/payment-details", json_payload={"conversation_id": conversation_id}
        )

    def get_order_status(self, reference_id: str) -> dict:
        endpoint = f"/order/{quote(reference_id, safe='')}/status"
        return self._make_request("GET", endpoint)

    def get_order_transactions(self, reference_id: str) -> List[dict]:
        """Get the order's transactions; the list is empty when there are none"""
        endpoint = f"/order/{quote(reference_id, safe='')}/transactions"
        return self._make_request("GET", endpoint) or []

    def get_order_payments(self, request: GetOrderPaymentsRequest) -> dict:
        """List the payments made against an order with commission totals"""
        return self._make_request("POST", "/order/payments", json_payload=request.to_dict())

    def charge_order(self, request: OrderChargeRequest) -> dict:
        """Charge an order; inspect ``isSuccess``, since the request can succeed while the charge fails"""
        return self._make_request("POST", "/order/charge", json_payload=request.to_dict())

    def approve_submerchant_payment(self, request: SubmerchantPaymentAction) -> dict:
        """Submit the stored item payout to the approval workflow.

        Deprecated: use ``approve_marketplace_payouts`` with explicit payout IDs.
        """
        return self._make_request(
            "POST", "/submerchants/payment/approve", json_payload=request.to_dict()
        )

    def disapprove_submerchant_payment(self, request: SubmerchantPaymentAction) -> dict:
        """Withdraw a stored payout's approval; inspect ``status`` and keep ``operation_id``"""
        return self._make_request(
            "POST", "/submerchants/payment/disapprove", json_payload=request.to_dict()
        )

    def update_submerchant_payment_item(self, request: SubmerchantPaymentItemUpdate) -> dict:
        """Change a stored payout allocation; inspect ``status`` and keep ``operation_id``"""
        return self._make_request(
            "PUT", "/submerchants/payment/item", json_payload=request.to_dict()
        )

    def get_card_installments(self, request: CardInstallmentsRequest) -> dict:
        """Get installment options and commission rates for a card BIN and amount"""
        return self._make_request("GET", "/card/installments", params=request.to_params())

    def get_installment_table(self, request: InstallmentTableRequest) -> dict:
        """Get installment options grouped by bank card program, with an interest-free flag per row"""
        return self._make_request("GET", "/card/installment-table", params=request.to_params())

    def create_order_term(self, term: OrderPaymentTermCreateDTO) -> dict:
        endpoint = "/order/term"
        payload = term.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def delete_order_term(
        self,
        request: Union[OrderPaymentTermDeleteDTO, str],
        term_reference_id: Optional[str] = None,
    ) -> dict:
        """Delete a payment term; pass a DTO or the order ID and term reference ID"""
        if isinstance(request, str):
            request = OrderPaymentTermDeleteDTO(order_id=request, term_reference_id=term_reference_id or "")
        endpoint = "/order/term"
        payload = request.to_dict()
        return self._make_request("DELETE", endpoint, json_payload=payload)

    def update_order_term(self, request: OrderPaymentTermUpdateDTO) -> dict:
        endpoint = "/order/term"
        payload = request.to_dict()
        return self._make_request("PATCH", endpoint, json_payload=payload)

    def get_order_term(self, term_reference_id: str) -> dict:
        endpoint = "/order/term"
        params = {"term_reference_id": term_reference_id}
        return self._make_request("GET", endpoint, params=params)

    def refund_order_term(self, term: OrderTermRefundRequest) -> dict:
        if not term.reference_id:
            raise ValueError("reference_id (the order's reference ID) is required to refund a term")
        endpoint = "/order/term/refund"
        payload = term.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def terminate_order(self, request: TerminateRequest) -> dict:
        endpoint = "/order/terminate"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def manual_callback(self, request: OrderManualCallbackDTO) -> dict:
        endpoint = "/order/callback"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def related_update(self, request: OrderRelatedReferenceDTO) -> dict:
        endpoint = "/order/releated"
        payload = request.to_dict()
        return self._make_request("PATCH", endpoint, json_payload=payload)

    def order_terminate(self, reference_id: str) -> dict:
        """Terminate an order by reference ID"""
        return self.terminate_order(TerminateRequest(reference_id=reference_id))

    def order_manual_callback(self, reference_id: str, conversation_id: Optional[str] = None) -> dict:
        """Ask the server to resend the order's callback"""
        return self.manual_callback(
            OrderManualCallbackDTO(reference_id=reference_id, conversation_id=conversation_id)
        )

    def order_related_update(self, reference_id: str, related_reference_id: str) -> dict:
        """Link an order to a related reference ID"""
        return self.related_update(
            OrderRelatedReferenceDTO(reference_id=reference_id, related_reference_id=related_reference_id)
        )

    def update_payment_options(self, request: OrderPaymentOptionsUpdateDTO) -> dict:
        endpoint = "/order/payment-options"
        payload = request.to_dict()
        return self._make_request("PATCH", endpoint, json_payload=payload)

    def split_order_item_payment(self, request: SplitOrderItemPaymentDTO) -> dict:
        endpoint = "/order/split"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def order_callback(self, id: str) -> dict:
        endpoint = f"/orders/{id}/callback"
        return self._make_request("GET", endpoint)

    def order_vpos_query(self, id: str) -> dict:
        endpoint = f"/orders/{id}/vpos-query"
        return self._make_request("GET", endpoint)

    def add_basket_item(self, request: AddBasketItemRequest) -> dict:
        endpoint = "/order/basket-item"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def remove_basket_item(self, request: RemoveBasketItemRequest) -> dict:
        endpoint = "/order/basket-item"
        payload = request.to_dict()
        return self._make_request("DELETE", endpoint, json_payload=payload)

    def update_basket_item(self, request: UpdateBasketItemRequest) -> dict:
        endpoint = "/order/basket-item"
        payload = request.to_dict()
        return self._make_request("PATCH", endpoint, json_payload=payload)

    def get_orders(
        self, page: str = "1", per_page: str = "10", buyer_id: str = ""
    ) -> dict:
        """DEPRECATED: Use get_order_list instead. Get orders with pagination and optional buyer filter"""
        return self.get_order_list(page=int(page), per_page=int(per_page), buyer_id=buyer_id)

    def get_order_pdf(self, id: str) -> FileResponse:
        endpoint = f"/order/{self._path_id(id, 'id')}/export/pdf"
        return self._make_request("GET", endpoint, raw_response=True)

    def get_order_excel(self, id: str) -> FileResponse:
        endpoint = f"/order/{self._path_id(id, 'id')}/export/excel"
        return self._make_request("GET", endpoint, raw_response=True)

    def create_order_refund_request(self, request: RefundOrderDTO) -> dict:
        endpoint = "/order/refund-request"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def add_order_oip(self, request: OrderOIPDTO) -> dict:
        endpoint = "/order/oip"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_organization_settings(self) -> dict:
        """Get organization settings"""
        endpoint = "/organization/settings"
        return self._make_request("GET", endpoint)

    def get_organization_callback(self) -> dict:
        """Get organization webhook callback URLs"""
        endpoint = "/organization/callback"
        return self._make_request("GET", endpoint)

    def update_organization_callback(self, request: CallbackURLDTO) -> dict:
        """Update organization webhook callback URLs"""
        endpoint = "/organization/callback"
        payload = request.to_dict()
        return self._make_request("PATCH", endpoint, json_payload=payload)

    def create_organization_business(self, request: OrgCreateBusinessRequest) -> dict:
        """Create Business Entity"""
        endpoint = "/organization/business/create"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_organization_currencies(self) -> dict:
        """List Supported Currencies"""
        endpoint = "/organization/currencies"
        return self._make_request("GET", endpoint)

    def get_organization_limit_user(self, request: GetUserLimitRequest) -> dict:
        """Get User Limits Configuration.

        Deprecated: the API has no organization user limit route, so this call always fails.
        """
        warnings.warn(
            "get_organization_limit_user calls a route the API does not provide",
            DeprecationWarning,
            stacklevel=2,
        )
        endpoint = "/organization/limit/user"
        payload = request.to_dict()
        return self._make_request("GET", endpoint, json_payload=payload)

    def set_organization_limit_user(self, request: SetLimitUserRequest) -> dict:
        """Set Limit To User.

        Deprecated: the API has no organization user limit route, so this call always fails.
        """
        warnings.warn(
            "set_organization_limit_user calls a route the API does not provide",
            DeprecationWarning,
            stacklevel=2,
        )
        endpoint = "/organization/limit/user"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_organization_limits(self, organization_id: Optional[str] = None) -> dict:
        """Get an organization's transaction limits.

        Calling it without ``organization_id`` is deprecated: the API has no
        ``/organization/limits`` route, so that request always fails.
        """
        if not organization_id:
            warnings.warn(
                "get_organization_limits without organization_id calls a route the API does not provide; "
                "pass the organization ID",
                DeprecationWarning,
                stacklevel=2,
            )
            return self._make_request("GET", "/organization/limits")
        endpoint = f"/organization/{quote(organization_id, safe='')}/limits"
        return self._make_request("GET", endpoint)

    def list_organization_vpos(self, request: GetVposRequest) -> dict:
        """List Virtual POS Terminals"""
        endpoint = "/organization/list-vpos"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_organization_meta(self, name: str) -> dict:
        """Get Organization Metadata"""
        endpoint = f"/organization/metas/{quote(name, safe='')}"
        return self._make_request("GET", endpoint)

    def get_organization_scopes(self) -> dict:
        """Get Organization Permissions"""
        endpoint = "/organization/scopes"
        return self._make_request("GET", endpoint)

    def get_organization_suborganizations(
        self, page: int = 1, per_page: int = 10
    ) -> dict:
        """List Sub-Organizations"""
        endpoint = "/organization/suborganizations"
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", endpoint, params=params)

    def get_suborganization(self, suborganization_id: str) -> dict:
        """Get a suborganization's detail"""
        endpoint = f"/organization/suborganizations/{self._path_id(suborganization_id, 'suborganization_id')}"
        return self._make_request("GET", endpoint)

    def get_submerchant_by_suborganization(self, suborganization_id: str) -> dict:
        endpoint = (
            f"/organization/suborganizations/{self._path_id(suborganization_id, 'suborganization_id')}"
            "/submerchant"
        )
        return self._make_request("GET", endpoint)

    def list_organization_currency_presets(self) -> dict:
        return self._make_request("GET", "/organization/currency-presets")

    def get_organization_suborganization_details(self, id: str) -> dict:
        """Get Sub-Organization Details"""
        return self.get_suborganization(id)

    def get_organization_suborganization_submerchants(self, id: str) -> dict:
        """Get Sub-Organization Submerchants"""
        return self.get_submerchant_by_suborganization(id)

    def get_organization_currency_presets(self) -> dict:
        """Get Organization Currency Presets"""
        return self.list_organization_currency_presets()

    def create_organization_currency(self, currency_code: str) -> dict:
        """Add a currency to the organization by ISO code, for example USD"""
        response = self._make_request(
            "POST",
            "/organization/currencies",
            json_payload={"currency_code": currency_code.strip().upper()},
        )
        self._currency_ids_by_unit = None
        return response

    def create_organization_user_token(
        self, request: Union[OrgUserTokenCreateRequest, OrgUserTokenCreateReq]
    ) -> dict:
        """Create an access token for an organization user; ``expire`` is in minutes"""
        return self._make_request(
            "POST", "/organization/user/token", json_payload=request.to_dict()
        )

    def resolve_currency_id(self, ref: str) -> str:
        """Return the organization currency UUID for a unit such as "TRY"; a UUID is returned unchanged.

        Most endpoints accept units directly, so this is only needed where a UUID is required.
        """
        ref = (ref or "").strip()
        if not ref:
            raise ValueError("currency_id is required")
        if _UUID_PATTERN.match(ref):
            return ref
        if self._currency_ids_by_unit is None:
            response = self.get_organization_currencies() or {}
            self._currency_ids_by_unit = {
                (currency.get("currency_unit") or "").strip().upper(): currency.get("id")
                for currency in response.get("currencies") or []
                if currency.get("currency_unit") and currency.get("id")
            }
        currency_id = self._currency_ids_by_unit.get(ref.upper())
        if not currency_id:
            raise ValueError(
                f"unknown currency reference {ref!r}; use a currency UUID or organization currency unit"
            )
        return currency_id

    def create_organization_user(self, request: OrgCreateUserReq) -> dict:
        """Create Organization User"""
        endpoint = "/organization/user/create"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def verify_organization_user(self, request: OrgUserVerifyReq) -> dict:
        """Verify User"""
        endpoint = "/organization/user/verify"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def verify_organization_user_mobile(self, request: OrgUserMobileVerifyReq) -> dict:
        """Verify User Mobile"""
        endpoint = "/organization/user/verify-mobile"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    # Subscription methods
    def get_subscription(self, request: SubscriptionGetRequest) -> dict:
        """Get subscription details by reference_id or external_reference_id"""
        endpoint = "/subscription"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def cancel_subscription(self, request: SubscriptionCancelRequest) -> dict:
        """Cancel a subscription by reference_id or external_reference_id"""
        endpoint = "/subscription/cancel"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def create_subscription(self, request: SubscriptionCreateRequest) -> dict:
        """Create a new subscription"""
        endpoint = "/subscription/create"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def list_subscriptions(self, page: int = 1, per_page: int = 10) -> dict:
        """List all subscriptions with pagination"""
        endpoint = "/subscription/list"
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", endpoint, params=params)

    def redirect_subscription(self, request: SubscriptionRedirectRequest) -> dict:
        """Get redirect URL for a subscription"""
        endpoint = "/subscription/redirect"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)


    def create_org_currency(self, payload: CreateOrganizationCurrencyPayload) -> Dict[str, Any]:
        return self.create_organization_currency(payload.currency_code)

    def get_org_metadata(self, name: str) -> Dict[str, Any]:
        endpoint = f"/organization/metas/{quote(name, safe='')}"
        return self._make_request("GET", endpoint)

    def get_org_partners(self) -> Dict[str, Any]:
        endpoint = "/organization/partners"
        return self._make_request("GET", endpoint)

    def get_org_limits(self, org_id: str, currency: str = None, operation: str = None) -> Dict[str, Any]:
        endpoint = f"/organization/{self._path_id(org_id, 'org_id')}/limits"
        params = {}
        if currency:
            params['currency'] = currency
        if operation:
            params['operation'] = operation
        return self._make_request("GET", endpoint, params=params)

    def get_system_config(self) -> Dict[str, Any]:
        endpoint = "/system/config"
        return self._make_request("GET", endpoint)

    @staticmethod
    def verify_webhook(
        payload: Union[str, bytes],
        signature: Optional[str],
        secret: Union[str, bytes],
        tolerance: int = WEBHOOK_TOLERANCE,
        now: Optional[int] = None,
    ) -> bool:
        """Verify the Tapsilat-Signature header of a callback against the organization's webhook secret

        Tapsilat sends ``t=<unix timestamp>,v1=<hex HMAC-SHA256 of "<timestamp>.<raw body>">``. The
        timestamp must be within ``tolerance`` seconds of ``now`` (the current time by default; 0
        disables the check) so that a captured callback cannot be replayed. ``payload`` must be the
        raw request body, before any JSON decoding. The comparison takes constant time.

        A bare hex HMAC-SHA256 of the payload, with or without a ``sha256=`` prefix, is still
        accepted for signatures made the way earlier versions of this SDK documented.
        """
        signature = (signature or "").strip()
        if not signature or not secret:
            return False
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        if isinstance(secret, str):
            secret = secret.encode("utf-8")

        if signature.startswith("sha256=") or "=" not in signature:
            if signature.startswith("sha256="):
                signature = signature[len("sha256="):]
            expected = hmac.new(secret, payload, hashlib.sha256).hexdigest().encode("ascii")
            # Compare bytes in constant time; bytes.lower() only changes ASCII letters
            return hmac.compare_digest(expected, signature.encode("utf-8").lower())

        timestamp = None
        candidates = []
        for part in signature.split(","):
            key, separator, value = part.strip().partition("=")
            if not separator:
                continue
            if key == "t":
                timestamp = value
            elif key == "v1":
                candidates.append(value.encode("utf-8").lower())
        if timestamp is None or not _SIGNATURE_TIMESTAMP_PATTERN.fullmatch(timestamp) or not candidates:
            return False
        if tolerance > 0:
            try:
                signed_at = int(timestamp)
            except ValueError:  # more digits than int() parses
                return False
            current = int(time.time()) if now is None else int(now)
            if abs(current - signed_at) > tolerance:
                return False

        mac = hmac.new(secret, timestamp.encode("ascii") + b".", hashlib.sha256)
        mac.update(payload)
        expected = mac.hexdigest().encode("ascii")
        return any(hmac.compare_digest(expected, candidate) for candidate in candidates)
