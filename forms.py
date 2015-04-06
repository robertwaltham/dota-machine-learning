from django import forms
from django.forms import Select, TextInput, CheckboxInput
from models import MatchPrediction, ScikitModel


class PredictionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PredictionForm, self).__init__(*args, **kwargs)
        valid_models = ScikitModel.objects.filter(is_ready=True)
        self.fields['model'].queryset = valid_models

    class Meta:
        model = MatchPrediction
        exclude = ['created', 'predicted_radiant_win' ]
        widgets = {
            'model': Select(attrs={'class': 'form-control'}),
        }
