from rest_framework import status
from rest_framework.exceptions import APIException

from .error_codes import ErrorCodes

from ...models.rd import RDStates


class RDStateError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, state: RDStates):
        detail = {
            "error": {
                "code": ErrorCodes.RD_STATE_ERROR,
                "description": "R&D item state is not <available>",
                "context": {"state": state},
            }
        }
        super().__init__(detail)


class ResumeRDError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        super().__init__(detail)


class PauseRDError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        super().__init__(detail)
