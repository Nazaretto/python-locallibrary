from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.
from django.forms import ModelForm
from .models import BookInstance


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    class Meta:
        widgets= {'renewal_date': forms.DateInput(attrs={'class':'datepicker'})}

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

            # Перевірка того, то дата не виходить за "верхню" межу (+4 тижні).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

            # Пам'ятайте, що завжди треба повертати "очищені" дані.
        return data


class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        # Перевірка того, що дата не в минулому
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Не забувайте завжди повертати очищені дані
        return data

    class Meta:
        model = BookInstance
        fields = ['due_back', ]
        labels = {'due_back': _('Renewal date'), }
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).'), }

