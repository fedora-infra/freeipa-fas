from urllib.parse import urlparse

from ipalib.parameters import Str
from ipapython.ipavalidate import Email as valid_email


class URL(Str):
    kwargs = Str.kwargs + (
        ("url_schemes", frozenset, frozenset({"http", "https"})),
    )

    def _rule_url_schemes(self, _, value):
        try:
            url = urlparse(value)
        except Exception as e:
            return _("cannot parse url '{url}', {error}").format(
                url=value, error=str(e)
            )
        if url.scheme not in self.url_schemes:
            return _(
                "unsupported scheme, url must start with: {scheme}"
            ).format(scheme=", ".join(sorted(self.url_schemes)))
        if not url.netloc:
            return _("empty host name")
        return None


class Email(Str):
    kwargs = Str.kwargs + (("email", bool, True),)

    def _rule_email(self, _, value):
        if not valid_email(value):
            return _("Invalid email address")
        return None


class IRCChannel(Str):
    kwargs = Str.kwargs + (("ircurl", bool, True),)

    def _rule_ircurl(self, _, value):
        return None

    def _convert_scalar(self, value, index=None):
        value = super()._convert_scalar(value, index)
        value = value.lstrip("#")
        if not value.startswith("irc:"):
            value = "irc:///{}".format(value)
        return value
