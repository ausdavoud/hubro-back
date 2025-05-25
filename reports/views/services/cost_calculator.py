from django.db.models import F

from common.models import DecisionPool, RippleTask
from contracts.views.views import ContractView
from finance.models import BudgetCash
from finance.views.views import FinanceView
from people.models import Team
from production.views.services import factories
from production.views.views import ProductionView
from rd.models import DynamicRD
from rd.views.views import RDView


def get_started_rds(team: Team, quarter: int) -> list[DynamicRD]:
    decisions = DecisionPool.objects.filter(
        team=team, made_at_quarter=quarter, endpoint=RDView.ENDPOINTS.START_RD
    )
    rds = [
        DynamicRD.objects.get(
            team=team,
            category=d.json_body["category"],
            order=d.json_body["order"],
        )
        for d in decisions
    ]
    return rds


def get_ongoing_rds(team: Team) -> list[DynamicRD]:
    rds = DynamicRD.objects.filter(
        team=team,
        time_spent_developing__gt=0,
        development_duration__gt=F("time_spent_developing"),
    )
    return list(rds)


def get_amortization_cost_by_ripple_task(team: Team, quarter: int) -> float:
    ripple_tasks = RippleTask.objects.filter(
        team=team,
        type=RippleTask.TaskTypes.AMORTIZATION_OF_PROJECTS,
        run_at_quarter=quarter,
    )
    if not ripple_tasks.exists():
        return 0
    total = sum(float(task.json_body["amount"]) for task in ripple_tasks)
    return total


def get_factory_start_costs(team: Team, quarter: int) -> float:
    decisions = DecisionPool.objects.filter(
        team=team,
        made_at_quarter=quarter,
        endpoint=ProductionView.ENDPOINTS.NEW_FACTORY,
    )
    costs = 0
    for d in decisions:
        ownership = d.json_body["ownership"]
        costs = float(factories[ownership]["build_cost"])

    return costs


def get_factory_maintenance_cost(team: Team, quarter: int) -> float:
    ripple_tasks = RippleTask.objects.filter(
        team=team,
        run_at_quarter=quarter,
        type=RippleTask.TaskTypes.FACTORY_MAINTENANCE,
    )
    costs = 0
    for r in ripple_tasks:
        costs += float(r.json_body["maintenance_cost"])

    return costs


def get_loan_received(team: Team, quarter: int) -> float:
    decision = DecisionPool.objects.filter(
        team=team,
        made_at_quarter=quarter,
        endpoint=FinanceView.ENDPOINTS.NEW_LOAN,
    ).first()
    if not decision:
        return 0
    return float(decision.json_body["amount"])


def get_loan_interest(team: Team, quarter: int) -> float:
    ripple_tasks = RippleTask.objects.filter(
        team=team,
        run_at_quarter=quarter,
        type=RippleTask.TaskTypes.LOAN_INTEREST,
    )
    if not ripple_tasks.exists():
        return 0
    total = sum(float(task.json_body["amount"]) for task in ripple_tasks)
    return total


def get_loan_repayment(team: Team, quarter: int) -> float:
    ripple_tasks = RippleTask.objects.filter(
        team=team,
        run_at_quarter=quarter,
        type=RippleTask.TaskTypes.LOAN_REPAYMENT,
    )
    if not ripple_tasks.exists():
        return 0

    total = sum(float(task.json_body["amount"]) for task in ripple_tasks)
    return total


def get_esg_reporting_fee(team: Team, quarter: int) -> float:
    ripple_tasks = RippleTask.objects.filter(
        team=team,
        run_at_quarter=quarter,
        type=RippleTask.TaskTypes.ESG_REPORTING,
    )
    if not ripple_tasks.exists():
        return 0
    return sum(float(task.json_body["amount"]) for task in ripple_tasks)


def get_marketing_budget(team: Team, quarter: int) -> float:
    decision = DecisionPool.objects.filter(
        team=team,
        made_at_quarter=quarter,
        endpoint=ContractView.ENDPOINTS.SET_CONTRACTS_ORDER,
    ).first()
    if not decision:
        return 0
    return float(decision.json_body["marketing_budget"])


def get_budgeted_cash_by_quarter(
    team: Team, quarter: int, current_quarter: int
) -> float:
    """
    Calculate the costs and revenue for the current quarter based on the team's decisions.
    """
    budgeted_cash = (
        200_000_00
        if quarter == 1
        else float(
            BudgetCash.objects.get(team=team, quarter=quarter - 1).value
        )
    )
    if quarter != current_quarter:
        budgeted_cash = float(
            BudgetCash.objects.get(team=team, quarter=quarter).value
        )
        return budgeted_cash

    # else if this is all about the current quarter:

    # R&D
    # Find all decisions to start an r&d project to pay the first
    # portion of the payment (remember that the cost is divided by
    # the number of quarters it takes to finish the project)
    rds = get_started_rds(team=team, quarter=quarter)
    for rd in rds:
        budgeted_cash -= float(rd.development_cost) / float(
            rd.development_duration
        )

    # Find all on-going projects to reduce the cost
    # (similar to previous part)
    rds = get_ongoing_rds(team=team)
    for rd in rds:
        budgeted_cash -= float(rd.development_cost) / float(
            rd.development_duration
        )

    """I found out that in the real hubro, amortization of projects
    is not included in the budgeted cash. But let's include it here"""
    # Amortization: find the ripple task for current quarter
    budgeted_cash -= get_amortization_cost_by_ripple_task(
        team=team, quarter=quarter
    )

    # Production
    # Decision to build a factory
    budgeted_cash -= get_factory_start_costs(team=team, quarter=quarter)

    # Maintenance cost of a factory (After being built)
    # it is 20_000 for owned, 15_000 for rented
    budgeted_cash -= get_factory_maintenance_cost(team=team, quarter=quarter)

    # Materials
    # find the decision of supplier (if exists), use it as reference
    # cost per unit. Otherwise default to 100

    # outsourcing / labor cost
    # I could not find a proper formula. So I'll just multiply
    # activity level by the default cost defined in factory

    # Contracts
    # Find fulfilled contracts of the next quarter and add them up

    # Marketing budget by decision. defaults to 0
    budgeted_cash -= get_marketing_budget(team=team, quarter=quarter)

    # ESG INDEX
    # 8000 first quarter, 3000 next quarters if enabled
    budgeted_cash -= get_esg_reporting_fee(team=team, quarter=quarter)

    # Loan
    # Add the loan received by the team (decision)
    budgeted_cash += get_loan_received(team=team, quarter=quarter)

    # Repayment of the loan
    # if there's a ripple task for loan repayment, add it to the budgeted cash
    budgeted_cash -= get_loan_repayment(team=team, quarter=quarter)

    # interest of the loan
    # If there's a ripple task for loan interest, add it to the budgeted cash
    budgeted_cash -= get_loan_interest(team=team, quarter=quarter)

    return budgeted_cash
