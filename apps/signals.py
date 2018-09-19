from .model import Asset
from .model import Balance
from django.contrib.auth.models import User


def init_balance(sender, instance, created, **kwargs):
    owners = User.objects.all()
    for owner in owners:
        try:
            balance = Balance.objects.get(owner__id=owner.id, asset__id=instance.id)
        except Balance.DoesNotExist:
            balance = Balance(asset=instance, owner=owner, amount=0.00)
            balance.save()



