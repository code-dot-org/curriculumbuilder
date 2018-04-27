from mezzanine.pages.models import Page

class Internationalizable:

    class Meta:
        abstract = True

    @classmethod
    def gather_strings(cls):
        strings = {}
        for obj in cls.objects.all():
            strings[obj.i18n_key] = {}
            for field in cls.internationalizable_fields():
                string = getattr(obj, field)
                if string:
                    strings[obj.i18n_key][field] = getattr(obj, field)
        return strings

    @property
    def i18n_key(self):
        return self.pk

    @classmethod
    def internationalizable_fields(cls):
        return []

class InternationalizablePage(Internationalizable, Page):

    class Meta:
        abstract = True

    @property
    def i18n_key(self):
        return self.slug

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']
