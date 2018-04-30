from mezzanine.pages.models import Page

class Internationalizable:

    class Meta:
        abstract = True

    @classmethod
    def internationalizable_fields(cls):
        return []

    @classmethod
    def get_i18n_objects(cls):
        return cls.objects

    @classmethod
    def gather_strings(cls):
        strings = {}
        for obj in cls.get_i18n_objects().all():
            if obj.should_be_translated:
                key = obj.i18n_key
                strings[key] = {}
                for field in cls.internationalizable_fields():
                    string = getattr(obj, field)
                    if string:
                        strings[key][field] = getattr(obj, field)
        return strings

    @property
    def should_be_translated(self):
        return True

    @property
    def i18n_key(self):
        return self.pk

class InternationalizablePage(Internationalizable, Page):

    class Meta:
        abstract = True

    @classmethod
    def get_i18n_objects(cls):
        return super(InternationalizablePage, cls).get_i18n_objects().select_related('parent')

    @property
    def should_be_translated(self):
        if self.parent and isinstance(self.parent, Page):
            real_parent = self.parent.get_content_model()
            if isinstance(real_parent, Internationalizable):
                return real_parent.should_be_translated

        return True;

    @property
    def i18n_key(self):
        return self.slug

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']
