from django import forms


class HoneypotField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required = False
        self.widget = forms.HiddenInput()

    def clean(self, value):
        super().clean(value)
        if value:
            raise forms.ValidationError("Bot detected. Invalid input")
