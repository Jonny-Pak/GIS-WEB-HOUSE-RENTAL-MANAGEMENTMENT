from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
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


class ChangePasswordRequestForm(forms.Form):
    old_password = forms.CharField(
        label='Mật khẩu hiện tại',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control register-input',
                'placeholder': 'Nhập mật khẩu hiện đang sử dụng',
                'autocomplete': 'current-password',
            }
        ),
    )
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


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Tên đăng nhập hoặc email hoặc mật khẩu không đúng.',
        'inactive': 'Tài khoản này đang bị vô hiệu hóa.',
    }

    def clean(self):
        username_input = (self.cleaned_data.get('username') or '').strip()
        password = self.cleaned_data.get('password')

        if not username_input:
            raise forms.ValidationError('Vui lòng nhập tên đăng nhập hoặc email.', code='required')
        if not password:
            raise forms.ValidationError('Vui lòng nhập mật khẩu.', code='required')

        if username_input and '@' in username_input:
            matched_user = User.objects.filter(email__iexact=username_input).order_by('id').first()
            if matched_user is not None:
                username_input = matched_user.get_username()

        if username_input and password:
            self.user_cache = authenticate(
                self.request,
                username=username_input,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            self.confirm_login_allowed(self.user_cache)

        self.cleaned_data['username'] = username_input
        return self.cleaned_data
