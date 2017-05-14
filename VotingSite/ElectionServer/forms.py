from django import forms

class ElectionCreationForm(forms.Form):
    name = forms.CharField(max_length=150, label='Name')
    description = forms.CharField(label='Description')
    startTime = forms.DateTimeField(label='Start date and time')
    endTime = forms.DateTimeField(label='End date and time')
    timeOpenBooth = forms.TimeField(required=False, label='Start Voting Time per Day')
    timeCloseBooth = forms.TimeField(required=False,label='End Voting Time per Day')