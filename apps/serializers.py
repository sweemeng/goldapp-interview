from .models import Transaction
from .models import Balance
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):

    txref = serializers.CharField(required=False)

    class Meta:
        model = Transaction
        fields = ('type', 'amount', 'txref', 'asset')


