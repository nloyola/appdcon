import logging
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import View
from urllib.parse import ParseResult
from pprint import pformat

from .services import DiscourseService
from .models import SignedSingleSignOn, SingleSignOn

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

        sso_encoded = SignedSingleSignOn(value=sso, signature=sig)

        single_signon = DiscourseService.decode_single_signon(sso_encoded)

        if single_signon is None:
            return HttpResponseBadRequest("unable to decode sso")

        logger.info(pformat(single_signon))

        site = DiscourseService().find_site(single_signon.return_url.hostname)

        if site is None:
            return HttpResponseBadRequest(
                f"no secret found for site: {single_signon.return_url.netloc}"
            )

        verification = DiscourseService.verify_single_signon(site.secret, sso_encoded)
        if verification is None:
            return HttpResponseBadRequest("sso hashing failed")

        if not verification:
            return HttpResponseBadRequest("signature verification failed")

        # if user is NOT logged in, then we have to redirect them to the login page. After
        # successfully logging in, the user must be redirected to Discourse.
        #
        # if user IS logged in, we create the redirect parameters required by Discourse Connect

        # hardcode user information for now
        user_info = SingleSignOn(
            nonce=single_signon.nonce,
            email="nloyola@gmail.com",
            external_id=1,
            username="nloyola1",
            name="Nelson Loyola other",
        )

        user_encoded = DiscourseService.sign_single_signon(site.secret, user_info)

        redir_url = ParseResult(
            single_signon.return_url.scheme,
            single_signon.return_url.netloc,
            single_signon.return_url.path,
            single_signon.return_url.params,
            user_encoded.urlencode(),
            single_signon.return_url.fragment,
        ).geturl()

        logger.info(pformat({"redir_url": redir_url, "params": user_encoded}))

        return redirect(redir_url)
