from django.contrib.auth import authenticate, login
from django.shortcuts import render
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages

# # Create your views here.
# def user_login(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             # 验证数据库中是否有此用户
#             user = authenticate(request, username=cd["username"], password=cd["password"])
#             if user is not None:
#                 if user.is_active:
#                     # 如果成功则将user通过login放入session会话
#                     login(request, user)
#                     return HttpResponse("Authenticated successfully")
#                 else:
#                     return HttpResponse("Disable account")
#             else:
#                 return HttpResponse("Invalid Login")
#     else:
#         form = LoginForm()
#     return render(request, "account/login.html", {"form": form})


# login_required装饰器将验证现在的用户，如果通过则执行该View，不通过则回到之前的登录url（根据请求url中的next判断之前url）
@login_required
def dashboard(request):
    return render(request,
                  'account/dashboard.html',
                  # 通过section追踪用户在浏览的位置
                  {'section': 'dashboard'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            # 使用set_password来将密码哈希加密
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated '
                                      'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
            instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})
