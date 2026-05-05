from django.contrib import messages
from django.contrib.messages import get_messages
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.utils import timezone

from datetime import timedelta

from accounts.forms import ForgotPasswordEmailForm, RegistrationOtpForm, ResetPasswordForm
from accounts.models import EmailOTP, Profile


REGISTER_PENDING_SESSION_KEY = 'register_pending_data'
RESET_PENDING_SESSION_KEY = 'reset_password_pending_data'
OTP_EXPIRY_MINUTES = 10


def _build_register_context(reg_errors=None, form_data=None):
    return {
        'reg_errors': reg_errors or [],
        'form_data': form_data or {},
    }


def _normalize_phone(phone):
    return ''.join(ch for ch in (phone or '') if ch.isdigit())


def _send_registration_otp_email(email, otp_code, username):
    subject = '[CHO THUÊ NHÀ] Mã OTP xác thực tài khoản'
    body = (
        'Xin chào,\n\n'
        f'Bạn đang đăng ký tài khoản: {username}\n'
        f'Mã OTP xác thực của bạn là: {otp_code}\n\n'
        f'Mã OTP này sẽ có hiệu lực trong {OTP_EXPIRY_MINUTES} phút.\n'
        'Nếu bạn không yêu cầu đăng ký, vui lòng bỏ qua email này.\n\n'
        'Trân trọng,\nHệ thống Thuê Nhà'
    )
    email_message = EmailMessage(
        subject=subject,
        body=body,
        to=[email],
    )
    email_message.send(fail_silently=False)


def _send_reset_password_otp_email(email, otp_code, username):
    subject = '[CHO THUE NHA] Ma OTP dat lai mat khau'
    body = (
        'Xin chào,\n\n'
        f'Bạn đang yêu cầu đặt lại mật khẩu cho tài khoản: {username}\n'
        f'Mã OTP xác thực của bạn là: {otp_code}\n\n'
        f'Mã OTP này sẽ có hiệu lực trong {OTP_EXPIRY_MINUTES} phút.\n'
        'Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.\n\n'
        'Trân trọng,\nHệ thống Thuê Nhà'
    )
    EmailMessage(
        subject=subject,
        body=body,
        to=[email],
    ).send(fail_silently=False)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        reg_errors = []
        form_data = {
            'username': username,
            'email': email,
            'phone': phone,
        }

        if not username:
            reg_errors.append('Tên đăng nhập không được để trống.')
        if not email:
            reg_errors.append('Email không được để trống.')
        if not phone:
            reg_errors.append('Số điện thoại không được để trống.')

        normalized_phone = _normalize_phone(phone)
        if normalized_phone and len(normalized_phone) != 10:
            reg_errors.append('Số điện thoại phải gồm đúng 10 chữ số.')

        if password != confirm_password:
            reg_errors.append('Mật khẩu xác nhận không khớp.')
        else:
            try:
                validate_password(password)
            except ValidationError as exc:
                reg_errors.extend(exc.messages)

        if User.objects.filter(username__iexact=username).exists():
            reg_errors.append('Tên đăng nhập đã tồn tại.')

        if User.objects.filter(email__iexact=email).exists():
            reg_errors.append('Email đã được sử dụng.')

        if reg_errors:
            return render(request, 'accounts/register.html', _build_register_context(reg_errors, form_data))

        expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        otp_code = EmailOTP.generate_unique_code()

        EmailOTP.objects.filter(
            email=email,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        ).update(used_at=timezone.now())

        otp_record = EmailOTP.objects.create(
            email=email,
            code=otp_code,
            expires_at=expires_at,
        )

        request.session[REGISTER_PENDING_SESSION_KEY] = {
            'username': username,
            'email': email,
            'phone': normalized_phone,
            'password': password,
            'otp_id': otp_record.id,
            'expires_at': expires_at.isoformat(),
        }
        request.session.modified = True

        try:
            _send_registration_otp_email(email=email, otp_code=otp_code, username=username)
        except Exception as exc:
            error_text = str(exc)
            is_mailtrap_demo_error = 'Demo domains can only be used' in error_text

            if is_mailtrap_demo_error and settings.DEBUG:
                # Clear old queued messages so only the latest OTP demo notice is shown.
                list(get_messages(request))
                messages.warning(
                    request,
                    'Mailtrap demo không thể gửi email ra ngoài. '
                    f'(Môi trường dev) Mã OTP của bạn là: {otp_code}'
                )
                return redirect('register_verify_otp')

            otp_record.delete()
            request.session.pop(REGISTER_PENDING_SESSION_KEY, None)

            if is_mailtrap_demo_error:
                reg_errors.append(
                    'Mailtrap đang ở chế độ demo: chỉ gửi được tới email chủ tài khoản Mailtrap. '
                    'Vui lòng dùng email chủ tài khoản Mailtrap hoặc cấu hình SMTP Mailtrap để gửi ra ngoài.'
                )
            else:
                reg_errors.append('Không thể gửi mã OTP lúc này. Vui lòng thử lại sau.')

            return render(request, 'accounts/register.html', _build_register_context(reg_errors, form_data))

        messages.info(request, f'Đã gửi mã OTP đến email {email}. Vui lòng nhập mã để hoàn tất đăng ký.')
        return redirect('register_verify_otp')

    return render(request, 'accounts/register.html', _build_register_context())


def register_verify_otp(request):
    def _render_otp_page(form, pending_email='', pending_username=''):
        return render(request, 'accounts/register_verify_otp.html', {
            'otp_form': form,
            'pending_email': pending_email,
            'pending_username': pending_username,
            'otp_expiry_minutes': OTP_EXPIRY_MINUTES,
        })

    pending_data = request.session.get(REGISTER_PENDING_SESSION_KEY)
    if not pending_data:
        messages.warning(request, 'Phiên xác thực OTP không còn hiệu lực. Vui lòng đăng ký lại.')
        return _render_otp_page(RegistrationOtpForm())

    email = pending_data.get('email', '')
    username = pending_data.get('username', '')

    if request.method == 'POST':
        form = RegistrationOtpForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            now = timezone.now()

            otp_record = EmailOTP.objects.filter(
                id=pending_data.get('otp_id'),
                email=email,
                code=otp_code,
                used_at__isnull=True,
                expires_at__gt=now,
            ).first()

            if otp_record is None:
                messages.error(request, 'Mã OTP không đúng hoặc đã hết hạn. Vui lòng kiểm tra lại.')
            else:
                if User.objects.filter(username__iexact=username).exists():
                    request.session.pop(REGISTER_PENDING_SESSION_KEY, None)
                    messages.error(request, 'Tên đăng nhập đã tồn tại. Vui lòng quay lại đăng ký.')
                    return _render_otp_page(form, pending_email=email, pending_username=username)

                if User.objects.filter(email__iexact=email).exists():
                    request.session.pop(REGISTER_PENDING_SESSION_KEY, None)
                    messages.error(request, 'Email đã được sử dụng. Vui lòng quay lại đăng ký.')
                    return _render_otp_page(form, pending_email=email, pending_username=username)

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=pending_data.get('password', ''),
                )
                Profile.objects.update_or_create(
                    user=user,
                    defaults={'phone': pending_data.get('phone', '')},
                )

                otp_record.used_at = now
                otp_record.save(update_fields=['used_at'])
                EmailOTP.objects.filter(
                    email=email,
                    used_at__isnull=True,
                ).update(used_at=now)

                request.session.pop(REGISTER_PENDING_SESSION_KEY, None)
                messages.success(request, 'Xác thực OTP thành công. Bạn có thể đăng nhập ngay bây giờ.')
                return redirect('login')
    else:
        form = RegistrationOtpForm()

    return _render_otp_page(form, pending_email=email, pending_username=username)


def forgot_password_request(request):
    form = ForgotPasswordEmailForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            messages.error(request, 'Email chưa được đăng ký tài khoản.')
        else:
            expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
            otp_code = EmailOTP.generate_unique_code()

            EmailOTP.objects.filter(
                email=user.email,
                used_at__isnull=True,
                expires_at__gt=timezone.now(),
            ).update(used_at=timezone.now())

            otp_record = EmailOTP.objects.create(
                email=user.email,
                code=otp_code,
                expires_at=expires_at,
            )

            request.session[RESET_PENDING_SESSION_KEY] = {
                'email': user.email,
                'user_id': user.id,
                'otp_id': otp_record.id,
                'expires_at': expires_at.isoformat(),
                'otp_verified': False,
            }
            request.session.modified = True

            try:
                _send_reset_password_otp_email(
                    email=user.email,
                    otp_code=otp_code,
                    username=user.username,
                )
            except Exception as exc:
                error_text = str(exc)
                is_mailtrap_demo_error = 'Demo domains can only be used' in error_text

                if is_mailtrap_demo_error and settings.DEBUG:
                    list(get_messages(request))
                    messages.warning(
                        request,
                        'Mailtrap demo không thể gửi email ra ngoài. '
                        f'(Môi trường dev) Mã OTP của bạn là: {otp_code}'
                    )
                    return redirect('forgot_password_verify_otp')

                otp_record.delete()
                request.session.pop(RESET_PENDING_SESSION_KEY, None)
                messages.error(request, 'Không thể gửi mã OTP lúc này. Vui lòng thử lại sau.')
            else:
                messages.info(request, f'Đã gửi mã OTP đến email {user.email}. Vui lòng nhập mã để xác thực.')
                return redirect('forgot_password_verify_otp')

    return render(request, 'accounts/forgot_password_request.html', {
        'email_form': form,
        'otp_expiry_minutes': OTP_EXPIRY_MINUTES,
    })


def forgot_password_verify_otp(request):
    def _render_otp_page(form, pending_email=''):
        return render(request, 'accounts/forgot_password_verify_otp.html', {
            'otp_form': form,
            'pending_email': pending_email,
            'otp_expiry_minutes': OTP_EXPIRY_MINUTES,
        })

    pending_data = request.session.get(RESET_PENDING_SESSION_KEY)
    if not pending_data:
        messages.warning(request, 'Không tìm thấy phiên quên mật khẩu. Vui lòng nhập lại email.')
        return _render_otp_page(RegistrationOtpForm())

    pending_email = pending_data.get('email', '')

    if request.method == 'POST':
        form = RegistrationOtpForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            now = timezone.now()

            otp_record = EmailOTP.objects.filter(
                id=pending_data.get('otp_id'),
                email=pending_email,
                code=otp_code,
                used_at__isnull=True,
                expires_at__gt=now,
            ).first()

            if otp_record is None:
                messages.error(request, 'Nhập sai mã OTP, vui lòng nhập lại.')
            else:
                otp_record.used_at = now
                otp_record.save(update_fields=['used_at'])

                pending_data['otp_verified'] = True
                pending_data['verified_at'] = now.isoformat()
                request.session[RESET_PENDING_SESSION_KEY] = pending_data
                request.session.modified = True

                messages.success(request, 'Xác thực OTP thành công. Vui lòng đặt mật khẩu mới.')
                return redirect('forgot_password_reset')
    else:
        form = RegistrationOtpForm()

    return _render_otp_page(form, pending_email=pending_email)


def forgot_password_reset(request):
    pending_data = request.session.get(RESET_PENDING_SESSION_KEY)
    if not pending_data:
        messages.warning(request, 'Không tìm thấy phiên quên mật khẩu. Vui lòng nhập lại email.')
        return redirect('forgot_password')

    if not pending_data.get('otp_verified'):
        messages.warning(request, 'Vui lòng xác thực OTP trước khi đặt mật khẩu mới.')
        return redirect('forgot_password_verify_otp')

    pending_email = pending_data.get('email', '')
    user = User.objects.filter(
        id=pending_data.get('user_id'),
        email__iexact=pending_email,
    ).first()

    if user is None:
        request.session.pop(RESET_PENDING_SESSION_KEY, None)
        messages.error(request, 'Không tìm thấy tài khoản tương ứng. Vui lòng thử lại.')
        return redirect('forgot_password')

    form = ResetPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_password = form.cleaned_data['new_password']
        confirm_new_password = form.cleaned_data['confirm_new_password']

        if new_password != confirm_new_password:
            messages.error(request, 'Mật khẩu nhập không khớp.')
        else:
            try:
                validate_password(new_password, user=user)
            except ValidationError as exc:
                for msg in exc.messages:
                    messages.error(request, msg)
            else:
                user.set_password(new_password)
                user.save(update_fields=['password'])

                request.session.pop(RESET_PENDING_SESSION_KEY, None)
                messages.success(request, 'Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại.')
                return redirect('login')

    return render(request, 'accounts/forgot_password_reset.html', {
        'reset_form': form,
        'pending_email': pending_email,
    })
