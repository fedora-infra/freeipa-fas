#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2020  FAS Contributors
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System

Modify group behavior
"""
from ipalib import _
from ipalib.parameters import Flag
from ipaserver.plugins.group import group
from ipaserver.plugins.group import group_add
from ipaserver.plugins.group import group_add_member
from ipaserver.plugins.group import group_find
from ipaserver.plugins.group import group_mod
from ipaserver.plugins.group import group_remove_member
from ipaserver.plugins.group import group_show
from ipaserver.plugins.internal import i18n_messages

from .fasagreement import fasagreement_member_output_params
from .fasutils import Email, IRCChannel, URL

if "fasgroup" not in group.possible_objectclasses:
    group.possible_objectclasses.append("fasgroup")

group_fas_attributes = [
    "fasurl",
    "fasmailinglist",
    "fasircchannel",
    "fasdiscussionurl",
]
group.default_attributes.extend(group_fas_attributes)
# always fetch objectclass so group_show can show fasgroup property
if "objectclass" not in group.default_attributes:
    group.default_attributes.append("objectclass")

# show FAS Agreement relationship
group.attribute_members["memberof"].append("fasagreement")
group_find.has_output_params += fasagreement_member_output_params
group_mod.has_output_params += fasagreement_member_output_params
group_show.has_output_params += fasagreement_member_output_params

group.managed_permissions.update(
    {
        "System: Read FAS group attributes": {
            "replaces_global_anonymous_aci": True,
            "ipapermbindruletype": "all",
            "ipapermright": {"read", "search", "compare"},
            "ipapermtargetfilter": ["(objectclass=fasgroup)"],
            "ipapermdefaultattr": set(group_fas_attributes),
        },
    }
)

group.takes_params += (
    Flag(
        "fasgroup?",
        label=_("FAS group"),
        flags={"virtual_attribute", "no_create", "no_update", "no_search"},
    ),
    URL(
        "fasurl?",
        cli_name="fasurl",
        label=_("Group URL"),
        maxlength=255,
    ),
    Email(
        "fasmailinglist?",
        cli_name="fasmailinglist",
        label=_("Mailing list address"),
        maxlength=255,
    ),
    IRCChannel(
        "fasircchannel*",
        cli_name="fasircchannel",
        label=_("IRC network and channel"),
        maxlength=255,
    ),
    URL(
        "fasdiscussionurl?",
        cli_name="fasdiscussionurl",
        label=_("Discussion / Forum Site URL"),
        maxlength=255,
    ),
)

group_add.takes_options += (
    Flag(
        "fasgroup",
        cli_name="fasgroup",
        doc=_("Create a FAS group"),
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


def check_fasgroup_attr(entry):
    """Common function to verify fasgroup attributes"""
    pass


def get_fasgroup_attribute(self, entry_attrs, options):
    if options.get("raw", False):
        return
    if "fasgroup" in entry_attrs.get("objectclass", []):
        entry_attrs["fasgroup"] = True


group.get_fasgroup_attribute = get_fasgroup_attribute


def _has_fasgroup_options(options):
    """Check there is a FAS option in options"""
    # --fasgroup flag is True
    if options.get("fasgroup"):
        return True
    # other FAS option except 'fasgroup' (might be present and False)
    return any(
        option.startswith("fas") for option in options if option != "fasgroup"
    )


def group_add_fas_precb(self, ldap, dn, entry, attrs_list, *keys, **options):
    """Add fasgroup object class and related attributes."""
    if _has_fasgroup_options(options):
        if not self.obj.has_objectclass(entry["objectclass"], "fasgroup"):
            entry["objectclass"].append("fasgroup")
        # check fasgroup attributes
        check_fasgroup_attr(entry)
    return dn


group_add.register_pre_callback(group_add_fas_precb)


def group_add_fas_postcb(self, ldap, dn, entry_attrs, *keys, **options):
    """Include fasgroup membership info"""
    self.obj.get_fasgroup_attribute(entry_attrs, options)
    return dn


group_add.register_post_callback(group_add_fas_postcb)


def group_find_fas_precb(
    self, ldap, filter, attrs_list, base_dn, scope, criteria=None, **options
):
    """Search filter for FAS group"""
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
    """Search filter for FAS group"""
    if not options.get("raw", False):
        for entry in entries:
            self.obj.get_fasgroup_attribute(entry, options)
    return truncated


group_find.register_post_callback(group_find_fas_postcb)


def group_mod_fas_precb(self, ldap, dn, entry, *keys, **options):
    """Add fasgroup object class and related attributes."""
    if _has_fasgroup_options(options):
        # add fasgroup object class
        if "objectclass" not in entry:
            entry_oc = ldap.get_entry(dn, ["objectclass"])
            entry["objectclass"] = entry_oc["objectclass"]
        if not self.obj.has_objectclass(entry["objectclass"], "fasgroup"):
            entry["objectclass"].append("fasgroup")
        # check fasgroup attributes
        check_fasgroup_attr(entry)
    return dn


group_mod.register_pre_callback(group_mod_fas_precb)


def group_remove_member_fas_postcb(
    self, ldap, completed, failed, dn, entry_attrs, *keys, **options
):
    """Also remove user from member manager attribute"""
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


def group_add_member_fas_precb(
    self, ldap, dn, found, not_found, *keys, **options
):
    """Enforce user agreements when adding new members

    users must consent to all agreements that are linked to this group.

    Limitations: The check does not work for indirect membership and does
    not limit existing users when a new agreement is linked to a group.
    """
    found_users = found["member"]["user"]
    if not found_users:
        # no users
        return dn

    # found some users, now check agreement
    group_agreements = self.api.Command.fasagreement_find(
        group=keys[0], pkey_only=True
    )["result"]
    if not group_agreements:
        # group has no agreements
        return dn

    # group has agreements
    group_agreements_cns = {a["cn"][0] for a in group_agreements}
    # rebuild found users and update not_found users
    # found users are a list of DNs
    # not found are a list of tuples (pkey, error message)
    found_users = found_users[:]
    new_found_users = found["member"]["user"] = []
    not_found_users = not_found["member"]["user"]

    for user_dn in found_users:
        user_uid = user_dn["uid"]
        # user agreements for group and user
        user_agreements = self.api.Command.fasagreement_find(
            group=keys[0], user=user_uid, pkey_only=True
        )["result"]
        user_agreements_cns = {a["cn"][0] for a in user_agreements}
        diff = group_agreements_cns.difference(user_agreements_cns)
        if diff:
            msg = _("missing user agreement: {}").format(
                ", ".join(sorted(diff))
            )
            not_found_users.append((user_uid, msg))
        else:
            new_found_users.append(user_dn)

    return dn


group_add_member.register_pre_callback(group_add_member_fas_precb)


def group_show_fas_postcb(self, ldap, dn, entry_attrs, *keys, **options):
    """Show fasgroup membership info"""
    self.obj.get_fasgroup_attribute(entry_attrs, options)
    return dn


group_show.register_post_callback(group_show_fas_postcb)


i18n_messages.messages["groupfas"] = {
    "section": _("Fedora Account System"),
    "group": _("FAS Group"),
    "make_fasgroup": _("Change to FAS group"),
}
