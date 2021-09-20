import hmac
import hashlib
import logging
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

from .models import SignedSingleSignOn, SingleSignOnRequest, SingleSignOn, Site

logger = logging.getLogger(__name__)


class DiscourseService:
    @staticmethod
    def decode_single_signon(sso_encoded: SignedSingleSignOn) -> Optional[SingleSignOnRequest]:
        """
        Decodes the a single signon value and returns the decoded values
        """
        decode = sso_encoded.base64_decode()
        if decode is None:
            logger.debug("sso could not be decoded")
            return None

        params = parse_qs(decode)
        nonce = params.get("nonce")
        if nonce is None:
            logger.debug("nonce not found")
            return None

        url = params.get("return_sso_url")
        if url is None:
            logger.debug("return_sso_url not found")
            return None

        req = SingleSignOnRequest(nonce[0], urlparse(url[0]))
        logger.debug("decode_single_signon: decoded sso: %s", req)
        return req

    @staticmethod
    def verify_single_signon(secret: str, sso_encoded: SignedSingleSignOn) -> Optional[bool]:
        """Verifies that hasing the encoded single signon with secret matches its signature."""
        return sso_encoded.is_valid(secret)

    @staticmethod
    def sign_single_signon(secret: str, data: SingleSignOn) -> SignedSingleSignOn:
        """Encodes and signs the single sign on information used in a reply to a Discourse Connect request"""
        sso = data.base64_encode()
        shash = hmac.new(secret.encode("ascii"), sso, digestmod=hashlib.sha256).hexdigest()
        return SignedSingleSignOn(value=sso.decode("ascii"), signature=shash)

    @staticmethod
    def sites() -> List[Site]:
        return list(Site.objects.all())

    @staticmethod
    def find_site(hostname: str) -> Site:
        return Site.objects.filter(hostname=hostname).first()
