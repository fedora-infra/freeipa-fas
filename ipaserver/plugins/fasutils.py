from urllib.parse import urlparse

from ipalib.parameters import Str


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
