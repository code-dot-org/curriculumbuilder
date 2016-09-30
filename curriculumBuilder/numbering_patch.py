from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from mezzanine.pages.models import Page, PageMoveException
from mezzanine.pages import views
from lessons.models import Lesson
from curricula.models import Unit, Chapter

"""
Mokeypatching the page order view to deal with out custom numbering logic

"""


@staff_member_required
def custom_admin_page_ordering(request):
  """
  Updates the ordering of pages via AJAX from within the admin.
  Then updates page numbering based on heirarchical ordering
  """

  def get_id(s):
    s = s.split("_")[-1]
    return int(s) if s.isdigit() else None

  page = get_object_or_404(Page, id=get_id(request.POST['id']))
  old_parent_id = page.parent_id
  new_parent_id = get_id(request.POST['parent_id'])
  new_parent = Page.objects.get(id=new_parent_id) if new_parent_id else None

  try:
    page.get_content_model().can_move(request, new_parent)
  except PageMoveException as e:
    messages.error(request, e)
    return HttpResponse('error')

  # Perform the page move
  if new_parent_id != page.parent_id:
    # Parent changed - set the new parent and re-order the
    # previous siblings.
    page.set_parent(new_parent)
    if hasattr(page, 'lesson'):
      lesson = Lesson.objects.get(id=page.id)
      number = lesson.get_number()
      unit = lesson.get_unit()
      curriculum = lesson.get_curriculum()
      Lesson.objects.filter(id=lesson.id).update(number=number, unit=unit, curriculum=curriculum)
    elif hasattr(page, 'unit'):
      unit = Unit.objects.get(id=page.id)
      number = unit.get_number()
      curriculum = unit.parent.curriculum
      Unit.objects.filter(id=unit.id).update(number=number, curriculum=curriculum)
      Lesson.objects.filter(unit=unit).update(unit=unit, curriculum=curriculum)

    pages = Page.objects.filter(parent_id=old_parent_id)
    for i, page in enumerate(pages.order_by('_order')):
      Page.objects.filter(id=page.id).update(_order=i)
      if hasattr(page, 'lesson'):
        lesson = Lesson.objects.get(id=page.id)
        print lesson, lesson._order, lesson.number, lesson.get_number()
        Lesson.objects.filter(id=lesson.id).update(number=lesson.get_number())
  # Set the new order for the moved page and its current siblings.
  for i, page_id in enumerate(request.POST.getlist('siblings[]')):
    Page.objects.filter(id=get_id(page_id)).update(_order=i)
    try:
      lesson = Lesson.objects.get(id=get_id(page_id))
      Lesson.objects.filter(id=lesson.id).update(number=lesson.get_number())
    except:
      pass
    try:
      unit = Unit.objects.get(id=get_id(page_id))
      Unit.objects.filter(id=unit.id).update(number=unit.get_number())
    except:
      pass

  return HttpResponse("ok")


views.admin_page_ordering = custom_admin_page_ordering
