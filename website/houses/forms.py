from django import forms
from .models import House, HouseImage

class HouseForm(forms.ModelForm):
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
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
