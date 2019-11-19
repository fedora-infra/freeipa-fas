#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System
"""
from ipalib.parameters import DateTime, Str
from ipalib import _

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
    ]
)

user.takes_params += (
    Str("fastimezone?", cli_name="fastimezone", label=_("user timezone")),
    Str("faslocale?", cli_name="faslocale", label=_("user locale")),
    Str("fasircnick?", cli_name="fasircnick", label=_("IRC nick name")),
    Str("fasgpgkeyid*", cli_name="fasgpgkeyid", label=_("GPG Key ids")),
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
)

i18n_messages.messages["userfas"] = {"name": _("Fedora Account System")}


def user_add_fas_precb(self, ldap, dn, entry, attrs_list, *keys, **options):
    if not self.obj.has_objectclass(entry["objectclass"], "fasuser") and any(
        option.startswith("fas") for option in options
    ):
        entry["objectclass"].append("fasuser")
    return dn


user_add.register_pre_callback(user_add_fas_precb)


def user_mod_fas_precb(self, ldap, dn, entry, attrs_list, *keys, **options):
    if any(option.startswith("fas") for option in options):
        if "objectclass" not in entry:
            entry_oc = ldap.get_entry(dn, ["objectclass"])
            entry["objectclass"] = entry_oc["objectclass"]
        if not self.obj.has_objectclass(entry["objectclass"], "fasuser"):
            entry["objectclass"].append("fasuser")
    return dn


user_mod.register_pre_callback(user_mod_fas_precb)
