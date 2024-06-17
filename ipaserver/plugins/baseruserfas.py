#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2020  FreeIPA FAS Contributors
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System

Common user extensions
"""
from ipalib import _
from ipalib.parameters import DateTime, Str, Bool

from ipaserver.plugins.baseuser import baseuser
from ipaserver.plugins.internal import i18n_messages

from .fasutils import URL

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
    "fasisprivate",
    "faspronoun",
    "fasrssurl",
]
baseuser.default_attributes.extend(fas_user_attributes)

baseuser.attribute_members["memberof"].append("fasagreement")

takes_params = (
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
        minlength=16,
        maxlength=40,
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
    Str(
        "faswebsiteurl*",
        cli_name="faswebsiteurl",
        label=_("Blog URL"),
        maxlength=255,
        normalizer=lambda value: value.strip(),
    ),
    Bool(
        "fasisprivate?",
        cli_name="fasisprivate",
        label=_("Hide personal data"),
        doc=_("Hide personal data from other users"),
    ),
    Str(
        "faspronoun*",
        cli_name="faspronoun",
        label=_("Preferred pronouns"),
        maxlength=64,
    ),
    Str(
        "fasrssurl*",
        cli_name="fasrssurl",
        label=_("RSS URL"),
        maxlength=255,
        normalizer=lambda value: value.strip(),
    ),
)

i18n_messages.messages["userfas"] = {"name": _("Fedora Account System")}
