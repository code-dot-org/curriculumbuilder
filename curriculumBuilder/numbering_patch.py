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
        # Parent changed - set the new parent
        page.set_parent(new_parent)

        # Ensure lessons, chapters, and units are in the correct hierarchy
        if page.content_model == 'lesson':
            lesson = Lesson.objects.get(id=page.id)
            number = lesson.get_number()
            unit = lesson.get_unit()
            curriculum = lesson.get_curriculum()
            Lesson.objects.filter(id=lesson.id).update(number=number, unit=unit, curriculum=curriculum)

        elif page.content_model == 'chapter':
            chapter = Chapter.objects.get(id=page.id)
            number = chapter.get_number()
            unit = chapter.parent.unit
            curriculum = unit.curriculum
            Chapter.objects.filter(id=chapter.id).update(number=number)
            Lesson.objects.filter(parent=page).update(unit=unit, curriculum=curriculum)

        elif page.content_model == 'unit':
            unit = Unit.objects.get(id=page.id)
            number = unit.get_number()
            curriculum = unit.parent.curriculum
            Unit.objects.filter(id=unit.id).update(number=number, curriculum=curriculum)
            Lesson.objects.filter(unit=unit).update(unit=unit, curriculum=curriculum)

        # Reorder previous siblings.
        pages = Page.objects.filter(parent_id=old_parent_id)
        for i, page in enumerate(pages.order_by('_order')):
            Page.objects.filter(id=page.id).update(_order=i)

            if page.content_model == 'lesson':
                update_numbering(page.lesson, Lesson)
            elif page.content_model == 'chapter':
                update_numbering(page.chapter, Chapter)
                for lesson in page.chapter.lessons:
                    update_numbering(lesson, Lesson)
            elif page.content_model == 'unit':
                update_numbering(page.unit, Unit)
                for lesson in page.unit.lessons:
                    update_numbering(lesson, Lesson)

    # Set the new order for the moved page and its current siblings.
    for i, page_id in enumerate(request.POST.getlist('siblings[]')):
        Page.objects.filter(id=get_id(page_id)).update(_order=i)

        sibling = Page.objects.get(id=get_id(page_id))

        # Need to make sure that children get renumbered as well
        if page.content_model == 'lesson':
            update_numbering(sibling.lesson, Lesson)
        elif page.content_model == 'chapter':
            update_numbering(sibling.chapter, Chapter)
            for lesson in sibling.chapter.lessons:
                update_numbering(lesson, Lesson)
        elif page.content_model == 'unit':
            update_numbering(sibling.unit, Unit)

    # If this is a lesson under a chapter, we need to renumber all children sibling chapters as well :/
    if page.content_model == 'lesson' and page.parent.content_model == 'chapter':
        for lesson in page.lesson.unit.lessons:
            update_numbering(lesson, Lesson)

    # if this is a chapter renumber all children
    if page.content_model == 'chapter':
        for lesson in page.chapter.unit.lessons:
            update_numbering(lesson, Lesson)

    return HttpResponse("ok")


def update_numbering(obj, model):
    model.objects.filter(id=obj.id).update(number=obj.get_number())


views.admin_page_ordering = custom_admin_page_ordering
