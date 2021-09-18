from django.db import models
from urllib.parse import ParseResult
from dataclasses import dataclass


@dataclass
class ConnectData:
    """Represents the data contained in an SSO value sent by Discourse Connect"""

    nonce: str
    return_url: ParseResult


@dataclass
class RedirectParams:
    """
    Holds the information to be sent back to Discourse on a valid connect request.

    See: https://meta.discourse.org/t/discourseconnect-official-single-sign-on-for-discourse-sso/13045
    """
    nonce: str
    email: str
    external_id: str
    username: str
    name: str


class Site(models.Model):
    """
    The information required to use Discourse Connect for a single Discourse site.
    """

    hostname = models.CharField(max_length=255, blank=False)
    secret = models.CharField(max_length=255, blank=False)
