from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, Dict, List, Optional


def _asdict_factory(data):
    """Convert dataclass to dict, removing None values and handling nested dataclasses"""
    if not is_dataclass(data):
        return data

    def convert_value(obj):
        if isinstance(obj, list):
            return [convert_value(v) for v in obj]
        if is_dataclass(obj):
            return _asdict_factory(obj)
        return obj

    result = {}
    for field in fields(data):
        value = getattr(data, field.name)
        if value is not None:
            result[field.name] = convert_value(value)
    return result


@dataclass
class BuyerDTO:
    name: str
    surname: str
    birth_date: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    gsm_number: Optional[str] = None
    id: Optional[str] = None
    identity_number: Optional[str] = None
    ip: Optional[str] = None
    last_login_date: Optional[str] = None
    registration_date: Optional[str] = None
    title: Optional[str] = None
    zip_code: Optional[str] = None
    income_type: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    registration_address: Optional[str] = None


@dataclass
class BasketItemPayerDTO:
    address: Optional[str] = None
    reference_id: Optional[str] = None
    tax_office: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    vat: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    identity_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class OrderItemPayment:
    amount: Optional[float] = None
    card_brand: Optional[str] = None
    id: Optional[str] = None
    masked_bin: Optional[str] = None
    paid_date: Optional[str] = None
    refundable_amount: Optional[float] = None
    refunded: Optional[bool] = None
    refunded_amount: Optional[float] = None
    refunded_date: Optional[str] = None
    status: Optional[int] = None
    type: Optional[str] = None


@dataclass
class BasketItemDTO:
    category1: Optional[str] = None
    category2: Optional[str] = None
    coupon: Optional[str] = None
    coupon_discount: Optional[float] = None
    data: Optional[str] = None
    id: Optional[str] = None
    item_type: Optional[str] = None
    name: Optional[str] = None
    item_payments: Optional[List[OrderItemPayment]] = None
    paid_amount: Optional[float] = None
    paidable_amount: Optional[float] = None
    price: Optional[float] = None
    commission_amount: Optional[float] = None
    mcc: Optional[str] = None
    payer: Optional[BasketItemPayerDTO] = None
    quantity: Optional[int] = None
    quantity_float: Optional[float] = None
    quantity_unit: Optional[str] = None
    refundable_amount: Optional[float] = None
    refunded_amount: Optional[float] = None
    status: Optional[int] = None
    sub_merchant_key: Optional[str] = None
    sub_merchant_price: Optional[str] = None
    # RFC3339 timestamp before which the item's marketplace payout is not released
    payout_release_at: Optional[str] = None


@dataclass
class BillingAddressDTO:
    address: Optional[str] = None
    billing_type: Optional[str] = None
    citizenship: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    country: Optional[str] = None
    district: Optional[str] = None
    tax_office: Optional[str] = None
    title: Optional[str] = None
    vat_number: Optional[str] = None
    zip_code: Optional[str] = None
    neighbourhood: Optional[str] = None
    street1: Optional[str] = None
    street2: Optional[str] = None
    street3: Optional[str] = None


@dataclass
class CheckoutDesignDTO:
    input_background_color: Optional[str] = None
    input_text_color: Optional[str] = None
    label_text_color: Optional[str] = None
    left_background_color: Optional[str] = None
    logo: Optional[str] = None
    # Deprecated: checkout no longer renders custom order detail HTML; the value is ignored
    order_detail_html: Optional[str] = None
    right_background_color: Optional[str] = None
    text_color: Optional[str] = None
    pay_button_color: Optional[str] = None
    # Deprecated: ignored by checkout; use the order's redirect_success_url and redirect_failure_url
    redirect_url: Optional[str] = None
    pay_button_text_color: Optional[str] = None
    page_background_color: Optional[str] = None
    border_color: Optional[str] = None
    input_border_color: Optional[str] = None
    accent_color: Optional[str] = None
    text_muted_color: Optional[str] = None
    surface_muted_color: Optional[str] = None
    dark_mode_enabled: Optional[bool] = None
    dark_colors: Optional[Dict[str, str]] = None
    placeholder_color: Optional[str] = None


@dataclass
class MetadataDTO:
    key: str
    value: str


@dataclass
class OrderCardDTO:
    card_id: str
    card_sequence: int


@dataclass
class PaymentTermDTO:
    """Payment term sent with order creation; due_date and paid_date must be RFC3339 timestamps"""

    amount: Optional[float] = None
    data: Optional[str] = None
    due_date: Optional[str] = None
    paid_date: Optional[str] = None
    required: Optional[bool] = None
    status: Optional[str] = None
    term_reference_id: Optional[str] = None
    term_sequence: Optional[int] = None
    hash_id: Optional[str] = None
    id: Optional[int] = None
    payments: Optional[List[Any]] = None


@dataclass
class OrderPFSubMerchantDTO:
    mcc: Optional[str] = None
    name: Optional[str] = None
    org_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    country_iso_code: Optional[str] = None
    id: Optional[str] = None
    national_id: Optional[str] = None
    postal_code: Optional[str] = None
    submerchant_nin: Optional[str] = None
    submerchant_url: Optional[str] = None
    switch_id: Optional[str] = None
    terminal_no: Optional[str] = None


@dataclass
class ShippingAddressDTO:
    address: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    country: Optional[str] = None
    shipping_date: Optional[str] = None
    tracking_code: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class SubOrganizationDTO:
    acquirer: Optional[str] = None
    address: Optional[str] = None
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    currency: Optional[str] = None
    email: Optional[str] = None
    gsm_number: Optional[str] = None
    iban: Optional[str] = None
    identity_number: Optional[str] = None
    legal_company_title: Optional[str] = None
    organization_name: Optional[str] = None
    sub_merchant_external_id: Optional[str] = None
    sub_merchant_key: Optional[str] = None
    sub_merchant_type: Optional[str] = None
    tax_number: Optional[str] = None
    tax_office: Optional[str] = None


@dataclass
class SubmerchantDTO:
    amount: Optional[float] = None
    merchant_reference_id: Optional[str] = None
    order_basket_item_id: Optional[str] = None


@dataclass
class OrderConsent:
    title: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderCreateDTO:
    amount: float
    currency: str
    locale: str
    buyer: BuyerDTO
    basket_items: Optional[List[BasketItemDTO]] = None
    billing_address: Optional[BillingAddressDTO] = None
    checkout_design: Optional[CheckoutDesignDTO] = None
    consents: Optional[List[OrderConsent]] = None
    conversation_id: Optional[str] = None
    enabled_installments: Optional[List[int]] = None
    external_reference_id: Optional[str] = None
    metadata: Optional[List[MetadataDTO]] = None
    order_cards: Optional[List[OrderCardDTO]] = None
    paid_amount: Optional[float] = None
    partial_payment: Optional[bool] = None
    payment_failure_url: Optional[str] = None
    payment_methods: Optional[bool] = None
    payment_mode: Optional[str] = None  # "auth" or "preauth"
    payment_options: Optional[List[str]] = None  # "credit_card","bank_transfer","cash"
    payment_success_url: Optional[str] = None
    payment_terms: Optional[List[PaymentTermDTO]] = None
    pf_sub_merchant: Optional[OrderPFSubMerchantDTO] = None
    redirect_failure_url: Optional[str] = None
    redirect_success_url: Optional[str] = None
    shipping_address: Optional[ShippingAddressDTO] = None
    sub_organization: Optional[SubOrganizationDTO] = None
    submerchants: Optional[List[SubmerchantDTO]] = None
    tax_amount: Optional[float] = None
    three_d_force: Optional[bool] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderAccountingRequest:
    order_reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderPostAuthRequest:
    amount: float
    reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderManualCallbackDTO:
    reference_id: str
    conversation_id: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class RefundOrderDTO:
    amount: float
    reference_id: str
    order_item_id: Optional[str] = None
    order_item_payment_id: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class CancelOrderDTO:
    reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class RefundAllOrderDTO:
    reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderPaymentDetailDTO:
    reference_id: str
    conversation_id: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class TerminateRequest:
    reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderRelatedReferenceDTO:
    reference_id: str
    related_reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderPaymentTermCreateDTO:
    """Adds a payment term to an order.

    ``order_id`` is the order's ID (``order_id`` from order creation), not its
    reference ID. Dates use YYYY-MM-DD.
    """

    order_id: str
    term_reference_id: str
    amount: float
    due_date: str
    term_sequence: int
    required: bool
    status: str
    data: Optional[str] = None
    paid_date: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderTermRefundRequest:
    """Refunds a payment term; ``term_id`` is the term's ID and ``reference_id`` the order's reference ID (required)"""

    term_id: str
    amount: float
    reference_id: Optional[str] = None
    term_payment_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SubscriptionBilling:
    address: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    country: Optional[str] = None
    vat_number: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class SubscriptionUser:
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    id: Optional[str] = None
    identity_number: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class SubscriptionGetRequest:
    external_reference_id: Optional[str] = None
    reference_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SubscriptionCancelRequest:
    external_reference_id: Optional[str] = None
    reference_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SubscriptionCreateRequest:
    amount: Optional[float] = None
    billing: Optional[SubscriptionBilling] = None
    card_id: Optional[str] = None
    currency: Optional[str] = None
    cycle: Optional[int] = None
    external_reference_id: Optional[str] = None
    failure_url: Optional[str] = None
    payment_date: Optional[int] = None
    period: Optional[int] = None
    success_url: Optional[str] = None
    title: Optional[str] = None
    user: Optional[SubscriptionUser] = None
    # day, week, month or year
    interval: Optional[str] = None
    interval_count: Optional[int] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SubscriptionRedirectRequest:
    subscription_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class AddBasketItemRequest:
    order_reference_id: str
    basket_item: BasketItemDTO

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class RemoveBasketItemRequest:
    order_reference_id: str
    basket_item_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class UpdateBasketItemRequest:
    order_reference_id: str
    basket_item: BasketItemDTO

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class CallbackURLDTO:
    callback_url: Optional[str] = None
    cancel_callback_url: Optional[str] = None
    fail_callback_url: Optional[str] = None
    refund_callback_url: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SubscriptionOrder:
    amount: Optional[str] = None
    currency: Optional[str] = None
    payment_date: Optional[str] = None
    payment_url: Optional[str] = None
    reference_id: Optional[str] = None
    status: Optional[str] = None


class OrderResponse(dict):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def reference_id(self) -> str:
        return self.get("reference_id")

    @property
    def checkout_url(self) -> str:
        return self.get("checkout_url")

    @property
    def order_id(self) -> str:
        return self.get("order_id")


@dataclass
class OrderPaymentTermDeleteDTO:
    order_id: str
    term_reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderPaymentTermUpdateDTO:
    """Replaces a payment term: the server stores every field as sent. Dates use YYYY-MM-DD."""

    amount: float
    due_date: str
    paid_date: Optional[str]
    required: bool
    status: str
    term_reference_id: str
    term_sequence: int

    def to_dict(self) -> dict:
        return _asdict_factory(self)


class OrgCreateBusinessRequest_BusinessType:
    INDIVIDUAL = 0
    CORPORATE = 1
    NON_PROFIT = 2
    GOVERNMENT = 3
    UNKNOWN = 4


@dataclass
class OrgCreateBusinessRequest:
    address: str
    business_name: str
    business_type: int
    email: str
    first_name: str
    identity_number: str
    last_name: str
    phone: str
    tax_number: str
    tax_office: str
    zip_code: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class GetUserLimitRequest:
    user_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SetLimitUserRequest:
    limit_id: str
    user_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class GetVposRequest:
    currency_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrgCreateUserReq:
    conversation_id: str
    email: str
    first_name: str
    identity_number: str
    is_mail_verified: bool
    last_name: str
    phone: str
    reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrgUserVerifyReq:
    user_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrgUserMobileVerifyReq:
    user_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# Order payments, charging and submerchant payment actions


@dataclass
class GetOrderPaymentsRequest:
    """Identifies an order by any one of its identifiers"""

    order_id: Optional[str] = None
    order_reference_id: Optional[str] = None
    conversation_id: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderChargeRequest:
    order_reference_id: str
    retry: Optional[bool] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SubmerchantPaymentAction:
    locale: str
    conversation_id: str
    payment_transaction_id: str
    acquirer: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SubmerchantPaymentItemUpdate:
    locale: str
    conversation_id: str
    payment_transaction_id: str
    sub_merchant_key: str
    # Positive decimal amount as a string, for example "60.25"
    sub_merchant_price: str
    acquirer: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# Card installments


@dataclass
class CardInstallmentsRequest:
    # The card's first digits (at least 8)
    bin: str
    amount: float
    # Currency unit or name, for example "TRY"
    currency: str
    is_three_d: Optional[bool] = None

    def to_params(self) -> dict:
        return _asdict_factory(self)


@dataclass
class InstallmentTableRequest:
    amount: float
    currency: str
    is_three_d: Optional[bool] = None

    def to_params(self) -> dict:
        return _asdict_factory(self)


# Organization


@dataclass
class OrgUserTokenCreateRequest:
    """Creates an access token for an organization user; ``expire`` is in minutes"""

    email: Optional[str] = None
    expire: Optional[int] = None
    invalidate_old_tokens: Optional[bool] = None
    user_id: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# Submerchants


@dataclass
class SubmerchantCreateRequest:
    """Creates or replaces a submerchant.

    ``currency_id`` accepts a currency UUID or an organization currency unit
    such as "TRY". ``sub_merchant_type`` is PERSONAL (requires
    identity_number), PRIVATE_COMPANY or LIMITED_OR_JOINT_STOCK_COMPANY (both
    require tax_number). Updates replace the profile, so send every field.
    """

    locale: str
    conversation_id: str
    name: str
    email: str
    gsm_number: str
    address: Optional[str] = None
    iban: Optional[str] = None
    tax_office: Optional[str] = None
    legal_company_title: Optional[str] = None
    currency_id: Optional[str] = None
    sub_merchant_external_id: Optional[str] = None
    identity_number: Optional[str] = None
    sub_merchant_type: Optional[str] = None
    tax_number: Optional[str] = None
    sub_merchant_key: Optional[str] = None
    organization_id: Optional[str] = None
    status: Optional[str] = None
    system_time: Optional[int] = None
    contact_name: Optional[str] = None
    contact_surname: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


SubmerchantUpdateRequest = SubmerchantCreateRequest


@dataclass
class MarketplaceAccountTarget:
    vpos_id: str
    # TEST or PROD
    environment: str


@dataclass
class MarketplaceSubmerchantCreateRequest(SubmerchantCreateRequest):
    """Creates a marketplace seller.

    Omit both ``vpos_id`` and ``provider_accounts`` to create only the logical
    seller; never combine them. Reuse the same ``idempotency_key`` and data
    when retrying.
    """

    provider_accounts: Optional[List[MarketplaceAccountTarget]] = None
    labels: Optional[List[str]] = None
    vpos_id: Optional[str] = None
    # auto or manual
    approval_mode: Optional[str] = None
    release_policy_id: Optional[str] = None
    idempotency_key: Optional[str] = None


@dataclass
class SubmerchantPayoutEventRequest:
    idempotency_key: str
    order_reference: str
    item_id: str
    event_type: str
    # RFC3339 timestamp
    occurred_at: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# VPOS


@dataclass
class VposCreateRequest:
    """VPOS configuration.

    Updates replace the stored configuration, so fields left out are stored
    as empty or false: read the VPOS first and send every field back.
    ``currencies`` accepts currency UUIDs or units such as "TRY".
    """

    name: str
    acquirer_id: str
    currencies: List[str]
    bank_name: Optional[str] = None
    env_mode: Optional[str] = None
    merchant: Optional[str] = None
    merchant_code: Optional[str] = None
    merchant_key: Optional[str] = None
    auth_key: Optional[str] = None
    terminal: Optional[str] = None
    company: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    store_key: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    guid: Optional[str] = None
    pid: Optional[str] = None
    client_id: Optional[str] = None
    client_code: Optional[str] = None
    type: Optional[str] = None
    block_date: Optional[int] = None
    priority: Optional[int] = None
    main: Optional[bool] = None
    force_three_d: Optional[bool] = None
    marketplace: Optional[bool] = None
    pf: Optional[bool] = None
    payment_mode: Optional[str] = None
    prefix: Optional[str] = None
    card_schemes: Optional[List[str]] = None
    failover: Optional[bool] = None
    pf_id: Optional[str] = None
    redirect_uri: Optional[str] = None
    tls: Optional[bool] = None
    tls_key: Optional[str] = None
    tls_cert: Optional[str] = None
    root_ca: Optional[str] = None
    main_installment: Optional[bool] = None
    main_without_installment: Optional[bool] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


VposUpdateRequest = VposCreateRequest


@dataclass
class VposSubmerchantCreateRequest:
    vpos_id: str
    external_reference_id: Optional[str] = None
    submerchant_id: Optional[str] = None
    terminal_no: Optional[str] = None
    mcc: Optional[str] = None
    tax_id: Optional[str] = None
    national_id: Optional[str] = None
    title: Optional[str] = None
    switch_id: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    country_isocode: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    submerchant_url: Optional[str] = None
    submerchant_nin: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class VposSubmerchantUpdateRequest:
    external_reference_id: Optional[str] = None
    submerchant_id: Optional[str] = None
    terminal_no: Optional[str] = None
    mcc: Optional[str] = None
    tax_id: Optional[str] = None
    national_id: Optional[str] = None
    title: Optional[str] = None
    switch_id: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# Card tokenization


@dataclass
class CardTokenizeRequest:
    card_number: str
    holder_name: str
    expiry_month: str
    # Two or four digits
    expiry_year: str
    cvv: str
    name: Optional[str] = None
    default: Optional[bool] = None
    # 1 = 3D secure, 2 = half secure, 3 = non-secure
    mode: Optional[int] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    redirect_success_url: Optional[str] = None
    redirect_failure_url: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# Marketplace (API version 2)


@dataclass
class MarketplaceProfileUpdate(SubmerchantCreateRequest):
    """Replaces a marketplace seller profile at ``revision``.

    ``revision`` comes from ``get_marketplace_submerchant`` and must be sent
    back exactly as received. Preserve fields you are not changing.
    """

    revision: str = ""
    labels: Optional[List[str]] = None
    approval_mode: Optional[str] = None
    release_policy_id: Optional[str] = None
    idempotency_key: Optional[str] = None


@dataclass
class MarketplaceContractFilter:
    # Currency UUID or unit such as "TRY"
    currency_id: str
    seller_type: str
    operation: str
    vpos_ids: List[str]


@dataclass
class MarketplaceAccountAction:
    """Confirms an account action using the account's latest revision and environment"""

    # create, retry, resubmit, update, retrieve or retry_sync
    action: str
    environment: str
    revision: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class MarketplacePayoutFilter:
    order_id: Optional[str] = None
    submerchant_id: Optional[str] = None
    vpos_id: Optional[str] = None
    provider: Optional[str] = None
    status: Optional[str] = None
    release_status: Optional[str] = None
    approval_mode: Optional[str] = None
    # Currency unit such as "TRY"
    currency: Optional[str] = None
    eligibility: Optional[str] = None
    search: Optional[str] = None
    min_amount: Optional[str] = None
    max_amount: Optional[str] = None
    # YYYY-MM-DD
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    per_page: int = 20

    def to_params(self) -> dict:
        return {k: v for k, v in _asdict_factory(self).items() if v != ""}


@dataclass
class MarketplacePayoutApproval:
    # At most 100 payout IDs
    ids: List[str]

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class MarketplaceApprovalPolicyInput:
    """Creates or replaces an approval rule.

    ``currency_id`` must be a UUID on the wire; the client resolves units such
    as "TRY" before sending.
    """

    name: str
    priority: int
    mode: str
    enabled: Optional[bool] = None
    provider: Optional[str] = None
    min_amount: Optional[str] = None
    max_amount: Optional[str] = None
    currency_id: Optional[str] = None
    submerchant_ids: Optional[List[str]] = None
    labels_any: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class MarketplaceReleasePolicyInput:
    name: str
    enabled: Optional[bool] = None
    default: Optional[bool] = None
    minimum_delay_seconds: Optional[int] = None
    explicit_not_before: Optional[str] = None
    required_external_event: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class MarketplaceApprovalSettings:
    # auto or manual
    default_mode: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class MarketplacePayoutOperationInput:
    # disapprove or update_item
    kind: str
    idempotency_key: str
    # The payout's current revision, sent back exactly as received
    revision: str
    seller_reference: Optional[str] = None
    net_amount: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


# Added on main


@dataclass
class OrderPaymentOptionsUpdateDTO:
    payment_options: List[str]
    reference_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SplitOrderItemPaymentDTO:
    amount: float
    order_id: str
    order_item_payment_id: str

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrderOIPDTO:
    order_id: str
    basket_item_id: str
    amount: float
    type: int
    wallet_id: Optional[str] = None
    paid_date: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class OrgUserTokenCreateReq:
    email: str
    expire: int
    invalidate_old_tokens: bool = False

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SubmerchantCreateDTO:
    locale: Optional[str] = None
    conversation_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    gsm_number: Optional[str] = None
    address: Optional[str] = None
    iban: Optional[str] = None
    tax_office: Optional[str] = None
    legal_company_title: Optional[str] = None
    currency_id: Optional[str] = None
    sub_merchant_external_id: Optional[str] = None
    identity_number: Optional[str] = None
    sub_merchant_type: Optional[str] = None
    tax_number: Optional[str] = None
    sub_merchant_key: Optional[str] = None
    organization_id: Optional[str] = None
    status: Optional[str] = None
    system_time: Optional[int] = None
    contact_name: Optional[str] = None
    contact_surname: Optional[str] = None

    def to_dict(self) -> dict:
        return _asdict_factory(self)


@dataclass
class SubmerchantUpdateDTO(SubmerchantCreateDTO):
    pass


class FileResponse:
    def __init__(self, content: bytes, filename: str = "download"):
        self.content = content
        self.filename = filename

    def download(self, destination: Optional[str] = None):
        import os
        if destination is None:
            destination = os.path.join(os.getcwd(), self.filename)
        elif os.path.isdir(destination):
            destination = os.path.join(destination, self.filename)
        
        with open(destination, "wb") as f:
            f.write(self.content)
        return destination


@dataclass
class CreateOrganizationCurrencyPayload:
    currency_code: str

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
