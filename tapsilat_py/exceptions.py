class APIException(Exception):
    def __init__(self, status_code: int, code: int, error: str):
        super().__init__(
            f"Tapsilat API Error\n status_code:{status_code}\ncode:{code}\nerror:{error}"
        )
        self.status_code = status_code
        self.code = code
        self.error = error
