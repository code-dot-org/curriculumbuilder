from fm.views import AjaxCreateView, AjaxUpdateView
from forms import ResourceForm


class ResourceCreateView(AjaxCreateView):
    form_class = ResourceForm