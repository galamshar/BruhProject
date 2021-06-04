from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, widgets, Textarea, EmailField
from bootstrap_datepicker_plus import DateTimePickerInput
from bruhproject.core.models import Bet, Event, Wallet


class NewUserForm(UserCreationForm):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class BetEventForm(ModelForm):
    class Meta:
        model = Bet
        fields = ['wallet', 'chosen_variant', 'amount', ]

    def __init__(self, *args, **kwargs):
        super(BetEventForm, self).__init__(*args, **kwargs)
        self.fields['wallet'].empty_label = "[ Select your wallet ]"
        self.fields['wallet'].label = ""
        self.fields['chosen_variant'].label = ""
        self.fields['amount'].label = ""
        self.fields['chosen_variant'].empty_label = "[ Click to variant for select ]"
        self.fields['amount'].widget.attrs['min'] = 1
        self.fields['amount'].widget.attrs['placeholder'] = "Amount of bet"
        self.fields['chosen_variant'].widget.attrs['disabled'] = True
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control shadow-none'

    def clean(self):
        super(BetEventForm, self).clean()
        wallet = self.cleaned_data.get('wallet')
        if wallet.money < self.cleaned_data.get('amount'):
            msg = 'Insufficient funds in the wallet!'
            self.add_error('amount', msg)
        elif self.cleaned_data.get('amount') < 1:
            msg = 'The minimum bet is 1!'
            self.add_error('amount', msg)