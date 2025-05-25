from rest_framework import serializers


class CashFlowReportSerializer(serializers.Serializer):
    """
    Serializer for the Cash Flow Report response data.
    """

    class CashFlowDataSerializer(serializers.Serializer):
        operating_activities = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            help_text="Cash flow from operating activities",
        )
        investing_activities = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            help_text="Cash flow from investing activities",
        )
        financing = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            help_text="Cash flow from financing activities",
        )

    data = CashFlowDataSerializer(
        help_text="Cash flow report data by category"
    )


class MarketReportSerializer(serializers.Serializer):
    class ContractFulfillmentSerializer(serializers.Serializer):
        """
        Serializer for individual contract fulfillment data.
        """

        contract_id = serializers.IntegerField(help_text="ID of the contract")
        product = serializers.IntegerField(
            help_text="ID of the deliverable product"
        )
        storage = serializers.FloatField(
            help_text="Available quantity of the product in storage"
        )
        desired = serializers.FloatField(
            help_text="Quantity desired/required by the contract"
        )

    """
    Serializer for the market report response data structure.
    """
    data = serializers.ListField(
        child=ContractFulfillmentSerializer(),
        help_text="Contract fulfillment data keyed by contract ID",
    )


class ProductionReportDataSerializer(serializers.Serializer):
    """
    Serializer for production report details.
    """

    product_category = serializers.CharField(
        help_text="Category of the product being produced"
    )
    product_alias = serializers.CharField(
        help_text="Alias/name of the product being produced"
    )
    produced_quantity = serializers.FloatField(
        help_text="Total quantity produced"
    )
    material_cost_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Material cost per unit"
    )
    material_cost_total = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total material cost"
    )
    labor_cost_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Labor cost per unit"
    )
    labor_cost_total = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total labor cost"
    )
    outsourcing_fee_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Outsourcing fee per unit"
    )
    outsourcing_fee_total = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total outsourcing fee"
    )
    variable_costs_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Variable costs per unit"
    )
    variable_costs_total = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total variable costs"
    )
    fixed_cost_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Fixed cost per unit"
    )
    fixed_cost_total = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total fixed costs"
    )
    total_cost_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total cost per unit"
    )
    total_cost_total = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total overall cost"
    )
    depreciation_this_quarter = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Depreciation amount for this quarter",
    )
    factory_current_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Current value of the factory",
    )
    stored_quantity = serializers.IntegerField(
        help_text="Quantity currently stored"
    )
    materials_emission_total = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total emissions from materials",
    )
    production_emission_total = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total emissions from production",
    )
    total_emission = serializers.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total emissions"
    )
    total_demand = serializers.IntegerField(help_text="Total product demand")


class ProductionReportErrorSerializer(serializers.Serializer):
    """
    Serializer for production report error response.
    """

    fixed_cost_total = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Fixed costs total even when no product is selected",
    )
    error = serializers.CharField(
        help_text="Error message when no product is selected"
    )


class ProductionReportSerializer(serializers.Serializer):
    """
    Serializer for the production report response.
    """

    data = ProductionReportDataSerializer(help_text="Production report data")
    error = serializers.CharField(
        help_text="Error message if applicable", required=False
    )


class QuarterlyReportSerializer(serializers.Serializer):
    revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    gross_profit = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    gross_profit_margin = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    net_income = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    net_profit_margin = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
