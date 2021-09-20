from django.views.generic import TemplateView


class HomepageView(TemplateView):
    template_name = 'appdcon/index.html'

    def get_context_data(self, **kwargs):
        return {"discourse_link": "https://nloyola.asuscomm.com/session/sso"}
