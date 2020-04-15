#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2020  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System

Stage user extension
"""
from ipalib import _
from ipalib import errors

from ipaserver.plugins.stageuser import stageuser
from ipaserver.plugins.stageuser import stageuser_add
from ipaserver.plugins.stageuser import stageuser_mod

from .baseruserfas import takes_params
from .userfas import user_add_fas_precb, user_mod_fas_precb

# same procedure as standard user
stageuser.takes_params += takes_params

stageuser_add.register_pre_callback(user_add_fas_precb)
stageuser_mod.register_pre_callback(user_mod_fas_precb)


def _check_conflict(self, ldap, dn, entry, operation):
    """Check for conflicting login and email address

    The stageuser_activate plugin does not modrdn the stage user to active
    user. Instead it first creates a new active user DN and then deletes the
    stage user DN. All uniqueness plugins have to exclude stage user area and
    FAS has to manually check for conflicts.
    """
    unique_attrs = ["uid", "krbprincipalname", "krbcanonicalname", "mail"]

    if operation == "add":
        attr_filters = ldap.make_filter(
            {attr: entry[attr] for attr in unique_attrs}, rules=ldap.MATCH_ANY
        )
    elif operation == "mod":
        entry["uid"] = dn["uid"]
        attr_filters = ldap.make_filter(
            {attr: entry[attr] for attr in unique_attrs if attr in entry},
            rules=ldap.MATCH_ANY,
        )
    else:
        raise ValueError(operation)

    objcls_filters = ldap.make_filter(
        {"objectclass": ["posixaccount", "inetOrgPerson"]},
        rules=ldap.MATCH_ANY,
    )
    filters = ldap.combine_filters(
        [objcls_filters, attr_filters], rules=ldap.MATCH_ALL
    )

    try:
        res, truncated = ldap.find_entries(
            filters,
            unique_attrs,
            base_dn=self.api.env.basedn,
            scope=ldap.SCOPE_SUBTREE,
        )
    except errors.NotFound:
        pass
    else:
        for conflict_entry in res:
            if conflict_entry.dn == dn:
                # skip own entry
                continue
            if "mail" in entry:
                raise errors.DuplicateEntry(
                    message=_(
                        "Login '%(user)s' or email address '%(mail)s' are "
                        "already registered."
                    )
                    % {"user": entry["uid"], "mail": ", ".join(entry["mail"])}
                )
            else:
                # mod operation
                raise errors.DuplicateEntry(
                    message=_("Login '%(user)s' is already registered.")
                    % {"user": entry["uid"]}
                )


def stageuser_add_fas_precb(
    self, ldap, dn, entry, attrs_list, *keys, **options
):
    """Verify that uid, mail, and krb principal are not in use
    """
    _check_conflict(self, ldap, dn, entry, operation="add")
    return dn


stageuser_add.register_pre_callback(stageuser_add_fas_precb)


def stageuser_mod_fas_precb(
    self, ldap, dn, entry, attrs_list, *keys, **options
):
    """Verify that uid, mail, and krb principal are not in use
    """
    print(entry)
    _check_conflict(self, ldap, dn, entry, operation="mod")
    return dn


stageuser_mod.register_pre_callback(stageuser_mod_fas_precb)
