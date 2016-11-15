from django.dispatch import receiver, Signal
from mezzanine.core.managers import SearchableQuerySet
from mezzanine.pages.models import Page
from lessons.models import Lesson
from curricula.models import Unit, Chapter

post_update = Signal()
model_classes = [Lesson, Unit, Chapter]

def update(self, *args, **kwargs):
  super(SearchableQuerySet, self).update(*args, **kwargs)
  post_update.send(sender=self.model, instance=self)

SearchableQuerySet.update = update

@receiver(post_update, sender=Page)
def update_number(sender, instance, *args, **kwargs):
  page = instance.first()
  if hasattr(page, "lesson"):
    page.lesson.save()
  elif hasattr(page, "unit"):
    page.unit.save()
  elif hasattr(page, "chapter"):
    page.chapter.save()
    for lesson in page.chapter.lessons:
      lesson.save()