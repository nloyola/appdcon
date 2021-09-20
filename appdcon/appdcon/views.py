from django.views.generic import TemplateView

from discourse.services import DiscourseService


class HomepageView(TemplateView):
    template_name = 'appdcon/index.html'

    def get_context_data(self, **kwargs):
        hostnames = [site.hostname for site in DiscourseService.sites()]
        return {"hostnames": hostnames}
