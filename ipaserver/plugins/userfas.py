#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System
"""
from ipalib import _
from ipalib import errors

from ipaserver.plugins.user import user
from ipaserver.plugins.user import user_add
from ipaserver.plugins.user import user_mod

from .baseruserfas import takes_params, fas_user_attributes

user.takes_params += takes_params

user.managed_permissions.update(
    {
        "System: Read FAS user attributes": {
            "replaces_global_anonymous_aci": True,
            "ipapermbindruletype": "all",
            "ipapermright": {"read", "search", "compare"},
            "ipapermtargetfilter": ["(objectclass=fasuser)"],
            "ipapermdefaultattr": {"nsAccountLock"}.union(
                fas_user_attributes
            ),
        },
        # not yet supported
        # "System: Self-Modify FAS user attributes": {
        #     "replaces_global_anonymous_aci": True,
        #     "ipapermright": {"write"},
        #     "ipapermtargetfilter": ["(objectclass=fasuser)"],
        #     "ipapermbindruletype": "self",
        #     "ipapermdefaultattr": fas_user_attributes.copy(),
        # },
    },
)


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
