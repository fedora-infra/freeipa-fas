#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2020  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System

Common user extensions
"""
from ipalib import _
from ipalib.parameters import DateTime, Str

from ipaserver.plugins.baseuser import baseuser
from ipaserver.plugins.internal import i18n_messages

from .fasutils import FilteredStrEnum, URL

# preferred pronouns
PRONOUNS = {
    "she/her": _("she/her"),
    "he/him": _("he/him"),
    "they/them": _("they/them"),
    "ask me": _("ask me"),
}

# other pronouns that are not considered by user-find-pronoun-variations
OTHER_PRONOUNS = {
    # https://uwm.edu/lgbtrc/support/gender-pronouns/
    "ae/aer": _("ae/aer"),
    "fae/faer": _("fae/faer"),
    "e/em": _("e/em"),
    "ey/em": _("ey/em"),
    "per/per": _("per/per"),
    "ve/ver": _("ve/ver"),
    "xe/xem": _("xe/xem"),
    "ze/hir": _("ze/hir"),
    "zie/hir": _("zie/hir"),
}

# lower-case, no white-space, just [a-z0-9_]
BLOCKED_PRONOUNS = {
    # transphobic meme "I sexually identify as an Attack Helicopter"
    "helicopter",
    # apache is a synonym for attack helicopter
    "apache",
}


# possible object classes and default attributes are shared between all
# users plugins.
if "fasuser" not in baseuser.possible_objectclasses:
    baseuser.possible_objectclasses.append("fasuser")

fas_user_attributes = [
    "fastimezone",
    "faslocale",
    "fasircnick",
    "fasgpgkeyid",
    "fasstatusnote",
    "fascreationtime",
    "fasrhbzemail",
    "fasgithubusername",
    "fasgitlabusername",
    "faswebsiteurl",
    "faspronoun",
]
baseuser.default_attributes.extend(fas_user_attributes)

baseuser.attribute_members["memberof"].append("fasagreement")

takes_params = (
    FilteredStrEnum(
        "faspronoun?",
        cli_name="faspronoun",
        label=_("Pronoun"),
        doc=_("Pronoun (free-form field with suggested values)"),
        normalizer=lambda value: value.strip().lower(),
        values=tuple(PRONOUNS),
        blocked_values=frozenset(BLOCKED_PRONOUNS),
    ),
    Str(
        "fastimezone?",
        cli_name="fastimezone",
        label=_("user timezone"),
        maxlength=64,
    ),
    Str(
        "faslocale?",
        cli_name="faslocale",
        label=_("user locale"),
        maxlength=64,
    ),
    Str(
        "fasircnick*",
        cli_name="fasircnick",
        label=_("IRC nick name"),
        maxlength=64,
    ),
    Str(
        "fasgpgkeyid*",
        cli_name="fasgpgkeyid",
        label=_("GPG Key ids"),
        maxlength=16,
    ),
    Str(
        "fasstatusnote?",
        cli_name="fasstatusnote",
        label=_("User status note"),
    ),
    DateTime(
        "fascreationtime?",
        cli_name="fascreationtime",
        label=_("user creation time"),
    ),
    Str(
        "fasrhbzemail?",
        cli_name="fasrhbzemail",
        label=_("Red Hat bugzilla email"),
        maxlength=255,
        normalizer=lambda value: value.strip(),
    ),
    Str(
        "fasgithubusername?",
        cli_name="fasgithubusername",
        label=_("GitHub username"),
        maxlength=255,
        normalizer=lambda value: value.strip(),
    ),
    Str(
        "fasgitlabusername?",
        cli_name="fasgitlabusername",
        label=_("GitLab username"),
        maxlength=255,
        normalizer=lambda value: value.strip(),
    ),
    URL(
        "faswebsiteurl?",
        cli_name="faswebsiteurl",
        label=_("Website / Blog URL"),
        maxlength=255,
        normalizer=lambda value: value.strip(),
    ),
)

i18n_messages.messages["userfas"] = {
    "name": _("Fedora Account System"),
    "pronoun_na": "<n/a>",
}
i18n_messages.messages["userfas"].update(
    {
        f"pronoun_{k.replace('/', '_').replace(' ', '_')}": v
        for k, v in PRONOUNS.items()
    }
)
