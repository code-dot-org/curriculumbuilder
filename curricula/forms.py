from django import forms
# from mezzanine.conf import settings
# from mezzanine.utils.importing import import_dotted_path


class ChangelogForm(forms.Form):

    # In case we want to support md later...
    # richtext_widget = import_dotted_path(settings.RICHTEXT_WIDGET_CLASS)

    comment = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'rows': 5, 'cols': 35}))
