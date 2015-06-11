from django import forms
from django.forms import Select, TextInput, CheckboxInput
from models import MatchPrediction, ScikitModel


class PredictionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PredictionForm, self).__init__(*args, **kwargs)
        valid_models = ScikitModel.get_all_ready()
        self.fields['model'].queryset = valid_models

    class Meta:
        model = MatchPrediction
        exclude = ['created', 'predicted_radiant_win' ]
        widgets = {
            'model': Select(attrs={'class': 'form-control'}),
        }


class ModelTestForm(forms.Form):
        n_matches = forms.IntegerField(label='Match Count', initial=2000)
        n_tests = forms.IntegerField(label='Test Count', initial=200)
        min_duration = forms.IntegerField(label='Min Duration', initial=600)
        algorithm = forms.ChoiceField(choices=(('SVC', 'SVC'), ('SVC', 'SGD')), )
