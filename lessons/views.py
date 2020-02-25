from __future__ import absolute_import
from fm.views import AjaxCreateView, AjaxUpdateView
from .forms import ResourceForm


class ResourceCreateView(AjaxCreateView):
    form_class = ResourceForm