from django.conf import settings


def language_code_do_translation(request):
    return {'LANGUAGE_CODE_DO_TRANSLATION': settings.LANGUAGE_CODE_DO_TRANSLATION}


def current_path_without_language(request):
    current_path = request.get_full_path()
    current_language = request.LANGUAGE_CODE
    current_language_prefix = "/" + current_language

    if current_path.startswith(current_language_prefix):
        return {'CURRENT_PATH_WITHOUT_LANGUAGE': current_path[len(current_language_prefix):]}
    else:
        return {'CURRENT_PATH_WITHOUT_LANGUAGE': current_path}
