from django.db import models
from urllib.parse import ParseResult
from dataclasses import dataclass


@dataclass
class ConnectData:
    """Represents the data contained in an SSO value sent by Discourse Connect"""

    nonce: str
    return_url: ParseResult


@dataclass
class RedirectData:
    nonce: str
    email: str
    external_id: str
    username: str
    name: str


class Site(models.Model):
    """
    The information required to use Discourse Connect.
    """

    url = models.CharField(max_length=255, blank=False)
    secret = models.CharField(max_length=255, blank=False)
