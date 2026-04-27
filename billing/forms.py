from django import forms
from .models import Invoice
from .models import InvoiceItem




class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["booking", "issue_date", "due_date"]





class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["description", "quantity", "unit_price"]