import hashlib
import hmac
import time

import pytest

from tapsilat_py import (
    WEBHOOK_SIGNATURE_HEADER,
    WEBHOOK_TOLERANCE,
    OrderStatus,
    TapsilatAPI,
    WebhookEvent,
)

# An order_lite callback and a known-good Tapsilat-Signature for this body and secret; the expected
# signature was computed with openssl, independently of the SDK.
PAYLOAD = (
    '{"data":{"id":"5f0c6f1e-1111-4a5b-9c1d-2e3f4a5b6c7d",'
    '"orderReferenceId":"0b6a4f9e-2222-4c3d-8e9f-a1b2c3d4e5f6","conversationId":"wc-1001","status":"3"},'
    '"type":"order_lite","token":"9d8c7b6a-3333-4e5f-a6b7-c8d9e0f1a2b3"}'
)
SECRET = "whsec_test"
TIMESTAMP = 1726480000
SIGNATURE = "3e003945e8122172a03ae1aa56fd099b56e6ac11a8472c03e33809c7c480aeb6"
LEGACY_SIGNATURE = "402b9d6616b32be533a4fc0300e8db19c304a56137d3fb274c614f30f9be6fbb"


def header(signature=SIGNATURE, timestamp=TIMESTAMP):
    return f"t={timestamp},v1={signature}"


def test_constants():
    assert WEBHOOK_SIGNATURE_HEADER == "Tapsilat-Signature"
    assert WEBHOOK_TOLERANCE == 300


def test_verifies_the_tapsilat_signature_header():
    assert TapsilatAPI.verify_webhook(PAYLOAD, header(), SECRET, 300, TIMESTAMP + 10)
    assert TapsilatAPI.verify_webhook(
        PAYLOAD, f" t={TIMESTAMP}, v1={SIGNATURE.upper()} ", SECRET, now=TIMESTAMP
    )


def test_accepts_a_bytes_payload_and_secret():
    assert TapsilatAPI.verify_webhook(PAYLOAD.encode(), header(), SECRET.encode(), now=TIMESTAMP)


def test_rejects_a_tampered_body_or_the_wrong_secret():
    tampered = PAYLOAD.replace('"status":"3"', '"status":"13"')

    assert not TapsilatAPI.verify_webhook(tampered, header(), SECRET, now=TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(), "other", now=TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(), "", now=TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, "", SECRET, now=TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, None, SECRET, now=TIMESTAMP)


def test_rejects_a_replayed_or_malformed_header():
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(), SECRET, 300, TIMESTAMP + 301)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(), SECRET, 300, TIMESTAMP - 301)
    assert TapsilatAPI.verify_webhook(PAYLOAD, header(), SECRET, 0, TIMESTAMP + 86400)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, f"v1={SIGNATURE}", SECRET, 0, TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, f"t={TIMESTAMP}", SECRET, 0, TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(
        PAYLOAD, header(timestamp="1726480000.5"), SECRET, 0, TIMESTAMP
    )
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(timestamp="-1726480000"), SECRET, 0, TIMESTAMP)


def test_rejects_a_timestamp_too_long_to_parse_without_raising():
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(timestamp="9" * 20), SECRET, now=TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(timestamp="9" * 5000), SECRET, now=TIMESTAMP)


def test_rejects_non_ascii_signatures_without_raising():
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(signature="ü" * 64), SECRET, now=TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(timestamp="١٧٢٦٤٨٠٠٠٠"), SECRET, 0, TIMESTAMP)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, "ü" * 64, SECRET)


def test_accepts_any_of_several_v1_signatures():
    signatures = f"t={TIMESTAMP},v1={'0' * 64},v1={SIGNATURE}"

    assert TapsilatAPI.verify_webhook(PAYLOAD, signatures, SECRET, 300, TIMESTAMP)


def test_uses_the_current_time_by_default():
    now = int(time.time())
    signature = hmac.new(SECRET.encode(), f"{now}.{PAYLOAD}".encode(), hashlib.sha256).hexdigest()

    assert TapsilatAPI.verify_webhook(PAYLOAD, header(signature, now), SECRET)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, header(), SECRET)


def test_still_accepts_the_legacy_body_signature():
    assert TapsilatAPI.verify_webhook(PAYLOAD, LEGACY_SIGNATURE, SECRET)
    assert TapsilatAPI.verify_webhook(PAYLOAD, f"sha256={LEGACY_SIGNATURE.upper()}", SECRET)
    assert not TapsilatAPI.verify_webhook(PAYLOAD, LEGACY_SIGNATURE, "other")


def test_parses_an_order_lite_callback():
    event = WebhookEvent.from_payload(PAYLOAD)

    assert event.type == WebhookEvent.TYPE_ORDER_LITE
    assert event.token == "9d8c7b6a-3333-4e5f-a6b7-c8d9e0f1a2b3"
    assert event.reference_id == "0b6a4f9e-2222-4c3d-8e9f-a1b2c3d4e5f6"
    assert event.conversation_id == "wc-1001"
    assert event.status_code == OrderStatus.PAID
    assert event.status == "Paid"
    assert event.is_paid
    assert not event.is_failed
    assert WebhookEvent.from_payload(PAYLOAD.encode()).reference_id == event.reference_id


def test_parses_an_order_callback():
    event = WebhookEvent({
        "type": "order",
        "token": "t-1",
        "data": {"id": "o-1", "reference_id": "ref-1", "conversation_id": "c-1", "status": 13},
    })

    assert event.reference_id == "ref-1"
    assert event.conversation_id == "c-1"
    assert event.status == "Failure"
    assert event.is_failed


def test_parses_an_order_payment_detail_callback():
    event = WebhookEvent({
        "type": "order_payment_detail",
        "token": "t-2",
        "data": {
            "id": "d-1",
            "order_reference_id": "ref-2",
            "conversation_id": "c-2",
            "order": {"reference_id": "ref-2", "id": "o-2", "status": "Paid"},
            "order_payment_status": {"code": 0},
        },
    })

    assert event.reference_id == "ref-2"
    assert event.conversation_id == "c-2"
    assert event.status_code == OrderStatus.PAID


def test_parses_callbacks_without_a_status():
    extended = WebhookEvent({
        "type": "extended_order",
        "data": {"id": "o-3", "reference_id": "ref-3", "terms": [{"reference_id": "term-1", "status": 2}]},
    })
    assert extended.reference_id == "ref-3"
    assert extended.conversation_id is None
    assert extended.status_code is None
    assert extended.status is None
    assert not extended.is_paid

    facilitator = WebhookEvent({
        "type": "payment_facilitator",
        "data": {"id": "p-1", "payment_id": "pay-1", "reference_id": "ref-4"},
    })
    assert facilitator.reference_id == "ref-4"


def test_ignores_a_zero_uuid():
    event = WebhookEvent({
        "type": "order_payment_detail",
        "data": {
            "order_reference_id": "00000000-0000-0000-0000-000000000000",
            "order": {"reference_id": "ref-5"},
        },
    })

    assert event.reference_id == "ref-5"


def test_reads_the_whole_payload_when_it_has_no_data_object():
    event = WebhookEvent.from_payload('{"reference_id": 42, "status": 9.0}')

    assert event.type is None
    assert event.token is None
    assert event.reference_id == "42"
    assert event.status == "Completed"


@pytest.mark.parametrize("payload", ['"order"', "[1]", "null", "not json", b"\xff"])
def test_rejects_a_payload_that_is_not_a_json_object(payload):
    with pytest.raises(ValueError):
        WebhookEvent.from_payload(payload)


def test_order_status_names_and_groups():
    assert OrderStatus.code("waiting for payment") == OrderStatus.WAITING_FOR_PAYMENT
    assert OrderStatus.code("21") == OrderStatus.EXPIRED
    assert OrderStatus.code(13.0) == OrderStatus.FAILURE
    assert OrderStatus.name(15) == "Partially refunded"
    assert OrderStatus.code("SUCCESS") is None
    assert OrderStatus.code(99) is None
    assert OrderStatus.code(True) is None
    assert OrderStatus.code("9" * 5000) is None
    assert OrderStatus.name(None) is None

    assert OrderStatus.is_paid("Sub merchant payment approved")
    assert OrderStatus.is_paid(OrderStatus.COMPLETED)
    assert not OrderStatus.is_paid("Waiting for payment")
    assert OrderStatus.is_failed("Expired")
    assert not OrderStatus.is_failed("Paid")
    assert OrderStatus.is_refunded("10")
    assert sorted(OrderStatus.NAMES) == list(range(1, 30))
