from django import forms
from .models import House, HouseImage, Tenant, Contract

class HouseForm(forms.ModelForm):
    old_address = forms.CharField(
        required=False,
        label='Địa chỉ cũ',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Ví dụ: 12 Nguyen Huu Canh, P.22, Q.Binh Thanh',
            'id': 'id_old_address',
        }),
    )
    new_address = forms.CharField(
        required=False,
        label='Địa chỉ mới',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Ví dụ: 12 Nguyen Huu Canh, Phuong 22, Thanh pho Thu Duc',
            'id': 'id_new_address',
            'autocomplete': 'off',
        }),
        help_text='Chỉ cần nhập 1 trong 2 ô địa chỉ.',
    )

    # Dùng cho user/chủ nhà tự đăng bài
    class Meta:
        model = House
        exclude = ['owner', 'status', 'created_at', 'updated_at', 'lat', 'lng', 'furniture', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nhà nguyên căn 3 phòng ngủ...'}),
            'house_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND/tháng'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'owner_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'electricity_price': forms.TextInput(attrs={'class': 'form-control'}),
            'water_price': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_people': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.address:
            self.fields['new_address'].initial = self.instance.address

    def clean(self):
        cleaned_data = super().clean()
        old_address = (cleaned_data.get('old_address') or '').strip()
        new_address = (cleaned_data.get('new_address') or '').strip()

        if not old_address and not new_address:
            message = 'Vui lòng nhập ít nhất một địa chỉ (cũ hoặc mới).'
            self.add_error('old_address', message)
            self.add_error('new_address', message)
            return cleaned_data

        cleaned_data['resolved_address'] = new_address or old_address
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.address = self.cleaned_data.get('resolved_address', '').strip()
        if commit:
            instance.save()
            self.save_m2m()
        return instance

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
