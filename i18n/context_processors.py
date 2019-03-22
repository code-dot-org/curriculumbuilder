from django.conf import settings

def language_code_do_translation(request):
    return {'LANGUAGE_CODE_DO_TRANSLATION': settings.LANGUAGE_CODE_DO_TRANSLATION}
