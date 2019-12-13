from django.shortcuts import redirect

def redirect_docs(request):
    response = redirect('/docs/' + request.path.split('/documentation/')[1])
    return response
