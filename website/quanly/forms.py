from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import House, HouseImage, Tenant, Contract


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True, max_length=10)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control register-input',
            'placeholder': 'Tên đăng nhập',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control register-input',
            'placeholder': 'example@gmail.com',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control register-input',
            'placeholder': 'Số điện thoại',
            'inputmode': 'numeric',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control register-input',
            'placeholder': 'Mật khẩu',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control register-input',
            'placeholder': 'Nhập lại mật khẩu',
        })

        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email

    def clean_phone(self):
        phone = ''.join(ch for ch in (self.cleaned_data.get('phone') or '') if ch.isdigit())
        if len(phone) != 10:
            raise forms.ValidationError('Số điện thoại phải gồm đúng 10 chữ số.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        exclude = ['owner', 'status', 'created_at', 'updated_at', 'lat', 'lng']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nhà nguyên căn 3 phòng ngủ...'}),
            'house_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND/tháng'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            
            'address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Số nhà, tên đường, phường/xã...',
                'required': 'required'
            }),
            
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'owner_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'electricity_price': forms.TextInput(attrs={'class': 'form-control'}),
            'water_price': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_people': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'furniture': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
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