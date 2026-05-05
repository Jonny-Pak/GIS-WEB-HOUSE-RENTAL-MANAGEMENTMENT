from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator as BaseUserAttributeSimilarityValidator,
    MinimumLengthValidator as BaseMinimumLengthValidator,
    CommonPasswordValidator as BaseCommonPasswordValidator,
    NumericPasswordValidator as BaseNumericPasswordValidator,
)

from django.core.exceptions import ValidationError

class UserAttributeSimilarityValidator(BaseUserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            return super().validate(password, user)
        except ValidationError:
            raise ValidationError('Mật khẩu không được giống với thông tin cá nhân.', code='password_too_similar')

class MinimumLengthValidator(BaseMinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            return super().validate(password, user)
        except ValidationError:
            raise ValidationError(f'Mật khẩu phải có ít nhất {self.min_length} ký tự.', code='password_too_short')

class CommonPasswordValidator(BaseCommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            return super().validate(password, user)
        except ValidationError:
            raise ValidationError('Mật khẩu quá đơn giản, hãy chọn mật khẩu khác.', code='password_too_common')

class NumericPasswordValidator(BaseNumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            return super().validate(password, user)
        except ValidationError:
            raise ValidationError('Mật khẩu phải bao gồm cả chữ và số.', code='password_entirely_numeric')
