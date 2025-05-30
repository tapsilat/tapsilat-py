from dataclasses import asdict, dataclass
from typing import Any, List, Optional


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
    registration_address: Optional[str] = None
    registration_date: Optional[str] = None
    title: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class BasketItemPayerDTO:
    address: Optional[str] = None
    reference_id: Optional[str] = None
    tax_office: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    vat: Optional[str] = None


@dataclass
class BasketItemDTO:
    category1: Optional[str] = None
    category2: Optional[str] = None
    commission_amount: Optional[float] = None
    coupon: Optional[str] = None
    coupon_discount: Optional[float] = None
    data: Optional[str] = None
    id: Optional[str] = None
    item_type: Optional[str] = None
    name: Optional[str] = None
    paid_amount: Optional[float] = None
    payer: Optional[BasketItemPayerDTO] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    quantity_float: Optional[float] = None
    quantity_unit: Optional[str] = None
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


@dataclass
class CheckoutDesignDTO:
    input_background_color: Optional[str] = None
    input_text_color: Optional[str] = None
    label_text_color: Optional[str] = None
    left_background_color: Optional[str] = None
    logo: Optional[str] = None
    order_detail_html: Optional[str] = None
    pay_button_color: Optional[str] = None
    redirect_url: Optional[str] = None
    right_background_color: Optional[str] = None
    text_color: Optional[str] = None


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
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    country_iso_code: Optional[str] = None
    id: Optional[str] = None
    mcc: Optional[str] = None
    name: Optional[str] = None
    org_id: Optional[str] = None
    postal_code: Optional[str] = None
    submerchant_nin: Optional[str] = None
    submerchant_url: Optional[str] = None
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
class OrderCreateDTO:
    amount: float
    currency: str
    locale: str
    buyer: BuyerDTO
    basket_items: Optional[List[BasketItemDTO]] = None
    billing_address: Optional[BillingAddressDTO] = None
    checkout_design: Optional[CheckoutDesignDTO] = None
    conversation_id: Optional[str] = None
    enabled_installments: Optional[List[int]] = None
    external_reference_id: Optional[str] = None
    metadata: Optional[List[MetadataDTO]] = None
    order_cards: Optional[OrderCardDTO] = None
    paid_amount: Optional[float] = None
    partial_payment: Optional[bool] = None
    payment_failure_url: Optional[str] = None
    payment_methods: Optional[bool] = None
    payment_options: Optional[List[str]] = None
    payment_success_url: Optional[str] = None
    payment_terms: Optional[List[PaymentTermDTO]] = None
    pf_sub_merchant: Optional[OrderPFSubMerchantDTO] = None
    shipping_address: Optional[ShippingAddressDTO] = None
    sub_organization: Optional[SubOrganizationDTO] = None
    submerchants: Optional[List[SubmerchantDTO]] = None
    tax_amount: Optional[float] = None
    three_d_force: Optional[bool] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RefundOrderDTO:
    amount: float
    reference_id: str
    order_item_id: Optional[str] = None
    order_item_payment_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


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
        return asdict(self)

@dataclass
class OrderPaymentTermUpdateDTO:
    term_reference_id: str
    amount: Optional[float] = None
    due_date: Optional[str] = None
    paid_date: Optional[str] = None
    required: Optional[bool] = None
    status: Optional[str] = None
    term_sequence: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OrderTermRefundRequest:
    term_id: str
    amount: float
    reference_id: Optional[str] = None
    term_payment_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


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
