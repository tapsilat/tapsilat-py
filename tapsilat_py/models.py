from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, List, Optional


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
    registration_address: Optional[str] = None


@dataclass
class BasketItemPayerDTO:
    address: Optional[str] = None
    reference_id: Optional[str] = None
    tax_office: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    vat: Optional[str] = None


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
    order_detail_html: Optional[str] = None
    right_background_color: Optional[str] = None
    text_color: Optional[str] = None
    pay_button_color: Optional[str] = None
    redirect_url: Optional[str] = None


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
    amount: Optional[float] = None
    data: Optional[str] = None
    due_date: Optional[str] = None
    paid_date: Optional[str] = None
    required: Optional[bool] = None
    status: Optional[str] = None
    term_reference_id: Optional[str] = None
    term_sequence: Optional[int] = None


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
