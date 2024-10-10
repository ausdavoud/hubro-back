from ...models.people import CustomUser


class CommonErrorCodes:
    @staticmethod
    def PLAYER_NOT_FOUND(user: CustomUser):
        return {"code": "0001", "description": "Player not found", "context": {"user_email": user.email}}

    @staticmethod
    def SERIALIZER_ERROR(serializer_errors):
        return {"code": "0002", "description": "Serializer error", "context": {"serializer_errors": serializer_errors}}
