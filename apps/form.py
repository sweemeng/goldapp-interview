from .models import Transaction
from django.forms import ModelForm


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'txref', 'asset', 'status']

    def clean_status(self):
        data = self.cleaned_data['status']
        if self.instance:
            status = self.instance.status
            # Should we handle this situation? for example revert REJECTED to PENDING because of error
            if status != Transaction.PENDING:
                raise forms.ValidationError("You cannot revert status")
        return data
                
