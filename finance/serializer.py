from rest_framework import serializers

from finance.models import FinancialAccount, Loan, Transaction


class NewLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["amount", "payback_period"]

    def validate(self, attrs):
        if attrs["payback_period"] not in [4, 8, 12, 16]:
            raise serializers.ValidationError("Payback period must be 4, 8, 12 or 16")
        if not 200_000_00 < attrs["amount"] < 2_000_000_00:  # Cents, not Dollars
            raise serializers.ValidationError("Amount must be between $200,000 and $1,000,000.")

        return super().validate(attrs)


class LoanSerializer(serializers.ModelSerializer):
    is_new = serializers.BooleanField(default=False)
    class Meta:
        model = Loan
        fields = "__all__"

class FinancialAcountSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = FinancialAccount
        fields = "__all__"

    def get_display_name(self, obj):
        return obj.get_code_display()

class TransactionSerializer(serializers.ModelSerializer):
    financial_account = FinancialAcountSerializer()
    class Meta:
        model = Transaction
        fields = "__all__"
