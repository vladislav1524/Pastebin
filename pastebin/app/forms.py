from django import forms 
from .models import Paste
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm


class PasteForm(forms.ModelForm):
    EXPIRATION_CHOICES = [
        ('10min', '10 минут'),
        ('hour', '1 час'),
        ('day', '1 день'),
        ('week', '1 неделя'),
        ('month', '1 месяц'),
        ('year', '1 год'),
    ]

    expiration_option = forms.ChoiceField(choices=EXPIRATION_CHOICES,
                                         label='Через какое время удалить', required=True)
    password = forms.CharField(required=False, label='Пароль (опционально)')

    class Meta:
        model = Paste
        fields = ['content', 'expiration_option', 'password']


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Введите пароль')


# auth
class CustomSignupForm(SignupForm):
    username = forms.CharField(max_length=150, label='Ваше имя')

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise ValidationError("Введите ваше имя.")

        return username
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.username = self.cleaned_data['username']
        user.save()
        return user
    

class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
