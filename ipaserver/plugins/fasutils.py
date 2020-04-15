#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2020  FAS Contributors
# See COPYING for license
#
import re
from urllib.parse import urlparse

from ipalib.parameters import Str, StrEnum
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


class FilteredStrEnum(StrEnum):
    """String enum without member enforcement and block list

    *values* are recommended values. Users are permitted to use custom values
    except for values in *blocked_values*.
    """

    kwargs = StrEnum.kwargs + (("blocked_values", frozenset, frozenset()),)

    def _rule_values(self, *args, **kw):
        """Don't enforce membership check
        """
        return None

    def _rule_blocked_values(self, _, value, **kw):
        """Block unwanted values
        """
        if value in self.values:
            # ok, known value
            return None
        # normalize, lower-case, and filtered string
        # remove everything that is not unicode equivalent of [a-z0-9_]
        mangled = re.sub(r"\W", "", value).lower()
        if any(blocked in mangled for blocked in self.blocked_values):
            return _("pronoun '{value}' is not permitted.").format(
                value=value
            )
        else:
            return None
