import factory
from faker import Faker
from faker import Factory
from .models import Transaction
from .models import Asset
from .models import Balance
from django.contrib.auth.models import User

faker = Factory.create()
transaction_type_list = [ 'buy', 'sell', 'top_up', 'withdraw' ]


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username  = factory.Sequence(lambda n: 'username_{}'.format(n))
    email = faker.email()


class AssetFactory(factory.DjangoModelFactory):
    class Meta:
        model = Asset

    name         = faker.name()
    display_name = faker.name()
    cost         = faker.pyfloat(positive=True)


class CashFactory(factory.DjangoModelFactory):
    class Meta:
        model = Asset

    name         = "cash"
    display_name = "CASH"
    cost         = 1.00


class GoldFactory(factory.DjangoModelFactory):
    class Meta:
        model = Asset

    name         = "gold"
    display_name = "GLD"
    cost         = 10.00


class CashBalanceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Balance

    asset  = factory.SubFactory(CashFactory)
    owner  = factory.SubFactory(UserFactory)
    amount = faker.pyfloat(positive=True)


class GoldBalanceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Balance

    asset  = factory.SubFactory(GoldFactory)
    owner  = factory.SubFactory(UserFactory)
    amount = faker.pyfloat(positive=True)


class TransactionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Transaction

    type      = faker.word(ext_word_list=transaction_type_list)
    amount    = faker.pyfloat(positive=True)
    txref     = faker.uuid4()
    asset_obj = factory.SubFactory(AssetFactory)
    asset     = factory.SelfAttribute('asset_obj.name')

    owner     = factory.SubFactory(UserFactory)
    status    = faker.word(ext_word_list=["PENDING", "APPROVED", "DENIED"])


class BalanceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Balance

    asset  = factory.SubFactory(Asset)
    owner  = factory.SubFactory(User)
    amount = faker.pyfloat(positive=True)
