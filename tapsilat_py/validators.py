from typing import List

from .exceptions import APIException


def validate_installments(installments_str: str) -> List[int]:
    """
    Validate and parse installments string. Returns list of valid installment string
    """
    if not installments_str:
        return [1]
    try:
        installments = [int(x.strip()) for x in installments_str.split(',')]
        for installment in installments:
            if installment < 1 or installment > 12:
                raise APIException(
                    status_code=400,
                    code=0,
                    error=f"Installment value '{installment}' is invalid. All installment values must be between 1 and 12 (inclusive)."
                )
        return installments if installments else [1]
    except ValueError:
        raise APIException(
            status_code=400,
            code=0,
            error="Enabled installments must be comma-separated integers (e.g., 1,2,3 or 2,4,6)"
        )
    except AttributeError:
        return [1]


def validate_gsm_number(phone: str) -> str:
    """
    Validate GSM number format internationally.
    Returns the cleaned phone sequence if valid.
    """
    if not phone:
        return phone

    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    if not clean_phone.replace('+', '').isdigit():
        raise APIException(
            status_code=400,
            code=0,
            error=f"Invalid phone number format: {phone}"
        )

    return clean_phone
