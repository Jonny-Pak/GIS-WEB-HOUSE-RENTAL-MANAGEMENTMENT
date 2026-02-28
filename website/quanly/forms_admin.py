from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import House, Furniture, Contract, HouseImage


User = get_user_model()


class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, label="Mật khẩu")

    class Meta:
        model = User
        fields = ["username", "email", "password", "is_staff", "is_superuser", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class AdminUserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=6,
        required=False,
        label="Mật khẩu mới (để trống nếu không đổi)",
    )

    class Meta:
        model = User
        fields = ["username", "email", "is_staff", "is_superuser", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user


class AdminHouseForm(forms.ModelForm):
    class Meta:
        model = House
        exclude = ["created_at", "updated_at"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'house_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'owner_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'electricity_price': forms.TextInput(attrs={'class': 'form-control'}),
            'water_price': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_people': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class AdminFurnitureForm(forms.ModelForm):
    class Meta:
        model = Furniture
        fields = "__all__"

class AdminContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"


class AdminHouseImageForm(forms.ModelForm):
    class Meta:
        model = HouseImage
        fields = "__all__"


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "permissions"]
