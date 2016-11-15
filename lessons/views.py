from fm.views import AjaxCreateView

from forms import ResourceForm


class ResourceCreateView(AjaxCreateView):
    form_class = ResourceForm
