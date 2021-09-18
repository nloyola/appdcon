from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template('appdcon/index.html')
    context = {"discourse_link": "https://nloyola.asuscomm.com/session/sso"}
    return HttpResponse(template.render(context, request))
