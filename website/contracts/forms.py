from django import forms
from .models import Tenant, Contract

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['full_name', 'phone', 'cccd', 'gender', 'dob', 'address', 'id_front_image', 'id_back_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'cccd': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['start_date', 'end_date', 'total_value', 'contract_document']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'total_value': forms.NumberInput(attrs={'class': 'form-control'}),
        }
