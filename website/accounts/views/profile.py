from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta

from accounts.forms import ProfileForm, ProfileUserForm, ChangePasswordRequestForm, RegistrationOtpForm
from accounts.models import Profile, EmailOTP

CHANGE_PASSWORD_SESSION_KEY = 'change_password_pending_data'
OTP_EXPIRY_MINUTES = 10

@login_required 
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = ProfileUserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công.')
        else:
            messages.error(request, 'Không thể cập nhật hồ sơ. Vui lòng kiểm tra lại thông tin.')
    else:
        user_form = ProfileUserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'user_form': user_form,
        'profile_form': profile_form,
    })


def _send_change_password_otp_email(email, otp_code, username):
    subject = '[CHO THUÊ NHÀ] Mã OTP thay đổi mật khẩu'
    body = (
        'Xin chào,\n\n'
        f'Tài khoản {username} vừa yêu cầu thay đổi mật khẩu đăng nhập.\n'
        f'Mã OTP xác thực của bạn là: {otp_code}\n\n'
        f'Mã OTP này sẽ có hiệu lực trong {OTP_EXPIRY_MINUTES} phút.\n'
        'Nếu bạn không yêu cầu thay đổi mật khẩu, vui lòng kiểm tra lại sự an toàn của tài khoản và bỏ qua email này.\n\n'
        'Trân trọng,\nHệ thống Thuê Nhà'
    )
    EmailMessage(
        subject=subject,
        body=body,
        to=[email],
    ).send(fail_silently=False)


@login_required
def change_password_request(request):
    form = ChangePasswordRequestForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_new_password = form.cleaned_data['confirm_new_password']

            if not request.user.check_password(old_password):
                messages.error(request, 'Mật khẩu hiện tại không đúng.')
            elif len(new_password) < 6:
                messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự.')
            elif new_password != confirm_new_password:
                messages.error(request, 'Mật khẩu mới không khớp.')
            else:
                try:
                    validate_password(new_password, user=request.user)
                except ValidationError as exc:
                    for msg in exc.messages:
                        messages.error(request, msg)
                else:
                    # Form valid, generate OTP and session keys
                    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
                    otp_code = EmailOTP.generate_unique_code()
                    user = request.user

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

                    request.session[CHANGE_PASSWORD_SESSION_KEY] = {
                        'new_password': new_password,
                        'otp_id': otp_record.id,
                        'expires_at': expires_at.isoformat(),
                    }
                    request.session.modified = True

                    try:
                        _send_change_password_otp_email(
                            email=user.email,
                            otp_code=otp_code,
                            username=user.username,
                        )
                    except Exception as exc:
                        otp_record.delete()
                        request.session.pop(CHANGE_PASSWORD_SESSION_KEY, None)
                        messages.error(request, 'Lỗi hệ thống: Không thể gửi mã OTP lúc này. Vui lòng thử lại sau.')
                    else:
                        messages.info(request, f'Đã gửi mã OTP đến email {user.email}. Vui lòng nhập mã để thay đổi mật khẩu.')
                        return redirect('change_password_verify_otp')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin biểu mẫu.')

    return render(request, 'accounts/change_password.html', {
        'form': form,
    })


@login_required
def change_password_verify_otp(request):
    pending_data = request.session.get(CHANGE_PASSWORD_SESSION_KEY)
    if not pending_data:
        messages.warning(request, 'Phiên xác thực đã hết hạn hoặc không tồn tại. Vui lòng thử lại.')
        return redirect('change_password')

    if request.method == 'POST':
        form = RegistrationOtpForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            now = timezone.now()

            otp_record = EmailOTP.objects.filter(
                id=pending_data.get('otp_id'),
                email=request.user.email,
                code=otp_code,
                used_at__isnull=True,
                expires_at__gt=now,
            ).first()

            if otp_record is None:
                messages.error(request, 'Mã OTP không đúng hoặc đã hết hạn. Vui lòng kiểm tra lại.')
            else:
                user = request.user
                new_password = pending_data.get('new_password', '')
                
                user.set_password(new_password)
                user.save(update_fields=['password'])

                otp_record.used_at = now
                otp_record.save(update_fields=['used_at'])

                request.session.pop(CHANGE_PASSWORD_SESSION_KEY, None)
                
                # Keep user logged in after password change
                update_session_auth_hash(request, user)

                messages.success(request, 'Thay đổi mật khẩu thành công!')
                return redirect('profile')
    else:
        form = RegistrationOtpForm()

    return render(request, 'accounts/change_password_verify_otp.html', {
        'otp_form': form,
        'email': request.user.email,
        'otp_expiry_minutes': OTP_EXPIRY_MINUTES,
    })
