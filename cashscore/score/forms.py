from django import forms

from .models import Application, Property


class ApplicationForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = Property.objects.filter(user=user)

    class Meta:
        model = Application
        fields = ( 'applicant_name', 'applicant_email', 'property', 'unit', 'rent_asked',)


class ApplicantForm(forms.Form):
    public_token = forms.CharField(widget=forms.HiddenInput())


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ('address',)
