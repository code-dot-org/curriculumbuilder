from django import forms

from lessons.models import Resource


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        exclude = ('name',)


class ChangelogForm(forms.Form):
    comment = forms.CharField(label='Comment', max_length=255)
