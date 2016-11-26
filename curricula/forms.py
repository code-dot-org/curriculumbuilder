from django import forms


class ChangelogForm(forms.Form):
    comment = forms.CharField(label='Comment', max_length=255)
