import logging
import json

from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict

from django_slack import slack_message

from models import Record

logger = logging.getLogger(__name__)


def gong(request):
    user = "@%s" % request.POST.get("user_name", "somebody")
    reason = request.POST.get("text", "Gonged stuff!")

    slack_message('slack/gonged.slack', {
        'user': user,
        'reason': reason
    })

    attachments = [
        {
            'author_name': user,
            'title': reason,
            'image_url': 'https://curriculum.code.org/images/gong.gif',
            'color': '#00adbc'
        }
    ]
    payload = {
        "response_type": "in_channel",
        "attachments": attachments,
    }

    record = Record(user=user, reason=reason)
    record.save()

    return HttpResponse(payload, content_type='application/json')


@never_cache
def get_gongs(request):
    record = Record.objects.latest(field_name='created')
    return JsonResponse(model_to_dict(record))
