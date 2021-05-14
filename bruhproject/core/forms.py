from django.forms import ModelForm, widgets, Textarea
from bootstrap_datepicker_plus import DateTimePickerInput
from bruhproject.core.models import Bet, Event, Wallet


class BetEventForm(ModelForm):
    class Meta:
        model = Bet
        fields = ['wallet', 'chosen_result', 'value', ]

    def __init__(self, *args, **kwargs):
        super(BetEventForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget.attrs['min'] = 1
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean(self):
        super(BetEventForm, self).clean()
        wallet = self.cleaned_data.get('wallet')
        if wallet.money < self.cleaned_data.get('value'):
            msg = 'Insufficient funds in the wallet!'
            self.add_error('value', msg)
        elif self.cleaned_data.get('value') < 1:
            msg = 'The minimum bet is 1!'
            self.add_error('value', msg)


class NewEventForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        exclude = ['author', 'creation_time', 'open', 'result', ]
        widgets = {
            'start_time': DateTimePickerInput(attrs={id: 'id_start_time'}),
            'end_time': DateTimePickerInput(attrs={id: 'id_end_time'}),
            'description' : Textarea(attrs={'style': 'resize:none;'})
        }


class CloseEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['result', ]
