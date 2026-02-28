from django import forms
from .models import House, HouseImage, Tenant, Contract

class HouseForm(forms.ModelForm):
    # Dùng cho user/chủ nhà tự đăng bài
    class Meta:
        model = House
        exclude = ['owner', 'status', 'created_at', 'updated_at', 'lat', 'lng', 'furniture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nhà nguyên căn 3 phòng ngủ...'}),
            'house_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND/tháng'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Số nhà, tên ngõ, tên đường...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'owner_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'electricity_price': forms.TextInput(attrs={'class': 'form-control'}),
            'water_price': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_people': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

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
