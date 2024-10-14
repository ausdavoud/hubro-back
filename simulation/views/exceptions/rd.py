from rest_framework import status
from rest_framework.exceptions import APIException

from ...models.rd import RDStates


class RDStateError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, state: RDStates):
        detail = {
            "error": {"code": "0104", "description": "R&D item state is not available", "context": {"state": state}}
        }
        super().__init__(detail)
