import base64
import binascii
from django.db import models
import hashlib
import hmac
from typing import Optional
from urllib.parse import ParseResult, urlencode
from dataclasses import dataclass


@dataclass
class SignedSingleSignOn:
    """Represents the endoded single signon data sent to / from a Discourse server in a HTTP request"""

    value: str
    signature: str

    def base64_decode(self) -> Optional[str]:
        try:
            return base64.b64decode(self.value.encode("ascii")).decode("ascii")
        except binascii.Error:
            return None

    def is_valid(self, secret) -> Optional[bool]:
        """
        Verifies that hasing the value (as HMAC-SHA256) with secret matches its signature.
        """
        try:
            hash = hmac.new(
                secret.encode("ascii"), self.value.encode("ascii"), digestmod=hashlib.sha256
            ).hexdigest()
            return self.signature == hash
        except binascii.Error:
            return None

    def urlencode(self) -> str:
        return urlencode({"sso": self.value, "sig": self.signature})


@dataclass
class SingleSignOnRequest:
    """Represents the data contained in an Discourse Connect single signon request. I.e. what
    discourse sends when a user attempts to login.

    The nonce expires 10 minutes after the user attempts to login.
    """

    nonce: str
    return_url: ParseResult


@dataclass
class SingleSignOn:
    """Holds the information sent in response to a Discourse server on a valid connect request.

    See: https://meta.discourse.org/t/discourseconnect-official-single-sign-on-for-discourse-sso/13045

    The nonce must be the same as the one sent in the single signon request. It expires 10 minutes
    after the user attempts to login.

    """

    nonce: str
    email: str
    external_id: str
    username: str
    name: str

    def base64_encode(self) -> str:
        msg = self.urlencode()
        return base64.b64encode(msg.encode("ascii"))

    def urlencode(self) -> str:
        return urlencode(
            {
                "nonce": self.nonce,
                "email": self.email,
                "external_id": self.external_id,
                "username": self.username,
                "name": self.name,
            }
        )


class Site(models.Model):
    """
    The information required to use Discourse Connect for a single Discourse site.
    """

    hostname = models.CharField(max_length=255, blank=False)
    secret = models.CharField(max_length=255, blank=False)
