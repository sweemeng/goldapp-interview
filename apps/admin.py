from django.contrib import admin
from .models import Transaction
from .models import Asset
from .form import TransactionForm


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionForm


class AssetAdmin(admin.ModelAdmin):
    pass


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Asset, AssetAdmin)
