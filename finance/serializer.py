from rest_framework import serializers

from finance.models import FinancialAccount, Loan, Transaction


class NewLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["amount", "payback_period"]

    def validate(self, attrs):
        if attrs["payback_period"] not in [4, 8, 12, 16]:
            raise serializers.ValidationError("Payback period must be 4, 8, 12 or 16")
        if attrs["amount"] > 100_000_000:  # Cents, not Dollars
            raise serializers.ValidationError("Amount must be less than 100_000_000")

        return super().validate(attrs)


class LoanSerializer(serializers.ModelSerializer):
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
