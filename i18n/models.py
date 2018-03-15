from mezzanine.pages.models import Page

class InternationalizablePage(Page):

    class Meta:
        abstract = True

    @classmethod
    def gather_strings(cls):
        strings = {}
        for obj in cls.objects.all():
            strings[obj.slug] = {}
            for field in cls.internationalizable_fields():
                strings[obj.slug][field] = getattr(obj, field)
        return strings

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']
