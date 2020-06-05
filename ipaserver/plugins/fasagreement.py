#
# FreeIPA plugin for Fedora Account System
# See COPYING for license
#
"""User agreement for Fedora Account System

Member users are stored in "memberUser" attribute while related groups are
stored in "member" attribute. FreeIPA does not have a "memberGroup" attribute.
"""
from ipalib import Bool, Str, StrEnum
from ipalib.plugable import Registry
from ipaserver.plugins.baseldap import (
    LDAPObject,
    LDAPSearch,
    LDAPCreate,
    LDAPDelete,
    LDAPUpdate,
    LDAPRetrieve,
    LDAPAddMember,
    LDAPRemoveMember,
    global_output_params,
    pkey_to_value,
)
from ipalib import _, ngettext
from ipapython.dn import DN
from ipaserver.plugins.internal import i18n_messages

__doc__ = _(
    """
"""
)


fasagreement_output_params = ()

register = Registry()


@register()
class fasagreement(LDAPObject):
    """User Agreement object for FAS
    """

    container_dn = DN(("cn", "fasagreements"))
    object_name = _("Agreement")
    object_name_plural = _("Agreements")
    object_class = ["ipaassociation", "fasagreement"]
    permission_filter_objectclasses = ["fasagreement"]
    default_attributes = [
        "cn",
        "description",
        "member",
        "memberuser",
    ]
    uuid_attribute = "ipauniqueid"
    attribute_members = {
        "memberuser": ["user"],
        "member": ["group"],
    }
    allow_rename = True
    managed_permissions = {
        "System: Read FAS Agreements": {
            "replaces_global_anonymous_aci": True,
            "ipapermbindruletype": "all",
            "ipapermright": {"read", "search", "compare"},
            "ipapermdefaultattr": {
                "cn",
                "description",
                "ipauniqueid",
                "ipaenabledflag",
                "member",
                "memberuser",
            },
        },
        "System: Add FAS Agreement": {
            "ipapermright": {"add"},
            "default_privileges": {"FAS Agreement Administrators"},
        },
        "System: Delete FAS Agreement": {
            "ipapermright": {"delete"},
            "default_privileges": {"FAS Agreement Administrators"},
        },
        "System: Manage FAS Agreement user membership": {
            "ipapermright": {"write"},
            "ipapermdefaultattr": {"memberUser"},
            "default_privileges": {"FAS Agreement Administrators"},
        },
        "System: Modify FAS Agreement": {
            "ipapermright": {"write"},
            "ipapermdefaultattr": {
                "cn",
                "description",
                "ipaenabledflag",
                "member",
            },
            "default_privileges": {"FAS Agreement Administrators"},
        },
    }

    label = _("User Agreements")
    label_singular = _("User Agreement")

    takes_params = (
        Str(
            "cn",
            cli_name="name",
            label=_("Agreement name"),
            primary_key=True,
        ),
        Str(
            "description?", cli_name="desc", label=_("Agreement Description"),
        ),
        Bool("ipaenabledflag?", label=_("Enabled"), flags=["no_option"],),
    )


@register()
class fasagreement_add(LDAPCreate):
    __doc__ = _("Create a new User Agreement.")

    has_output_params = (
        LDAPCreate.has_output_params + fasagreement_output_params
    )
    msg_summary = _('Added User Agreement "%(value)s"')

    def pre_callback(
        self, ldap, dn, entry_attrs, attrs_list, *keys, **options
    ):
        entry_attrs["ipaenabledflag"] = ["TRUE"]
        return dn


@register()
class fasagreement_del(LDAPDelete):
    __doc__ = _("Delete a User Agreement.")

    msg_summary = _('Deleted User Agreement "%(value)s"')


@register()
class fasagreement_mod(LDAPUpdate):
    __doc__ = _("Modify a User Agreement.")

    has_output_params = (
        LDAPUpdate.has_output_params + fasagreement_output_params
    )
    msg_summary = _('Modified User Agreement "%(value)s"')


@register()
class fasagreement_find(LDAPSearch):
    __doc__ = _("Search for User Agreements.")

    member_attributes = ["member", "memberuser"]

    has_output_params = (
        LDAPSearch.has_output_params + fasagreement_output_params
    )
    msg_summary = ngettext(
        "%(count)d User Agreement matched",
        "%(count)d User Agreements matched",
        0,
    )


@register()
class fasagreement_show(LDAPRetrieve):
    __doc__ = _("Display the properties of a User Agreeement.")

    has_output_params = (
        LDAPRetrieve.has_output_params + fasagreement_output_params
    )


@register()
class fasagreement_add_user(LDAPAddMember):
    __doc__ = _("Add users to a User Agreement")

    member_attributes = ["memberuser"]
    member_count_out = (_("%i user added."), _("%i users added."))


@register()
class fasagreement_remove_user(LDAPRemoveMember):
    __doc__ = _("Remove users from a User Agreement")

    member_attributes = ["memberuser"]
    member_count_out = (_("%i user removed."), _("%i users removed."))


@register()
class fasagreement_add_group(LDAPAddMember):
    __doc__ = _("Add group to a User Agreement")

    member_attributes = ["member"]
    member_count_out = (_("%i group added."), _("%i groups added."))


@register()
class fasagreement_remove_group(LDAPRemoveMember):
    __doc__ = _("Remove group from a User Agreement")

    member_attributes = ["member"]
    member_count_out = (_("%i group removed."), _("%i groups removed."))


i18n_messages.messages["fasagreement"] = {
    "fasagreements": _("User Agreement"),
    "add": _("Add User Agrement"),
    "remove": _("Remove User Agrement"),
}
