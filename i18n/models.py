from mezzanine.pages.models import Page

class Internationalizable:

    class Meta:
        abstract = True

    @classmethod
    def gather_strings(cls):
        strings = {}
        for obj in cls.objects.all():
            strings[obj.unique_identifier] = {}
            for field in cls.internationalizable_fields():
                string = getattr(obj, field)
                if string:
                    strings[obj.unique_identifier][field] = getattr(obj, field)
        return strings

    @property
    def unique_identifier(self):
        return self.pk

    @classmethod
    def internationalizable_fields(cls):
        return []

class InternationalizablePage(Internationalizable, Page):

    class Meta:
        abstract = True

    @property
    def unique_identifier(self):
        return self.slug

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']
