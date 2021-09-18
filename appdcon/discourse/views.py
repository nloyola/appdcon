import logging
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import View
from urllib.parse import ParseResult, urlencode
from pprint import pformat

from .services import DiscourseService
from .models import Site, RedirectParams

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

        site = Site.objects.filter(hostname=connect_data.return_url.hostname).first()

        if site is None:
            return HttpResponseBadRequest(
                f"no secret found for site: {connect_data.return_url.netloc}"
            )

        verification = DiscourseService.verify_connecta_attempt(site.secret, sso, sig)
        if verification is None:
            return HttpResponseBadRequest("sso hashing failed")

        if not verification:
            return HttpResponseBadRequest("signature verification failed")

        # if user is NOT logged in, then we have to redirect them to the login page. After
        # successfully logging in, the user must be redirected to Discourse.
        #
        # if user IS logged in, we create the redirect parameters required by Discourse Connect

        # hardcode user information for now
        user_info = RedirectParams(
            nonce=connect_data.nonce,
            email="nloyola@gmail.com",
            external_id=1,
            username="nloyola1",
            name="Nelson Loyola other",
        )

        params = DiscourseService.encode_and_sign_msg(site.secret, user_info)

        redir_url = ParseResult(
            connect_data.return_url.scheme,
            connect_data.return_url.netloc,
            connect_data.return_url.path,
            connect_data.return_url.params,
            urlencode(params),
            connect_data.return_url.fragment,
        ).geturl()

        logger.info(pformat({"redir_url": redir_url, "payload": params}))

        return redirect(redir_url)
