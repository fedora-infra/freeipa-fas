#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System

Modify group behavior
"""
from ipaserver.plugins.group import group_remove_member


def group_remove_member_fas_postcb(
    self, ldap, completed, failed, dn, entry_attrs, *keys, **options
):
    """Also remove user from member manager attribute
    """
    if "user" in options:
        result = self.api.Command.group_remove_member_manager(
            keys[0], user=options["user"]
        )
        if result["completed"]:
            # one or more member managers were removed, update the entry
            entry_attrs.pop("membermanager", None)
            newentry = ldap.get_entry(dn, ["membermanager"])
            entry_attrs.update(newentry)
    return completed, dn


group_remove_member.register_post_callback(group_remove_member_fas_postcb)
