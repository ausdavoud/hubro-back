from typing import Any

from django.core.management.base import BaseCommand

from contracts.models import Contract, ContractPriority
from contracts.views.services import (
    assign_contracts_to_teams,
    get_winner_teams,
)
from people.models import Player
from rd.models import DynamicRD, RDCategories


class Command(BaseCommand):
    help = "Simulate contract distribution for all teams."

    def handle(self, *args: Any, **options: Any) -> str | None:
        player_h = Player.objects.get(user__email="h@g.com")
        player_a = Player.objects.get(user__email="a@g.com")
        player_m = Player.objects.get(user__email="m@g.com")
        # move users to quarter 8 (green is available from q8)
        player_h.state_variables.quarter = 8
        player_a.state_variables.quarter = 8
        player_m.state_variables.quarter = 8
        player_h.state_variables.save()
        player_a.state_variables.save()
        player_m.state_variables.save()

        # unlock r&d for them
        # user h
        basic_jetpack = DynamicRD.objects.get(
            player=player_h, category=RDCategories.BASIC, order=1
        )
        basic_jetpack.started_at = 8
        basic_jetpack.time_spent_developing = 1
        basic_jetpack.save()
        sporty_jetpack = DynamicRD.objects.get(
            player=player_h, category=RDCategories.SPORTY, order=1
        )
        sporty_jetpack.started_at = 8
        sporty_jetpack.time_spent_developing = 2
        sporty_jetpack.save()
        safe_jetpack = DynamicRD.objects.get(
            player=player_h, category=RDCategories.SAFE, order=1
        )
        safe_jetpack.started_at = 8
        safe_jetpack.time_spent_developing = 2
        safe_jetpack.save()

        # user a
        safe_jetpack = DynamicRD.objects.get(
            player=player_a, category=RDCategories.SAFE, order=1
        )
        safe_jetpack.started_at = 8
        safe_jetpack.time_spent_developing = 2
        safe_jetpack.save()
        green_jetpack = DynamicRD.objects.get(
            player=player_a, category=RDCategories.GREEN, order=1
        )
        green_jetpack.started_at = 8
        green_jetpack.time_spent_developing = 3
        green_jetpack.save()
        green_jetpack = DynamicRD.objects.get(
            player=player_a, category=RDCategories.GREEN, order=1
        )
        green_jetpack.started_at = 8
        green_jetpack.time_spent_developing = 3
        green_jetpack.save()

        # user h
        basic_jetpack = DynamicRD.objects.get(
            player=player_m, category=RDCategories.BASIC, order=1
        )
        basic_jetpack.started_at = 8
        basic_jetpack.time_spent_developing = 1
        basic_jetpack.save()
        sporty_jetpack = DynamicRD.objects.get(
            player=player_m, category=RDCategories.SPORTY, order=1
        )
        sporty_jetpack.started_at = 8
        sporty_jetpack.time_spent_developing = 2
        sporty_jetpack.save()
        green_jetpack = DynamicRD.objects.get(
            player=player_m, category=RDCategories.GREEN, order=1
        )
        green_jetpack.started_at = 8
        green_jetpack.time_spent_developing = 3
        green_jetpack.save()

        # move to quarter 11 to get r&d done
        player_h.state_variables.quarter = 11
        player_a.state_variables.quarter = 11
        player_m.state_variables.quarter = 11

        # set marketing budget
        player_h.state_variables.marketing_budget = 100000
        player_a.state_variables.marketing_budget = 900000
        player_m.state_variables.marketing_budget = 130000
        player_h.state_variables.save()
        player_a.state_variables.save()
        player_m.state_variables.save()

        # teams set priority
        # player h
        basic_contracts = Contract.objects.filter(
            closure_quarter=11, deliverable_product=RDCategories.BASIC
        ).order_by("?")
        safe_contracts = Contract.objects.filter(
            closure_quarter=11, deliverable_product=RDCategories.SAFE
        ).order_by("?")
        priority = 1
        for basic_contract in basic_contracts:
            ContractPriority.objects.create(
                player=player_h,
                contract=basic_contract,
                priority=priority,
                quarter=11,
            )
            priority += 1
        priority = 1
        for safe_contract in safe_contracts:
            ContractPriority.objects.create(
                player=player_h,
                contract=safe_contract,
                priority=priority,
                quarter=11,
            )
            priority += 1

        # player a
        safe_contracts = Contract.objects.filter(
            closure_quarter=11, deliverable_product=RDCategories.SAFE
        ).order_by("?")
        green_contracts = Contract.objects.filter(
            closure_quarter=11, deliverable_product=RDCategories.GREEN
        ).order_by("?")
        priority = 1
        for safe_contract in safe_contracts:
            ContractPriority.objects.create(
                player=player_a,
                contract=safe_contract,
                priority=priority,
                quarter=11,
            )
            priority += 1
        priority = 1
        for green_contract in green_contracts:
            ContractPriority.objects.create(
                player=player_a,
                contract=green_contract,
                priority=priority,
                quarter=11,
            )
            priority += 1

        # player m
        green_contracts = Contract.objects.filter(
            closure_quarter=11, deliverable_product=RDCategories.GREEN
        ).order_by("?")
        sporty_contracts = Contract.objects.filter(
            closure_quarter=11, deliverable_product=RDCategories.SPORTY
        ).order_by("?")
        priority = 1
        for green_contract in green_contracts:
            ContractPriority.objects.create(
                player=player_m,
                contract=green_contract,
                priority=priority,
                quarter=11,
            )
            priority += 1
        priority = 1
        for sporty_contract in sporty_contracts:
            ContractPriority.objects.create(
                player=player_m,
                contract=sporty_contract,
                priority=priority,
                quarter=11,
            )
            priority += 1

        # find winner teams
        sorted_teams = get_winner_teams(
            [
                (
                    player,
                    player.state_variables.esg_index,
                    player.state_variables.marketing_budget,
                )
                for player in [player_h, player_a, player_m]
            ]
        )
        self.stdout.write(str(sorted_teams))
        # assign contracts
        response = assign_contracts_to_teams(
            sorted_teams, current_quarter=11, handler=self
        )
        self.stdout.write(str(response))
