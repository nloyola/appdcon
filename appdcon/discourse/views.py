import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import View
from urllib.parse import ParseResult, urlencode
from pprint import pformat

from .services import DiscourseService
from .models import Site, RedirectData

# to generate a secret string on Linux use the following command:
# date +%s | sha256sum | base64 | head -c 32 ; echo

# temp secret: NDEzNzc3MzYxMzE2YzM3ZDdkZjJlYzc1


logger = logging.getLogger(__name__)


class DiscourseView(View):
    def get(self, request):
        errors = []

        sso = request.GET.get("sso")
        if sso is None:
            errors.append("sso not specified")

        sig = request.GET.get("sig")
        if sig is None:
            errors.append("sig not specified")

        if len(errors):
            return HttpResponseBadRequest(", ".join(errors))

        connect_data = DiscourseService.decode_sso(sso)

        if connect_data is None:
            return HttpResponseBadRequest("unable to decode sso")

        logger.info(
            pformat({"connect_data": connect_data, "sig": sig}, sort_dicts=True)
        )

        site = Site.objects.filter(url__icontains=connect_data.return_url.netloc)[0]

        if not site:
            return HttpResponseBadRequest(
                f"no secret found for site: {connect_data.return_url.netloc}"
            )

        verification = DiscourseService.verify_sso(site.secret, sso, sig)
        if verification is None:
            return HttpResponseBadRequest("signature verification failed")

        payload = DiscourseService.encode_and_sign_msg(
            site.secret,
            RedirectData(
                nonce=connect_data.nonce,
                email="nloyola3@gmail.com",
                external_id=50,
                username="nloyola3",
                name="Nelson Loyola other",
            ),
        )

        redir_url = ParseResult(
            connect_data.return_url.scheme,
            connect_data.return_url.netloc,
            connect_data.return_url.path,
            connect_data.return_url.params,
            urlencode(payload),
            connect_data.return_url.fragment,
        ).geturl()

        logger.info("---> %s", pformat({"redir_url": redir_url, "payload": payload}))
        # return HttpResponse("Hello, world. You're at the Discourse Connect index.")
        return redirect(redir_url)
