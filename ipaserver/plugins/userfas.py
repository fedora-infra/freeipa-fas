#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System
"""
from ipalib import _
from ipalib import errors
from ipalib.parameters import DateTime, Str

from ipaserver.plugins.user import user
from ipaserver.plugins.user import user_add
from ipaserver.plugins.user import user_mod
from ipaserver.plugins.internal import i18n_messages

user.possible_objectclasses.append("fasuser")

user.default_attributes.extend(
    [
        "fastimezone",
        "faslocale",
        "fasircnick",
        "fasgpgkeyid",
        "fasstatusnote",
        "fascreationtime",
        "fasrhbzemail",
        "fasgithubusername",
        "fasgitlabusername",
    ]
)

user.takes_params += (
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
        "fasircnick?",
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
)

i18n_messages.messages["userfas"] = {"name": _("Fedora Account System")}


def check_fasuser_attr(entry):
    """Common function to verify fasuser attributes
    """
    fasrhbzemail = entry.get("fasrhbzemail")
    if fasrhbzemail is not None and "@" not in fasrhbzemail:
        msg = _("invalid e-mail format: %(email)s")
        raise errors.ValidationError(
            name="fasrhbzemail", errors=msg % {"email": fasrhbzemail}
        )


def user_add_fas_precb(self, ldap, dn, entry, attrs_list, *keys, **options):
    if any(option.startswith("fas") for option in options):
        # add fasuser object class
        if not self.obj.has_objectclass(entry["objectclass"], "fasuser"):
            entry["objectclass"].append("fasuser")
        # check fasuser attributes
        check_fasuser_attr(entry)
    return dn


user_add.register_pre_callback(user_add_fas_precb)


def user_mod_fas_precb(self, ldap, dn, entry, attrs_list, *keys, **options):
    if any(option.startswith("fas") for option in options):
        # add fasuser object class
        if "objectclass" not in entry:
            entry_oc = ldap.get_entry(dn, ["objectclass"])
            entry["objectclass"] = entry_oc["objectclass"]
        if not self.obj.has_objectclass(entry["objectclass"], "fasuser"):
            entry["objectclass"].append("fasuser")
        # check fasuser attributes
        check_fasuser_attr(entry)
    return dn


user_mod.register_pre_callback(user_mod_fas_precb)
