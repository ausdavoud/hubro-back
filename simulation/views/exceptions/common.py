from django.db.models import Model
from rest_framework import status
from rest_framework.exceptions import APIException


class DatabaseRecordNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, model: Model, context: dict):
        detail = {
            "error": {
                "code": "0001",
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
                "code": "0002",
                "description": "Serializer error",
                "context": {"serializer_errors": serializer_errors},
            }
        }
        super().__init__(detail)
