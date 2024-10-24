from rest_framework import status
from rest_framework.exceptions import APIException

from common.views.error_codes import ErrorCodes
from rd.models import RDStates


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


class RDStartError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        detail = {
            "error": {
                "code": ErrorCodes.RD_START_ERROR,
                "description": detail,
            }
        }
        super().__init__(detail)


class RDResumeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        detail = {
            "error": {
                "code": ErrorCodes.RD_RESUME_ERROR,
                "description": detail,
            }
        }
        super().__init__(detail)


class RDPauseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        detail = {"error": {"code": ErrorCodes.RD_PAUSE_ERROR, "description": detail}}
        super().__init__(detail)
