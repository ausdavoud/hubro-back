from rest_framework import serializers

from finance.models import Loan, Transaction


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


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
