from typing import Any, Dict, Optional

import hmac
import hashlib
import requests

from .exceptions import APIException
from .models import (
    OrderAccountingRequest,
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
    OrderPaymentOptionsUpdateDTO,
    SplitOrderItemPaymentDTO,
)
from .validators import validate_gsm_number, validate_installments


class TapsilatAPI:
    def __init__(
        self,
        api_key: str = "",
        timeout: int = 10,
        base_url: str = "https://panel.tapsilat.dev/api/v1",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

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
    ) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
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
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            resp_status_code = e.response.status_code if e.response is not None else 0
            api_code_from_json = -1
            error_msg = "Unknown API error"

            if e.response is not None:
                try:
                    if e.response.content:
                        error_data = e.response.json()
                        api_code_from_json = error_data.get("code", -1)
                        error_msg = error_data.get("error", e.response.text)
                    else:
                        error_msg = e.response.reason or "HTTP error with no content"
                except requests.exceptions.JSONDecodeError:
                    error_msg = e.response.text

            raise APIException(resp_status_code, api_code_from_json, error_msg) from e
        except requests.exceptions.RequestException as e:
            raise APIException(0, -1, str(e)) from e

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

    def get_order(self, reference_id: str) -> OrderResponse:
        endpoint = f"/order/{reference_id}"
        response = self._make_request("GET", endpoint)
        return OrderResponse(response)

    def get_order_by_conversation_id(self, conversation_id: str) -> OrderResponse:
        endpoint = f"/order/conversation/{conversation_id}"
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
    ) -> dict:
        endpoint = "/order/list"
        raw_params = {
            "page": page,
            "per_page": per_page,
            "start_date": start_date,
            "end_date": end_date,
            "organization_id": organization_id,
            "related_reference_id": related_reference_id,
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
        endpoint = f"/order/{reference_id}/payment-details"
        return self._make_request("GET", endpoint)

    def get_order_status(self, reference_id: str) -> dict:
        endpoint = f"/order/{reference_id}/status"
        return self._make_request("GET", endpoint)

    def get_order_transactions(self, reference_id: str) -> dict:
        endpoint = f"/order/{reference_id}/transactions"
        return self._make_request("GET", endpoint)

    def create_order_term(self, term: OrderPaymentTermCreateDTO) -> dict:
        endpoint = "/order/term"
        payload = term.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def delete_order_term(self, request: OrderPaymentTermDeleteDTO) -> dict:
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
        """Get orders with pagination and optional buyer filter"""
        endpoint = "/order/list"
        params = {"page": page, "per_page": per_page}
        if buyer_id:
            params["buyer_id"] = buyer_id
        return self._make_request("GET", endpoint, params=params)

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
        """Get User Limits Configuration"""
        endpoint = "/organization/limit/user"
        payload = request.to_dict()
        return self._make_request("GET", endpoint, json_payload=payload)

    def set_organization_limit_user(self, request: SetLimitUserRequest) -> dict:
        """Set Limit To User"""
        endpoint = "/organization/limit/user"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_organization_limits(self) -> dict:
        """Get Organization Transaction Limits"""
        endpoint = "/organization/limits"
        return self._make_request("GET", endpoint)

    def list_organization_vpos(self, request: GetVposRequest) -> dict:
        """List Virtual POS Terminals"""
        endpoint = "/organization/list-vpos"
        payload = request.to_dict()
        return self._make_request("POST", endpoint, json_payload=payload)

    def get_organization_meta(self, name: str) -> dict:
        """Get Organization Metadata"""
        endpoint = f"/organization/meta/{name}"
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

    @staticmethod
    def verify_webhook(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = hmac.new(
            secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        return f"sha256={expected_signature}" == signature
