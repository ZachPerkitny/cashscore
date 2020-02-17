from django import forms
from django.core import validators

from .models import Application, Property


class ApplicationForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_property'].queryset = Property.objects.filter(user=user)
        self.fields['applicant_name'].widget.attrs.update({ 'autofocus': True })

    class Meta:
        model = Application
        fields = ( 'applicant_name', 'applicant_email', 'user_property', 'unit', 'rent_asked',)


class CommaSeperatedField(forms.Field):
    def __init__(self, min_length=None, max_length=None, **kwargs):
        self.min_length = min_length
        self.max_length = max_length
        super().__init__(**kwargs)
        if min_length is not None:
            self.validators.append(validators.MinLengthValidator(int(min_length)))
        if max_length is not None:
            self.validators.append(validators.MaxLengthValidator(int(max_length)))

    def to_python(self, value):
        value = str(value)
        return value.split(',')


class ApplicantForm(forms.Form):
    tokens = CommaSeperatedField(min_length=1, widget=forms.HiddenInput())


class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({ 'autofocus': True })

    class Meta:
        model = Property
        fields = ('address',)
