from ajax_select import LookupChannel
from django.core import urlresolvers
from lessons.models import Resource

class ResourceLookup(LookupChannel):
  model = Resource

  def get_query(self, q, request):
    return Resource.objects.filter(name__icontains=q).order_by('name')

  def format_item_display(self, obj):
    display_text = obj.name
    if obj.url:
      display_text += u"  -  [%s](%s)" % (obj.name, obj.url)
    display_text += u"  -  <a href='%s' target='_blank'>edit</a>" % (urlresolvers.reverse('admin:lessons_resource_change', args=(obj.pk,)),)
    return display_text