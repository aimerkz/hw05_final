from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )


class ChangeForm(PasswordChangeForm):
    model = User
    fields = ('current_password', 'new_password', 'new_password_again')


class ResetForm(PasswordResetForm):
    model = User
    fields = ('email')


class ResetConfirmForm(SetPasswordForm):
    model = User
    fields = ('new_password', 'conf_new_password')
