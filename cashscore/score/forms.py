from django.forms import ModelForm

from .models import Application, Property


class ApplicationForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = Property.objects.filter(user=user)

    class Meta:
        model = Application
        fields = ( 'applicant_name', 'applicant_email', 'property', 'unit', 'rent_asked',)


class PropertyForm(ModelForm):
    class Meta:
        model = Property
        fields = ('address',)
