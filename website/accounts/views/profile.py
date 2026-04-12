from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.forms import ProfileForm, ProfileUserForm
from accounts.models import Profile

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
