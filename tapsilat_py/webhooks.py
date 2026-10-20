import json
import re
from typing import Any, Dict, Optional, Union

# The header that carries the signature of every callback Tapsilat sends
WEBHOOK_SIGNATURE_HEADER = "Tapsilat-Signature"

# How many seconds a callback's signature timestamp may differ from the current time
WEBHOOK_TOLERANCE = 300

_DIGITS_PATTERN = re.compile(r"[0-9]+")
_ZERO_UUID = "00000000-0000-0000-0000-000000000000"


class OrderStatus:
    """Order status codes, as callbacks and order details carry them, and the names that
    GET /order/{reference_id}/status returns for them.
    """

    RECEIVED = 1
    UNPAID = 2
    PAID = 3
    PROCESSING = 4
    SHIPPED = 5
    ON_HOLD = 6
    WAITING_FOR_PAYMENT = 7
    CANCELLED = 8
    COMPLETED = 9
    REFUNDED = 10
    FRAUD = 11
    REJECTED = 12
    FAILURE = 13
    RETRYING = 14
    PARTIALLY_REFUNDED = 15
    SUB_MERCHANT_PAYMENT_APPROVED = 16
    SUB_MERCHANT_PAYMENT_DISAPPROVED = 17
    SUB_MERCHANT_PAYMENT_ERRORED = 18
    STILL_HAS_UNPAID_INSTALLMENTS = 19
    STILL_HAS_UNPAID_TERMS = 20
    EXPIRED = 21
    STILL_HAS_UNPAID_SUB_MERCHANT_PAYMENTS = 22
    PARTIALLY_PAID = 23
    TERMINATED = 24
    CARD_TOKENIZATION = 25
    PRE_AUTHORIZED = 26
    DISPUTED = 27
    PARTIALLY_DISPUTED = 28
    SUSPECT = 29

    NAMES: Dict[int, str] = {
        RECEIVED: "Received",
        UNPAID: "Unpaid",
        PAID: "Paid",
        PROCESSING: "Processing",
        SHIPPED: "Shipped",
        ON_HOLD: "On hold",
        WAITING_FOR_PAYMENT: "Waiting for payment",
        CANCELLED: "Cancelled",
        COMPLETED: "Completed",
        REFUNDED: "Refunded",
        FRAUD: "Fraud",
        REJECTED: "Rejected",
        FAILURE: "Failure",
        RETRYING: "Retrying",
        PARTIALLY_REFUNDED: "Partially refunded",
        SUB_MERCHANT_PAYMENT_APPROVED: "Sub merchant payment approved",
        SUB_MERCHANT_PAYMENT_DISAPPROVED: "Sub merchant payment disapproved",
        SUB_MERCHANT_PAYMENT_ERRORED: "Sub merchant payment errored",
        STILL_HAS_UNPAID_INSTALLMENTS: "Still has unpaid installments",
        STILL_HAS_UNPAID_TERMS: "Still has unpaid terms",
        EXPIRED: "Expired",
        STILL_HAS_UNPAID_SUB_MERCHANT_PAYMENTS: "Still has unpaid sub merchant payments",
        PARTIALLY_PAID: "Partially Paid",
        TERMINATED: "Terminated",
        CARD_TOKENIZATION: "Card Tokenization",
        PRE_AUTHORIZED: "Pre Authorized",
        DISPUTED: "Disputed",
        PARTIALLY_DISPUTED: "Partially disputed",
        SUSPECT: "Suspect",
    }

    # Statuses of an order whose payment was captured
    PAID_STATUSES = frozenset({PAID, COMPLETED, SUB_MERCHANT_PAYMENT_APPROVED})

    # Statuses of an order that will not be paid
    FAILED_STATUSES = frozenset({CANCELLED, FRAUD, REJECTED, FAILURE, EXPIRED, TERMINATED})

    # Statuses of an order whose payment was refunded in full or in part
    REFUNDED_STATUSES = frozenset({REFUNDED, PARTIALLY_REFUNDED})

    _CODES_BY_NAME = {name.lower(): code for code, name in NAMES.items()}

    @classmethod
    def code(cls, status: Any) -> Optional[int]:
        """Returns the status code for a code, a numeric string such as order_lite callbacks send,
        or a status name such as "Paid" (case-insensitive), or None when the value is not a status
        """
        if isinstance(status, bool):
            return None
        if isinstance(status, float) and status.is_integer():
            status = int(status)
        if isinstance(status, int):
            return status if status in cls.NAMES else None
        if not isinstance(status, str):
            return None
        status = status.strip()
        if _DIGITS_PATTERN.fullmatch(status):
            try:
                return cls.code(int(status))
            except ValueError:  # more digits than int() parses
                return None
        return cls._CODES_BY_NAME.get(status.lower())

    @classmethod
    def name(cls, status: Any) -> Optional[str]:
        """Returns the status name, such as "Paid", or None when the value is not a status"""
        code = cls.code(status)
        return None if code is None else cls.NAMES[code]

    @classmethod
    def is_paid(cls, status: Any) -> bool:
        return cls.code(status) in cls.PAID_STATUSES

    @classmethod
    def is_failed(cls, status: Any) -> bool:
        return cls.code(status) in cls.FAILED_STATUSES

    @classmethod
    def is_refunded(cls, status: Any) -> bool:
        return cls.code(status) in cls.REFUNDED_STATUSES


class WebhookEvent:
    """A callback Tapsilat posts to an organization's callback URLs or to an order's
    payment_success_url and payment_failure_url: {"type": "...", "data": {...}, "token": "<delivery id>"}.

    The shape of "data" depends on the type, which each organization chooses in the panel:
    "order_lite" (the default), "order", "order_payment_detail", "extended_order" or
    "payment_facilitator". The properties read the order's reference ID, conversation ID and status
    from whichever shape arrived.

    Verify the Tapsilat-Signature header with TapsilatAPI.verify_webhook() before trusting a callback.
    """

    TYPE_ORDER = "order"
    TYPE_ORDER_LITE = "order_lite"
    TYPE_ORDER_PAYMENT_DETAIL = "order_payment_detail"
    TYPE_EXTENDED_ORDER = "extended_order"
    TYPE_PAYMENT_FACILITATOR = "payment_facilitator"

    def __init__(self, payload: Dict[str, Any]):
        if not isinstance(payload, dict):
            raise ValueError("the webhook payload is not a JSON object")
        type_ = payload.get("type")
        token = payload.get("token")
        data = payload.get("data")
        # The decoded payload
        self.payload: Dict[str, Any] = payload
        self.type: Optional[str] = type_ if isinstance(type_, str) else None
        # Unique per delivery
        self.token: Optional[str] = token if isinstance(token, str) else None
        # The callback's "data" object, or the whole payload when it has none
        self.data: Dict[str, Any] = data if isinstance(data, dict) else payload

    @classmethod
    def from_payload(cls, payload: Union[str, bytes]) -> "WebhookEvent":
        """Decodes a raw callback body; raises ValueError when it is not a JSON object"""
        try:
            decoded = json.loads(payload)
        except ValueError as e:
            raise ValueError("the webhook payload is not a JSON object") from e
        return cls(decoded)

    @property
    def reference_id(self) -> Optional[str]:
        """The order's reference ID"""
        order = self._order()
        return _first_id(
            self.data.get("orderReferenceId"),
            self.data.get("order_reference_id"),
            self.data.get("reference_id"),
            order.get("reference_id"),
        )

    @property
    def conversation_id(self) -> Optional[str]:
        """The conversation ID the order was created with"""
        return _first_id(self.data.get("conversationId"), self.data.get("conversation_id"))

    @property
    def status_code(self) -> Optional[int]:
        """The order status code (see OrderStatus), or None when this callback type carries none"""
        code = OrderStatus.code(self.data.get("status"))
        if code is None:
            code = OrderStatus.code(self._order().get("status"))
        return code

    @property
    def status(self) -> Optional[str]:
        """The order status name, such as "Paid", or None when this callback type carries none"""
        return OrderStatus.name(self.status_code)

    @property
    def is_paid(self) -> bool:
        return OrderStatus.is_paid(self.status_code)

    @property
    def is_failed(self) -> bool:
        return OrderStatus.is_failed(self.status_code)

    @property
    def is_refunded(self) -> bool:
        return OrderStatus.is_refunded(self.status_code)

    def _order(self) -> Dict[str, Any]:
        order = self.data.get("order")
        return order if isinstance(order, dict) else {}


def _first_id(*values: Any) -> Optional[str]:
    """Returns the first non-empty string, or integer as a string, skipping the zero UUID"""
    for value in values:
        if isinstance(value, str) and value not in ("", _ZERO_UUID):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
    return None
