from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Имя")
    last_name = forms.CharField(required=True, label="Фамилия")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'city')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем роль для обычной регистрации
        self.fields['role'].widget = forms.HiddenInput()
        self.fields['role'].initial = 'volunteer'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'city',
                  'bio', 'skills', 'interests', 'avatar')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('vk_link', 'telegram_link', 'birth_date', 'occupation',
                  'organization', 'volunteer_experience', 'available_weekdays', 'has_car')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'volunteer_experience': forms.Textarea(attrs={'rows': 4}),
        }


class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Введите 6-значный код'})
    )


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'})
    )


class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data