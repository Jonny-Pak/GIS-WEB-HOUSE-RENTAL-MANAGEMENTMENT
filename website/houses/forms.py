from django import forms
from .models import House, HouseImage


class SupportRequestForm(forms.Form):
    full_name = forms.CharField(
        max_length=120,
        label='Họ và tên',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: Nguyễn Văn A',
            }
        ),
    )
    contact_email = forms.EmailField(
        label='Email liên hệ',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'ban@email.com',
            }
        ),
    )
    subject = forms.CharField(
        max_length=180,
        label='Tiêu đề hỗ trợ',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Mô tả ngắn vấn đề bạn gặp phải',
            }
        ),
    )
    message = forms.CharField(
        label='Nội dung',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Vui lòng mô tả chi tiết để đội hỗ trợ phản hồi nhanh hơn.',
            }
        ),
    )

    def clean_full_name(self):
        value = self.cleaned_data['full_name'].strip()
        if len(value) < 2:
            raise forms.ValidationError('Vui lòng nhập họ tên hợp lệ.')
        return value

class HouseForm(forms.ModelForm):
    estimated_area_m2 = forms.FloatField(required=False, widget=forms.HiddenInput())
    polygon_geojson = forms.CharField(required=False, widget=forms.HiddenInput())

    AREA_TOLERANCE_RATIO = 0.10

    class Meta:
        model = House
        exclude = ['owner', 'status', 'created_at', 'updated_at', 'lat', 'lng', 'furniture', 'district']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nhà nguyên căn 3 phòng ngủ...'}),
            'house_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND/tháng'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VND'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}),

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

    def clean(self):
        cleaned_data = super().clean()

        area = cleaned_data.get('area')
        polygon_geojson = (self.data.get('polygon_geojson') or '').strip()
        estimated_area_raw = (self.data.get('estimated_area_m2') or '').strip()

        if not polygon_geojson:
            self.add_error('area', 'Vui lòng vẽ polygon trên bản đồ để hệ thống tính diện tích trước.')
            return cleaned_data

        try:
            estimated_area = float(estimated_area_raw)
        except (TypeError, ValueError):
            self.add_error('area', 'Không đọc được diện tích từ polygon. Vui lòng vẽ lại vùng đất.')
            return cleaned_data

        if estimated_area <= 0:
            self.add_error('area', 'Diện tích polygon không hợp lệ. Vui lòng vẽ lại vùng đất.')
            return cleaned_data

        if area is None:
            self.add_error('area', 'Diện tích là bắt buộc.')
            return cleaned_data

        tolerance = max(5.0, estimated_area * self.AREA_TOLERANCE_RATIO)
        difference = abs(float(area) - estimated_area)
        if difference > tolerance:
            self.add_error(
                'area',
                (
                    f'Diện tích nhập ({float(area):.1f} m²) vượt ngưỡng cho phép so với polygon '
                    f'({estimated_area:.1f} m²). Chỉ được lệch tối đa ±{tolerance:.1f} m².'
                ),
            )

        cleaned_data['estimated_area_m2'] = estimated_area
        return cleaned_data
