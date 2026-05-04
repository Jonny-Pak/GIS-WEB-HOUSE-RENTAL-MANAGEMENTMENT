from django import forms
from django.db import models
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

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            qs = Tenant.objects.filter(phone=phone)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Số điện thoại này đã được đăng ký cho một khách thuê khác.")
        return phone

    def clean_cccd(self):
        cccd = self.cleaned_data.get('cccd')
        if cccd:
            qs = Tenant.objects.filter(cccd=cccd)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Số CCCD này đã tồn tại trên hệ thống.")
        return cccd

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['start_date', 'end_date', 'total_value', 'contract_document']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'total_value': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        house = cleaned_data.get('house') or getattr(self.instance, 'house', None)

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")

        # Kiểm tra trùng lặp hợp đồng còn hiệu lực cho cùng một nhà
        if house and start_date and end_date:
            overlapping_contracts = Contract.objects.filter(
                house=house,
                status='active',
            ).exclude(pk=self.instance.pk if self.instance else None)

            # Kiểm tra xem khoảng thời gian mới có chồng lấn với bất kỳ hợp đồng active nào không
            # Chỗ này dùng logic: (StartA <= EndB) and (EndA >= StartB)
            overlapping_contracts = overlapping_contracts.filter(
                models.Q(start_date__lte=end_date, end_date__gte=start_date)
            )

            if overlapping_contracts.exists():
                raise forms.ValidationError(
                    f"Căn nhà này đã có hợp đồng đang hiệu lực trong khoảng thời gian từ "
                    f"{overlapping_contracts.first().start_date} đến {overlapping_contracts.first().end_date}. "
                    "Vui lòng kiểm tra lại."
                )

        return cleaned_data
