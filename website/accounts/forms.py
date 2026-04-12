from django import forms
from django.contrib.auth.models import User

from accounts.models import Profile


class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['email'].disabled = True


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar']
        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nhập số điện thoại',
                    'maxlength': '10',
                }
            ),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError('Số điện thoại phải gồm đúng 10 chữ số.')
        return phone


class RegistrationOtpForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label='Mã OTP',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control register-input text-center',
                'placeholder': 'Nhập 6 chữ số OTP',
                'inputmode': 'numeric',
                'autocomplete': 'one-time-code',
            }
        ),
    )

    def clean_otp_code(self):
        code = (self.cleaned_data.get('otp_code') or '').strip()
        if not code.isdigit():
            raise forms.ValidationError('Mã OTP phải gồm đúng 6 chữ số.')
        return code


class ForgotPasswordEmailForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control register-input',
                'placeholder': 'example@gmail.com',
                'autocomplete': 'email',
            }
        ),
    )

    def clean_email(self):
        return (self.cleaned_data.get('email') or '').strip().lower()


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control register-input',
                'placeholder': 'Nhập mật khẩu mới',
                'autocomplete': 'new-password',
            }
        ),
    )
    confirm_new_password = forms.CharField(
        label='Xác nhận mật khẩu mới',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control register-input',
                'placeholder': 'Nhập lại mật khẩu mới',
                'autocomplete': 'new-password',
            }
        ),
    )
