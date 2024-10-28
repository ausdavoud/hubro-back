from django.db.models import Model
from rest_framework import status
from rest_framework.exceptions import APIException

from common.views.error_codes import ErrorCodes


class DatabaseRecordNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, model: Model, context: dict):
        detail = {
            "error": {
                "code": ErrorCodes.DATABASES_RECORD_NOT_FOUND_CODE,
                "description": "Database object not found",
                "context": {"database_model_name": model._meta.model_name, **context},
            }
        }
        super().__init__(detail)


class SerializerError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, serializer_errors):
        detail = {
            "error": {
                "code": ErrorCodes.SERIALIZER_ERROR_CODE,
                "description": "Serializer error",
                "context": {"serializer_errors": serializer_errors},
            }
        }
        super().__init__(detail)


class FinishQuarterError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, context: dict = {}):
        detail = {
            "error": {
                "code": ErrorCodes.FINISH_QUARTER_ERROR_CODE,
                "description": "Error while handling post quarter logic",
                "context": context,
            }
        }
        super().__init__(detail)


class DuplicateDecision(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, context: dict = {}):
        detail = {
            "error": {
                "code": ErrorCodes.DUPLICATE_DECISION_ERROR_CODE,
                "description": "You've already made the same decision at this quarter",
                "context": context,
            }
        }
        super().__init__(detail)


class AtomicTransactionError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, context: dict):
        detail = {
            "error": {
                "code": ErrorCodes.ATOMIC_TRANSACTION_ERROR_CODE,
                "description": "Failed during an integrated atomic transaction",
                "context": context,
            }
        }
        super().__init__(detail)
