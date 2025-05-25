from decimal import Decimal


from ahmad.contracts import generate_contract_data
from common.management.data_fixtures import (
    BASIC_JETPACK_CONTRACT,
    GREEN_JETPACK_CONTRACT,
    SAFE_JETPACK_CONTRACT,
    SPORTY_JETPACK_CONTRACT,
)
from common.models import DecisionPool
from common.views.services import get_db_record_select_prefetch_or_404
from contracts.models import Contract, ContractAssignment, ContractPriority
from contracts.serializers import (
    ContractAssignmentSerializer,
    ContractPrioritySerializer,
)
from people.models import SimulationClass, Team
from rd.models import RDCategories
from rd.views.services import get_available_rd_dynamics_at_next_quarter


def create_contracts(simulation_class: SimulationClass):
    for JETPACK_CONTRACT in [
        BASIC_JETPACK_CONTRACT,
        SPORTY_JETPACK_CONTRACT,
        SAFE_JETPACK_CONTRACT,
        GREEN_JETPACK_CONTRACT,
    ]:
        for current_quarter in range(1, 14):
            if JETPACK_CONTRACT.get(current_quarter, None) is None:
                continue
            contracts = generate_contract_data(
                current_quarter,
                JETPACK_CONTRACT[current_quarter]["product_demand"],
                JETPACK_CONTRACT[current_quarter]["contracts"],
                JETPACK_CONTRACT[current_quarter]["contract_price_start"],
                JETPACK_CONTRACT[current_quarter]["contract_price_end"],
                JETPACK_CONTRACT[current_quarter]["required_esg_index"],
                JETPACK_CONTRACT["product_type"],
            )
            contracts_objs = [
                Contract(simulation_class=simulation_class, **contract)
                for contract in contracts
            ]
            contracts = Contract.objects.bulk_create(contracts_objs)


def set_contracts_order(team: Team, decision: DecisionPool) -> None:
    """
    This function sets the priority of the contracts of the team.
    """
    json_body = decision.json_body
    marketing_budget = json_body["marketing_budget"]
    contract_ids = json_body["contract_ids"]
    current_quarter = team.simulation_class.current_quarter
    team_esg_index = team.state_variables.esg_index
    simulation_class = team.simulation_class

    team.state_variables.marketing_budget = marketing_budget
    team.state_variables.save()

    contract_objs = []
    for index, contract_id in enumerate(contract_ids):
        contract = get_db_record_select_prefetch_or_404(
            Contract,
            id=contract_id,
            simulation_class=simulation_class,
            closure_quarter=current_quarter,
            minimum_esg_index__lte=team_esg_index,
        )
        contract_priority = ContractPriority(
            team=team,
            contract=contract,
            priority=index + 1,
            quarter=current_quarter,
        )
        contract_objs.append(contract_priority)

    contract_priorities = ContractPriority.objects.bulk_create(contract_objs)
    serialized_contract_priorities = ContractPrioritySerializer(
        contract_priorities, many=True
    )

    response = {
        "contract_priorities": serialized_contract_priorities.data,
        "marketing_budget": marketing_budget,
    }
    return response


def get_winner_teams(
    teams_info: list[tuple[Team, int, Decimal]],
) -> list[Team]:
    """
    `teams_info`: list of tuples (team object, esg index, marketing budget)

    Returns teams ordered by their esg and marketing budget.
    """
    teams_info.sort(
        key=lambda x: Decimal(0.1) * x[1] + Decimal(0.9) * x[2], reverse=True
    )
    return [team for team, _, _ in teams_info]


def assign_contracts_to_teams(
    teams: list[Team], current_quarter: int
) -> dict[int, list[Contract]]:
    """
    `teams_ids`: list of team_ids
    """

    contract_assignment_objs = []
    team_loads = {
        product_category: {team: 0 for team in teams}
        for product_category in RDCategories.values
    }
    # Teams choose contracts
    for team in teams:
        if team.team_type == Team.TeamType.BOT:
            next_available_contract = (
                Contract.objects.filter(
                    status=Contract.Statuses.PENDING,
                    closure_quarter=current_quarter,
                )
                .order_by("?")
                .last()
            )
            contract_assignment = ContractAssignment(
                team=team,
                contract=next_available_contract,
                status=ContractAssignment.Statuses.WAITING,
            )
            next_available_contract.status = Contract.Statuses.ASSIGNED
            next_available_contract.save()
            contract_assignment_objs.append(contract_assignment)
            team_loads[next_available_contract.deliverable_product][team] += 1
            continue

        contract_priorities = (
            ContractPriority.objects.filter(team=team, quarter=current_quarter)
            .order_by("priority")
            .all()
        )

        dynamic_rd_objects = get_available_rd_dynamics_at_next_quarter(
            team=team, current_quarter=current_quarter
        )
        available_products = {
            dynamic_rd.category for dynamic_rd in dynamic_rd_objects
        }
        for contract_priority in contract_priorities:
            if (
                contract_priority.contract.status == Contract.Statuses.ASSIGNED
                or contract_priority.contract.deliverable_product
                not in available_products
                or team.state_variables.marketing_budget < 5000
                or team.state_variables.esg_index
                < contract_priority.contract.minimum_esg_index
            ):
                continue

            contract_assignment = ContractAssignment(
                team=team,
                contract=contract_priority.contract,
                status=ContractAssignment.Statuses.WAITING,
            )
            contract_priority.contract.status = Contract.Statuses.ASSIGNED
            contract_priority.contract.save()
            contract_assignment_objs.append(contract_assignment)
            team_loads[contract_priority.contract.deliverable_product][
                team
            ] += 1
            break

    # Remaining contracts choose teams
    remaining_contracts = Contract.objects.filter(
        status=Contract.Statuses.PENDING, closure_quarter=current_quarter
    )
    for contract in remaining_contracts:
        eligible_teams = [
            team
            for team in teams
            if (
                team.team_type == Team.TeamType.BOT
                or team.rd.get(
                    category=contract.deliverable_product, order=1
                ).is_completed
            )
            and team.state_variables.marketing_budget >= 5000
            and team.state_variables.esg_index >= contract.minimum_esg_index
        ]

        if not eligible_teams:
            continue

        # Choose team with best ranking/load balance
        # FIXME: Possible #BUG
        """
        This algorithm chooses teams based on their load balance and then 
        if equal, based on their esg and marketing budget.
        You might want the company with the highest esg and marketing budget
        to get the contract, not the team with the lowest load balance.
        """
        team = min(
            eligible_teams,
            key=lambda t: (
                team_loads[contract.deliverable_product][t],
                Decimal(-0.1 * t.state_variables.esg_index)
                - Decimal(0.9) * t.state_variables.marketing_budget,
            ),
        )

        contract_assignment = ContractAssignment(
            team=team,
            contract=contract,
            status=ContractAssignment.Statuses.WAITING,
        )
        contract.status = Contract.Statuses.ASSIGNED
        contract.save()
        contract_assignment_objs.append(contract_assignment)
        team_loads[contract.deliverable_product][team] += 1

    contract_assignments = ContractAssignment.objects.bulk_create(
        contract_assignment_objs
    )
    serialized_contract_assignment = ContractAssignmentSerializer(
        contract_assignments, many=True
    )

    response = {
        "contract_assignments": serialized_contract_assignment.data,
    }
    return response
