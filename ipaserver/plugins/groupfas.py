#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System

Modify group behavior
"""
from ipalib import _
from ipalib import errors
from ipalib.parameters import Flag
from ipaserver.plugins.group import group
from ipaserver.plugins.group import group_add
from ipaserver.plugins.group import group_find
from ipaserver.plugins.group import group_mod
from ipaserver.plugins.group import group_remove_member
from ipaserver.plugins.group import group_show

group.possible_objectclasses.append("fasgroup")
if "objectclass" not in group.default_attributes:
    group.default_attributes.append("objectclass")

group.takes_params += (
    Flag(
        "fasgroup?",
        label=_("FAS group"),
        flags={"virtual_attribute", "no_create", "no_update", "no_search"},
    ),
)

group_add.takes_options += (
    Flag(
        "fasgroup",
        cli_name="fasgroup",
        doc=_("create a FAS group"),
        default=False,
    ),
)

group_find.takes_options += (
    Flag(
        "fasgroup",
        cli_name="fasgroup",
        doc=_("search for FAS groups"),
        default=False,
    ),
)

group_mod.takes_options += (
    Flag(
        "fasgroup",
        cli_name="fasgroup",
        doc=_("change to a FAS group"),
        default=False,
    ),
)


def get_fasgroup_attribute(self, entry_attrs, options):
    if options.get("raw", False):
        return
    if "fasgroup" in entry_attrs.get("objectclass", []):
        entry_attrs["fasgroup"] = True


group.get_fasgroup_attribute = get_fasgroup_attribute


def group_add_fas_precb(
    self, ldap, dn, entry_attrs, attrs_list, *keys, **options
):
    """Add fasgroup object class
    """
    if options.get("fasgroup", False):
        entry_attrs["objectclass"].append("fasgroup")
    return dn


group_add.register_pre_callback(group_add_fas_precb)


def group_add_fas_postcb(self, ldap, dn, entry_attrs, *keys, **options):
    """Include fasgroup membership info
    """
    self.obj.get_fasgroup_attribute(entry_attrs, options)
    return dn


group_add.register_post_callback(group_add_fas_postcb)


def group_find_fas_precb(
    self, ldap, filter, attrs_list, base_dn, scope, criteria=None, **options
):
    """Search filter for FAS group
    """
    if options.get("fasgroup", False):
        fasfilter = ldap.make_filter(
            {"objectclass": ["fasgroup"]}, rules=ldap.MATCH_ALL
        )
        filter = ldap.combine_filters(
            [filter, fasfilter], rules=ldap.MATCH_ALL
        )
    return filter, base_dn, scope


group_find.register_pre_callback(group_find_fas_precb)


def group_find_fas_postcb(self, ldap, entries, truncated, *args, **options):
    """Search filter for FAS group
    """
    if not options.get("raw", False):
        for entry in entries:
            self.obj.get_fasgroup_attribute(entry, options)
    return truncated


group_find.register_post_callback(group_find_fas_postcb)


def group_mod_fas_precb(self, ldap, dn, entry_attrs, *keys, **options):
    """Add fasgroup object class
    """
    if options.get("fasgroup", False):
        old_entry_attrs = ldap.get_entry(dn, ["objectclass"])
        if "fasgroup" in old_entry_attrs["objectclass"]:
            raise errors.EmptyModlist(
                message=_("This is already a FAS group")
            )
        old_entry_attrs["objectclass"].append("fasgroup")
        entry_attrs["objectclass"] = old_entry_attrs["objectclass"]
    return dn


group_mod.register_pre_callback(group_mod_fas_precb)


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


def group_show_fas_postcb(self, ldap, dn, entry_attrs, *keys, **options):
    """Show fasgroup membership info
    """
    self.obj.get_fasgroup_attribute(entry_attrs, options)
    return dn


group_show.register_post_callback(group_show_fas_postcb)
