from rest_framework.exceptions import APIException
from rest_framework import status

from common.views.error_codes import ErrorCodes


class InvalidQuarter(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
    ):
        detail = {
            "error": {
                "code": ErrorCodes.INVALID_QUARTER,
                "description": "Cannot access future (or previous to 1) quarters.",
            }
        }
        super().__init__(detail)
