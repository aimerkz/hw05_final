from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView

from django.views.generic import CreateView

from django.urls import reverse_lazy

from .forms import CreationForm, ChangeForm, ResetForm, ResetConfirmForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PassChange(PasswordChangeView):
    form_class = ChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class PassChangeDone(PasswordChangeDoneView):
    form_class = ChangeForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_change_done.html'


class PassReset(PasswordResetView):
    form_class = ResetForm
    success_url = reverse_lazy('users:password_reset_done.html')
    template_name = 'users/password_reset_form.html'


class PassResetDone(PasswordResetDoneView):
    form_class = ResetForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_done.html'


class PassResetConfirm(PasswordResetConfirmView):
    form_class = ResetConfirmForm
    success_url = reverse_lazy('users:password_reset_')
    template_name = 'users/password_reset_confirm.html'


class PassResetComplete(PasswordResetCompleteView):
    form_class = ResetConfirmForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_complete.html'
