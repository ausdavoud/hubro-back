from decimal import Decimal

from django.db import DatabaseError, transaction

from common.models import DecisionPool, RippleTask
from common.views import exceptions as common_exceptions
from common.views.services import get_db_record_select_prefetch_or_404
from finance.models import FinancialAccount, Transaction
from finance.serializer import TransactionSerializer
from people.models import Team
from production.models import Factory, Production
from production.serializers import FactorySerializer, ProductionSerializer
from rd.models import DynamicRD


def new_factory(team: Team, decision: DecisionPool):
    factories = {
        "OW": {
            "ownership": Factory.OwnershipTypes.OWNED,
            "output_per_quarter": 1000,
            "build_cost": 100_000_00,
            "setup_time": 1,
            "outsourcing_fee_per_unit": 0,
            "labor_cost_per_unit": 58_00,
            "maintenance_cost_per_quarter": 20_000_00,
            "resale_value_percent": 70,
            "emissions_per_unit": 0.5,
            "depreciation_time": 20,
            "fixed_cost": 0,
            "workers": 0,
            "hours": 0,
            "wage": 0,
            "base": 1000,
        },
        "RN": {
            "ownership": Factory.OwnershipTypes.RENTED,
            "output_per_quarter": 1000,
            "build_cost": 30_000_00,
            "setup_time": 1,
            "outsourcing_fee_per_unit": 58_00,
            "labor_cost_per_unit": 0,
            "maintenance_cost_per_quarter": 15_000_00,
            "resale_value_percent": 0,
            "emissions_per_unit": 0.4,
            "depreciation_time": 0,
            "fixed_cost": 0,
            "workers": 0,
            "hours": 0,
            "wage": 0,
            "base": 1000,
        },
    }
    # Technically, the factory is built at the next quarter of the decision
    built_at_quarter = decision.made_at_quarter + 1
    ownership = decision.json_body["ownership"]
    factory_name = decision.json_body["factory_name"]
    factory = Factory.objects.create(
        team=team, name=factory_name, built_at_quarter=built_at_quarter, **factories[ownership]
    )
    serialized_factory = FactorySerializer(factory)
    return {"factory": serialized_factory.data}


def sell_factory(team: Team, factory_id: int, current_quarter: int):
    factory: Factory = get_db_record_select_prefetch_or_404(Factory, id=factory_id, team=team)

    if factory.ownership != Factory.OwnershipTypes.RENTED and factory.ownership != Factory.OwnershipTypes.OWNED:
        raise common_exceptions.ValidationError(description=f"Factory with id {factory_id} has unknown ownership type")
    try:
        with transaction.atomic():
            # delete productions related to this factory
            deleted_productions = Production.objects.filter(team=team, factory=factory).delete()

            # delete ripple tasks related to that production
            deleted_ripple_tasks = RippleTask.objects.filter(
                team=team,
                type=RippleTask.TaskTypes.PRODUCTION,
                json_body__factory_id=factory_id,
            ).delete()

            if factory.ownership == Factory.OwnershipTypes.RENTED:
                serialized_factory_data = FactorySerializer(factory).data
                factory.delete()
                return serialized_factory_data

            elif factory.ownership == Factory.OwnershipTypes.OWNED:
                sale_amount = Decimal(factory.resale_value_percent * factory.build_cost)
                loss_amount = Decimal(factory.build_cost - sale_amount)
                factories_account = get_db_record_select_prefetch_or_404(FinancialAccount, code=FinancialAccount.AccountNames.FACTORIES)
                loss_on_sale_of_assets_account = get_db_record_select_prefetch_or_404(
                    FinancialAccount,
                    code=FinancialAccount.AccountNames.LOSS_ON_SALE_OF_ASSETS
                )
                loss_credit_transaction = Transaction.objects.create(
                    team=team,
                    category=Transaction.Categories.LOSS_ON_SALE_OF_ASSETS,
                    quarter=current_quarter,
                    credit_amount=loss_amount,
                    debit_amount=0,
                    financial_account=factories_account,
                )

                loss_debit_transaction = Transaction.objects.create(
                    team=team,
                    category=Transaction.Categories.LOSS_ON_SALE_OF_ASSETS,
                    quarter=current_quarter,
                    credit_amount=0,
                    debit_amount=loss_amount,
                    financial_account=loss_on_sale_of_assets_account,
                )

                cash_account = get_db_record_select_prefetch_or_404(FinancialAccount, code=FinancialAccount.AccountNames.CASH)
                sale_credit_transaction = Transaction.objects.create(
                    team=team,
                    category=Transaction.Categories.SOLD_FACTORIES,
                    quarter=current_quarter,
                    credit_amount=sale_amount,
                    debit_amount=0,
                    financial_account=factories_account,
                )
                sale_debit_transaction = Transaction.objects.create(
                    team=team,
                    category=Transaction.Categories.SOLD_FACTORIES,
                    quarter=current_quarter,
                    credit_amount=0,
                    debit_amount=sale_amount,
                    financial_account=cash_account,
                )
                factory.delete()
    except DatabaseError:
        raise common_exceptions.AtomicTransactionError("sell factory")

    serialized_loss_credit_transaction = TransactionSerializer(loss_credit_transaction).data
    serialized_loss_debit_transaction = TransactionSerializer(loss_debit_transaction).data
    serialized_sale_credit_transaction = TransactionSerializer(sale_credit_transaction).data
    serialized_sale_debit_transaction = TransactionSerializer(sale_debit_transaction).data
    response = {
        "deleted_productions": deleted_productions,
        "deleted_ripple_tasks": deleted_ripple_tasks,
        "loss_credit_transaction": serialized_loss_credit_transaction,
        "loss_debit_transaction": serialized_loss_debit_transaction,
        "sale_credit_transaction": serialized_sale_credit_transaction,
        "sale_debit_transaction": serialized_sale_debit_transaction,
    }
    return response


def select_product(team: Team, decision: DecisionPool):
    json_body = decision.json_body
    current_quarter = decision.made_at_quarter
    factory_id = json_body["factory_id"]
    product_id = json_body["product_id"]

    factory: Factory = get_db_record_select_prefetch_or_404(Factory, id=factory_id, team=team)
    product: DynamicRD = get_db_record_select_prefetch_or_404(DynamicRD, id=product_id, team=team)

    try:
        try:
            production = Production.objects.get(
                team=team,
                factory=factory,
                quarter=current_quarter,
            )
            production.product = product
            production.save()
        except Production.DoesNotExist:
            production = Production.objects.create(
                team=team,
                factory=factory,
                quarter=current_quarter,
                product=product,
                activity_level=100,
                produced_quantity=0,
                labor_cost=999,
            )

        json_body = {
            "production_id": production.pk,
            "factory_id": factory.pk,
            "product_id": product.pk,
        }
        ripple_task = RippleTask.objects.create(
            team=team, run_at_quarter=current_quarter + 1, type=RippleTask.TaskTypes.PRODUCTION, json_body=json_body
        )

    except DatabaseError:
        raise common_exceptions.AtomicTransactionError("select product")
    serialized_production = ProductionSerializer(production)
    response = serialized_production.data
    return response


def set_activity_level(team: Team, decision: DecisionPool):
    json_body = decision.json_body
    factory_id = json_body["factory_id"]
    activity_level = json_body["activity_level"]

    factory: Factory = get_db_record_select_prefetch_or_404(Factory, id=factory_id, team=team)
    production: Production = get_db_record_select_prefetch_or_404(Production, team=team, factory=factory)

    production.activity_level = activity_level
    production.save()

    serialized_production = ProductionSerializer(production)
    return serialized_production.data
