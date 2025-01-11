from common.models import RippleTask
from common.views.exceptions import ValidationError
from django.db import DatabaseError, transaction
from common.views import exceptions as common_exceptions
from people.models import Player
from rest_framework import status
from rest_framework.response import Response


def enable_esg_reporting(player: Player):
    if player.state_variables.quarter < 3:
        raise ValidationError("Cannot enable ESG reporting before quarter 3.")
    if player.state_variables.esg_reporting_enabled:
        raise ValidationError("ESG reporting is already enabled.")
    try:
        with transaction.atomic():
            player.state_variables.esg_reporting_enabled = True
            json_body = {"amount": 8_000_00}
            RippleTask.objects.create(
                player=player,
                run_at_quarter=player.state_variables.quarter,
                type=RippleTask.TaskTypes.ESG_REPORTING,
                json_body=json_body,
            )
            player.state_variables.save()
    except DatabaseError:
        raise common_exceptions.AtomicTransactionError(state="Error at making a loan object")

    return Response("ESG reporting enabled.", status=status.HTTP_200_OK)
