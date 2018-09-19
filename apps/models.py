from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import signals
from django.dispatch import receiver
from django.db.models import F
import uuid


# Because there might be multiple assets
class Asset(models.Model):
    name         = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    # Cash will cost 1 everytime, 
    cost         = models.FloatField()


class Transaction(models.Model):
    SELL     = 'sell'
    BUY      = 'buy'
    WITHDRAW = 'withdraw'
    TOP_UP   = 'top_up'

    TX_TYPE_CHOICE = (
        (SELL,     'sell'),
        (BUY,      'buy'),
        (WITHDRAW, 'buy'),
        (TOP_UP,   'topup'),
    )
    APPROVED = 'APPROVED'
    PENDING  = 'PENDING'
    DENIED   = 'DENIED'

    STATUS_CHOICE = (
        ( PENDING,  'PENDING'),
        ( APPROVED, 'APPROVED'),
        ( DENIED,   'DENIED'),
    )

    type       = models.CharField(
        max_length=10,
        choices=TX_TYPE_CHOICE
    )
    amount     = models.FloatField()
    txref      = models.CharField(max_length=255)
    asset      = models.CharField(max_length=255)
    asset_obj  = models.ForeignKey(Asset, on_delete=models.CASCADE)
    owner      = models.ForeignKey(User, on_delete=models.CASCADE)
    status     = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default=PENDING
    )

    def save(self, *args, **kwargs):
        self.txref = str(uuid.uuid4())
        asset = Asset.objects.get(name=self.asset)
        
        self.asset_obj = asset
        super().save(*args, **kwargs)


class Balance(models.Model):
    asset  = models.ForeignKey(Asset, on_delete=models.CASCADE)
    owner  = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.00)
    

def init_balance(sender, instance, created, **kwargs):
    if created:
        owners = User.objects.all()
        for owner in owners:
            try:
                balance = Balance.objects.get(owner__id=owner.id, asset__id=instance.id)
            except Balance.DoesNotExist:
                balance = Balance(asset=instance, owner=owner, amount=0.00)
                balance.save()


def set_user_initial_balance(sender, instance, created, **kwargs):
    if created:
        assets = Asset.objects.all()
        for asset in assets:
            try:
                balance = Balance.objects.get(owner=instance, asset=asset)
            except Balance.DoesNotExist:
                balance = Balance(asset=asset, owner=instance, amount=0.00)
                balance.save()


def verify_balance(sender, instance, raw, **kwargs):
    if instance.type == sender.BUY: 
        owner = instance.owner
        cash = Asset.objects.get(name="cash")
        asset = Asset.objects.get(name=instance.asset)
        balance = Balance.objects.get(owner__id=owner.id, asset__id=cash.id)
        amount = balance.amount
        cost = instance.amount * asset.cost
        if amount < cost:
            instance.status = sender.DENIED
    elif instance.type == sender.SELL:
        owner = instance.owner
        asset = Asset.objects.get(name=instance.asset)
        balance = Balance.objects.get(owner=owner, asset=asset)
        amount = balance.amount
        if amount < instance.amount:
            instance.status = sender.DENIED
    elif instance.type == sender.WITHDRAW:
        owner = instance.owner
        asset = Asset.objects.get(name=instance.asset)
        balance = Balance.objects.get(owner=owner, asset=asset)
        amount = balance.amount
        if amount < instance.amount:
            instance.status = sender.DENIED


def set_balance(sender, instance, created, **kwargs):
    # not created is important, only set for update only. 
    if not created:
        # update to reject or approved, but not in reverse
        # ignore if reject
        # maybe get cancel status if needed
        if instance.status == Transaction.APPROVED:
            owner = instance.owner
            asset = instance.asset_obj
            balance = Balance.objects.get(owner__id=owner.id, asset__id=asset.id)
            cash = Asset.objects.get(name="cash")
            cash_balance = Balance.objects.get(owner__id=owner.id, asset__id=cash.id)
            cost = asset.cost * instance.amount

            if instance.type == 'buy':
                cash_balance.amount = F('amount') - cost
                balance.amount = F('amount') + instance.amount

            if instance.type == 'sell':
                cash_balance.amount = F('amount') + cost
                balance.amount = F('amount') - instance.amount

            if instance.type == 'top_up':
                cash_balance.amount = F('amount') + cost
                balance.amount = F('amount') + 0

            if instance.type == 'withdraw':
                cash_balance.amount = F('amount') - cost
                balance.amount = F('amount') - 0

            cash_balance.save()
            balance.save()


signals.post_save.connect(receiver=init_balance, sender=Asset)
signals.pre_save.connect(receiver=verify_balance, sender=Transaction)
signals.post_save.connect(receiver=set_balance, sender=Transaction)
signals.post_save.connect(receiver=set_user_initial_balance, sender=User)
