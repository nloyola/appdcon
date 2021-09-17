import binascii
import base64
import hmac
import hashlib
import logging
from urllib.parse import urlparse
from typing import Optional
from urllib.parse import parse_qs, urlencode

from .models import ConnectData, RedirectData
from pprint import pformat

# http://192.168.50.5:8000/discourse/
# ?sso=bm9uY2U9MTQ3NGQ1YTZmY2QwODlkYzgyNTczNmIwMTNhMTQyMTUmcmV0dXJuX3Nzb191cmw9aHR0cHMlM0ElMkYlMkZubG95b2xhLmFzdXNjb21tLmNvbSUyRnNlc3Npb24lMkZzc29fbG9naW4%3D
# &sig=ff4c87e83b131f9e3f1738d04ce455ae95628cae25d097982348bd5eec0898c0
#
#
# 'nonce=1474d5a6fcd089dc825736b013a14215&return_sso_url=https%3A%2F%2Fnloyola.asuscomm.com%2Fsession%2Fsso_login'

logger = logging.getLogger(__name__)


class DiscourseService:
    @staticmethod
    def decode_sso(sso: str) -> Optional[ConnectData]:
        """
        Decodes the SSO from a request and returns the decoded values
        """
        try:
            decode = base64.b64decode(sso.encode("ascii")).decode("ascii")
            logger.debug("decoded sso: %s", decode)

            params = parse_qs(decode)
            nonce = params.get("nonce")
            if nonce is None:
                logger.debug("nonce not found")
                return None

            url = params.get("return_sso_url")
            if url is None:
                logger.debug("return_sso_url not found")
                return None

            return ConnectData(nonce[0], urlparse(url[0]))

        except binascii.Error:
            return None

    @staticmethod
    def verify_sso(secret: str, sso: str, sig: str) -> Optional[bool]:
        """
        Verifies that encoding sso as HMAC-SHA256 matches the signature in sig. The secret is
        used to encode the sso.
        """
        try:
            verification = hmac.new(
                secret.encode("ascii"), sso.encode("ascii"), digestmod=hashlib.sha256
            ).hexdigest()
            logger.debug("verification: %s", pformat(verification))
            return sig == verification
        except binascii.Error:
            return None

    @staticmethod
    def encode_and_sign_msg(secret: str, data: RedirectData) -> dict[str, str]:
        """Encodes and signs a message to be used to reply to a Discourse Connect request"""
        msg = urlencode(
            {
                "nonce": data.nonce,
                "email": data.email,
                "external_id": data.external_id,
                "username": data.username,
                "name": data.name,
            }
        )
        logger.debug("msg: %s", pformat(msg))
        sso_bytes = base64.b64encode(msg.encode("ascii"))
        sso = sso_bytes.decode("ascii")
        sig = hmac.new(
            secret.encode("ascii"), sso_bytes, digestmod=hashlib.sha256
        ).hexdigest()
        return {"sso": sso, "sig": sig}
