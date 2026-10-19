from typing import Any, Dict, Optional


class APIException(Exception):
    """Raised when a request fails or the API answers with an error.

    ``status_code`` is the HTTP status (0 when no response was received),
    ``code`` the ``code`` field of the error body (-1 when absent) and
    ``error`` the ``message`` field, falling back to ``error`` or the raw body.
    ``status``, ``errors`` and ``raw_body`` carry the body's ``status`` field,
    per-field validation messages and the unparsed response body.
    """

    def __init__(
        self,
        status_code: int,
        code: Any,
        error: str,
        status: Optional[str] = None,
        errors: Optional[Dict[str, Any]] = None,
        raw_body: Optional[str] = None,
    ):
        super().__init__(
            f"Tapsilat API Error\n status_code:{status_code}\ncode:{code}\nerror:{error}"
        )
        self.status_code = status_code
        self.code = code
        self.error = error
        self.message = error
        self.status = status
        self.errors = errors
        self.raw_body = raw_body
