import json
from unittest.mock import MagicMock, patch

import pytest

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.exceptions import APIException
from tapsilat_py.models import (
    BuyerDTO,
    CardInstallmentsRequest,
    CardTokenizeRequest,
    GetOrderPaymentsRequest,
    InstallmentTableRequest,
    MarketplaceAccountTarget,
    MarketplaceApprovalPolicyInput,
    MarketplaceContractFilter,
    MarketplacePayoutApproval,
    MarketplacePayoutFilter,
    MarketplacePayoutOperationInput,
    MarketplaceProfileUpdate,
    MarketplaceSubmerchantCreateRequest,
    OrderChargeRequest,
    OrderCreateDTO,
    OrderTermRefundRequest,
    OrgUserTokenCreateRequest,
    SubmerchantCreateRequest,
    SubmerchantPaymentAction,
    SubmerchantPaymentItemUpdate,
    SubmerchantPayoutEventRequest,
    VposCreateRequest,
    VposSubmerchantCreateRequest,
)

BASE = "https://panel.test/api/v1"
V2 = "https://panel.test/api/v2"
CURRENCY_ID = "9f4050e8-1111-4f25-b4ef-aaaaaaaaaaaa"


def make_response(status=200, body="{}", content_type="application/json"):
    response = MagicMock()
    response.status_code = status
    response.content = body.encode() if isinstance(body, str) else body
    response.headers = {"Content-Type": content_type}
    response.reason = "Bad Request"
    response.json.side_effect = lambda: json.loads(response.content)
    return response


@pytest.fixture
def client():
    return TapsilatAPI(api_key="key", base_url=BASE)


def call(mock_request, index=-1):
    """Returns (method, url, params, json) of a recorded request"""
    args, kwargs = mock_request.call_args_list[index]
    return args[0], args[1], kwargs.get("params"), kwargs.get("json")


@patch("tapsilat_py.client.requests.request")
class TestTransport:
    def test_versioned_base_url(self, mock_request):
        assert TapsilatAPI(base_url="https://panel.test/api/v1/")._versioned_base_url("v2") == V2
        assert TapsilatAPI(base_url="https://panel.test")._versioned_base_url("v2") == V2
        assert TapsilatAPI(base_url="https://panel.test/x")._versioned_base_url("v2") == "https://panel.test/x/api/v2"

    def test_error_keeps_code_field_errors_and_raw_body(self, mock_request, client):
        body = '{"message":"INVALID_REQUEST_BODY","code":400000,"errors":{"email":"REQUIRED"}}'
        mock_request.return_value = make_response(400, body)
        with pytest.raises(APIException) as error:
            client.create_submerchant(SubmerchantCreateRequest("tr", "c", "A", "", "1"))
        assert error.value.status_code == 400
        assert error.value.code == 400000
        assert error.value.error == "INVALID_REQUEST_BODY"
        assert error.value.errors == {"email": "REQUIRED"}
        assert error.value.raw_body == body

    def test_error_falls_back_to_error_field(self, mock_request, client):
        mock_request.return_value = make_response(424, '{"error":"payout is not eligible","code":9}')
        with pytest.raises(APIException) as error:
            client.approve_marketplace_payouts(MarketplacePayoutApproval(ids=["p"]))
        assert error.value.message == "payout is not eligible"
        assert error.value.code == 9

    def test_html_page_with_status_200_raises(self, mock_request, client):
        mock_request.return_value = make_response(200, "<!doctype html><html></html>", "text/html; charset=utf-8")
        with pytest.raises(APIException) as error:
            client.get_order("ref")
        assert error.value.status_code == 200
        assert "non-JSON response" in error.value.error
        assert "<html>" in error.value.raw_body

    def test_empty_body_is_success(self, mock_request, client):
        mock_request.return_value = make_response(204, "", "")
        assert client.delete_marketplace_release_policy("rel_1") == {}
        assert call(mock_request)[:2] == ("DELETE", f"{V2}/marketplace/release-policies/rel_1")

    def test_ids_are_path_escaped(self, mock_request, client):
        mock_request.return_value = make_response(200, "{}")
        client.get_vpos("v/1")
        assert call(mock_request)[1] == f"{BASE}/vpos/v%2F1"
        with pytest.raises(ValueError):
            client.get_vpos("")


@patch("tapsilat_py.client.requests.request")
class TestOrders:
    def test_create_order_fills_checkout_url(self, mock_request, client):
        mock_request.side_effect = [
            make_response(200, '{"order_id":"o_1","reference_id":"ref_1"}'),
            make_response(200, '{"reference_id":"ref_1","checkout_url":"https://checkout.test/ref_1"}'),
        ]
        order = OrderCreateDTO(amount=10, currency="TRY", locale="tr",
                               buyer=BuyerDTO(name="J", surname="D", gsm_number="+90 555 123 45 67"))
        response = client.create_order(order)
        assert response.checkout_url == "https://checkout.test/ref_1"
        assert call(mock_request, 0)[3]["buyer"]["gsm_number"] == "+905551234567"
        assert call(mock_request, 1)[:2] == ("GET", f"{BASE}/order/ref_1")

    def test_create_order_ignores_checkout_lookup_failure(self, mock_request, client):
        mock_request.side_effect = [
            make_response(200, '{"order_id":"o_1","reference_id":"ref_1"}'),
            make_response(400, '{"error":"not found"}'),
        ]
        response = client.create_order(OrderCreateDTO(amount=10, currency="TRY", locale="tr", buyer=BuyerDTO(name="J", surname="D")))
        assert response.reference_id == "ref_1"
        assert response.checkout_url is None

    def test_transactions_null_is_empty_list(self, mock_request, client):
        mock_request.return_value = make_response(200, "null")
        assert client.get_order_transactions("ref_1") == []

    def test_order_payments_charge_and_payment_actions(self, mock_request, client):
        mock_request.return_value = make_response(200, '{"isSuccess":true}')
        client.get_order_payments(GetOrderPaymentsRequest(order_reference_id="ref_1"))
        assert call(mock_request)[::3] == ("POST", {"order_reference_id": "ref_1"})
        assert client.charge_order(OrderChargeRequest(order_reference_id="ref_1", retry=True))["isSuccess"]
        assert call(mock_request)[1] == f"{BASE}/order/charge"
        action = SubmerchantPaymentAction("tr", "c", "p", "iyzico")
        client.approve_submerchant_payment(action)
        assert call(mock_request)[:2] == ("POST", f"{BASE}/submerchants/payment/approve")
        client.disapprove_submerchant_payment(action)
        assert call(mock_request)[:2] == ("POST", f"{BASE}/submerchants/payment/disapprove")
        client.update_submerchant_payment_item(SubmerchantPaymentItemUpdate("tr", "c", "p", "k", "1.00", "iyzico"))
        assert call(mock_request)[:2] == ("PUT", f"{BASE}/submerchants/payment/item")

    def test_payment_details_by_conversation_id(self, mock_request, client):
        mock_request.return_value = make_response(200, "{}")
        client.get_order_payment_details_by_conversation_id("conv_1")
        assert call(mock_request)[::3] == ("POST", {"conversation_id": "conv_1"})

    def test_term_routes_and_aliases(self, mock_request, client):
        mock_request.return_value = make_response(200, '{"message":"ok","code":200}')
        client.delete_order_term("order_1", "term_1")
        assert call(mock_request)[::3] == ("DELETE", {"order_id": "order_1", "term_reference_id": "term_1"})
        client.order_manual_callback("ref_1", "conv_1")
        assert call(mock_request)[:2] == ("POST", f"{BASE}/order/callback")
        client.order_related_update("ref_1", "ref_2")
        assert call(mock_request)[:2] == ("PATCH", f"{BASE}/order/releated")
        client.order_terminate("ref_1")
        assert call(mock_request)[::3] == ("POST", {"reference_id": "ref_1"})

    def test_term_refund_requires_order_reference(self, mock_request, client):
        with pytest.raises(ValueError):
            client.refund_order_term(OrderTermRefundRequest(term_id="t", amount=1))
        mock_request.assert_not_called()

    def test_order_list_filters(self, mock_request, client):
        mock_request.return_value = make_response(200, '{"rows":[]}')
        client.get_order_list(conversation_id="c_1", buyer_id="b_1", status=3)
        assert call(mock_request)[2] == {"page": 1, "per_page": 10, "conversation_id": "c_1", "buyer_id": "b_1", "status": 3}

    def test_card_installments(self, mock_request, client):
        mock_request.return_value = make_response(200, '{"is_installment_available":true}')
        client.get_card_installments(CardInstallmentsRequest(bin="54066200", amount=100, currency="TRY", is_three_d=True))
        assert call(mock_request)[1:3] == (f"{BASE}/card/installments", {"bin": "54066200", "amount": 100, "currency": "TRY", "is_three_d": True})
        client.get_installment_table(InstallmentTableRequest(amount=100, currency="TRY"))
        assert call(mock_request)[1:3] == (f"{BASE}/card/installment-table", {"amount": 100, "currency": "TRY"})


@patch("tapsilat_py.client.requests.request")
class TestOrganization:
    def test_routes(self, mock_request, client):
        mock_request.return_value = make_response(200, "{}")
        client.list_organization_currency_presets()
        assert call(mock_request)[1] == f"{BASE}/organization/currency-presets"
        client.create_organization_currency(" usd ")
        assert call(mock_request)[::3] == ("POST", {"currency_code": "USD"})
        client.create_organization_user_token(OrgUserTokenCreateRequest(user_id="u_1", expire=60))
        assert call(mock_request)[3] == {"user_id": "u_1", "expire": 60}
        client.get_suborganization("so_1")
        assert call(mock_request)[1] == f"{BASE}/organization/suborganizations/so_1"
        client.get_submerchant_by_suborganization("so_1")
        assert call(mock_request)[1] == f"{BASE}/organization/suborganizations/so_1/submerchant"

    def test_currency_resolution_is_cached_until_a_currency_is_created(self, mock_request, client):
        currencies = '{"currencies":[{"id":"%s","currency_unit":"TRY"}]}' % CURRENCY_ID
        mock_request.side_effect = lambda *args, **kwargs: make_response(200, currencies)
        assert client.resolve_currency_id("try") == CURRENCY_ID
        assert client.resolve_currency_id(CURRENCY_ID) == CURRENCY_ID
        assert client.resolve_currency_id("TRY") == CURRENCY_ID
        assert mock_request.call_count == 1
        client.create_organization_currency("usd")
        client.resolve_currency_id("TRY")
        assert mock_request.call_count == 3
        with pytest.raises(ValueError):
            client.resolve_currency_id("XYZ")


@patch("tapsilat_py.client.requests.request")
class TestManagementGroups:
    def test_submerchants(self, mock_request, client):
        mock_request.return_value = make_response(200, '{"code":200,"message":"ok"}')
        request = SubmerchantCreateRequest("tr", "c", "A", "a@b.c", "905551112233", currency_id="TRY")
        client.create_submerchant(request)
        assert call(mock_request)[::3] == ("POST", request.to_dict())
        assert call(mock_request)[3]["currency_id"] == "TRY"
        client.update_submerchant("sm_1", request)
        assert call(mock_request)[:2] == ("PATCH", f"{BASE}/submerchants/sm_1")
        client.list_submerchants(2, 5)
        assert call(mock_request)[2] == {"page": 2, "per_page": 5}
        client.delete_submerchant("sm_1")
        assert call(mock_request)[0] == "DELETE"
        client.record_submerchant_payout_event(SubmerchantPayoutEventRequest("k", "ref", "i", "service_completed"))
        assert call(mock_request)[1] == f"{BASE}/submerchant-payout-events"
        seller = MarketplaceSubmerchantCreateRequest(
            "tr", "c", "A", "a@b.c", "1",
            provider_accounts=[MarketplaceAccountTarget(vpos_id="v", environment="TEST")],
            idempotency_key="seller-1",
        )
        client.create_marketplace_submerchant(seller)
        method, url, _, body = call(mock_request)
        assert (method, url) == ("POST", f"{V2}/submerchants")
        assert body["provider_accounts"] == [{"vpos_id": "v", "environment": "TEST"}]

    def test_vpos(self, mock_request, client):
        mock_request.return_value = make_response(200, '{"code":200}')
        client.list_vpos(suborganization_id="so_1")
        assert call(mock_request)[2] == {"page": 1, "per_page": 10, "suborganization_id": "so_1"}
        config = VposCreateRequest(name="POS", acquirer_id="acq", currencies=["TRY"], failover=True, tls=True)
        client.update_vpos("v_1", config)
        assert call(mock_request)[::3] == ("PATCH", config.to_dict())
        for method, expected in [
            (client.list_vpos_acquirers, "/vpos/acquirers"),
            (client.list_card_schemes, "/vpos/card-schemes"),
            (client.list_vpos_acquirer_templates, "/vpos/acquirer-templates"),
        ]:
            method()
            assert call(mock_request)[1] == f"{BASE}{expected}"
        client.create_vpos_submerchant(VposSubmerchantCreateRequest(vpos_id="v_1"))
        assert call(mock_request)[:2] == ("POST", f"{BASE}/vpos-submerchant")
        client.list_vpos_submerchants(vpos_id="v_1")
        assert call(mock_request)[2] == {"page": 1, "per_page": 10, "vpos_id": "v_1"}
        client.delete_vpos_submerchant("vs_1")
        assert call(mock_request)[:2] == ("DELETE", f"{BASE}/vpos-submerchant/vs_1")

    def test_tokenization(self, mock_request, client):
        mock_request.return_value = make_response(200, "{}")
        card = CardTokenizeRequest("4111111111111111", "J D", "12", "30", "123", user_id="u")
        client.tokenize_card(card)
        assert call(mock_request)[:2] == ("POST", f"{BASE}/tokenization/card/tokenize")
        client.list_saved_cards(1, 20)
        assert call(mock_request)[2] == {"page": 1, "per_page": 20}
        client.delete_saved_card("card_1")
        assert call(mock_request)[:2] == ("DELETE", f"{BASE}/tokenization/card/card_1")


@patch("tapsilat_py.client.requests.request")
class TestMarketplace:
    def test_seller_routes_use_v2(self, mock_request, client):
        mock_request.return_value = make_response(200, "{}")
        client.list_marketplace_submerchants(external_id="ext")
        assert call(mock_request)[1:3] == (f"{V2}/submerchants", {"page": 1, "per_page": 20, "external_id": "ext"})
        update = MarketplaceProfileUpdate("tr", "c", "A", "a@b.c", "1", revision="2026-01-02T03:04:05.123456789Z")
        client.update_marketplace_submerchant("s_1", update)
        method, url, _, body = call(mock_request)
        assert (method, url) == ("PATCH", f"{V2}/submerchants/s_1")
        assert body["revision"] == "2026-01-02T03:04:05.123456789Z"
        with pytest.raises(ValueError):
            client.update_marketplace_submerchant("s_1", MarketplaceProfileUpdate("tr", "c", "A", "a@b.c", "1"))
        client.get_marketplace_seller_contracts(
            MarketplaceContractFilter(currency_id="TRY", seller_type="PRIVATE_COMPANY", operation="create", vpos_ids=["v_1", "v_2"])
        )
        assert call(mock_request)[2]["vpos_id"] == ["v_1", "v_2"]
        client.get_marketplace_seller_accounts("s_1")
        assert call(mock_request)[1] == f"{V2}/submerchants/s_1/providers"

    def test_payouts_and_operations(self, mock_request, client):
        mock_request.return_value = make_response(200, "{}")
        client.list_marketplace_payouts(MarketplacePayoutFilter(eligibility="ready", currency="TRY"))
        assert call(mock_request)[2] == {"eligibility": "ready", "currency": "TRY", "page": 1, "per_page": 20}
        client.run_marketplace_payout_operation(
            "p_1", MarketplacePayoutOperationInput(kind="disapprove", idempotency_key="k", revision="r")
        )
        assert call(mock_request)[::3] == ("POST", {"kind": "disapprove", "idempotency_key": "k", "revision": "r"})
        client.reconcile_marketplace_payout_operation("op_1")
        assert call(mock_request)[:2] == ("POST", f"{V2}/marketplace/payout-operations/op_1/reconcile")
        client.retry_marketplace_payout_operation("op_1")
        assert call(mock_request)[1] == f"{V2}/marketplace/payout-operations/op_1/retry"

    def test_approval_policy_currency_resolution(self, mock_request, client):
        currencies = '{"currencies":[{"id":"%s","currency_unit":"TRY"}]}' % CURRENCY_ID
        mock_request.side_effect = [make_response(200, currencies), make_response(201, '{"status":"created"}')]
        client.create_marketplace_approval_policy(
            MarketplaceApprovalPolicyInput(name="Manual", priority=1, mode="manual", currency_id="try")
        )
        assert call(mock_request, 0)[1] == f"{BASE}/organization/currencies"
        assert call(mock_request, 1)[1:] == (
            f"{V2}/marketplace/approval-policies",
            None,
            {"name": "Manual", "priority": 1, "mode": "manual", "currency_id": CURRENCY_ID},
        )


def test_verify_webhook_uses_constant_time_comparison():
    signature = "sha256=5031fe3d989c6d1537a013fa6e739da23463fdaec3b70137d828e36ace221bd0"
    assert TapsilatAPI.verify_webhook("data", signature, "key")
    assert not TapsilatAPI.verify_webhook("data", "sha256=invalid", "key")
    assert not TapsilatAPI.verify_webhook("data", None, "key")
