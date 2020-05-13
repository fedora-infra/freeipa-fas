from ipalib import api, errors, output
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
from ipaserver.plugins.hbacrule import is_all
from ipalib import _, ngettext
from ipapython.dn import DN


__doc__ = _(
    """
"""
)

register = Registry()


@register()
class agreement(LDAPObject):
    """
    User Agreement object.
    """

    container_dn = DN(("cn", "agreements"))
    object_name = _("Agreement")
    object_name_plural = _("Agreements")
    object_class = ["ipaassociation", "fasagreement"]
    permission_filter_objectclasses = ["fasagreement"]
    default_attributes = [
        "cn",
        "description",
        "member",
    ]
    uuid_attribute = "ipauniqueid"
    attribute_members = {
        "member": ["user"],
    }
    managed_permissions = {
        "System: Read FAS Agreements": {
            "replaces_global_anonymous_aci": True,
            "ipapermbindruletype": "all",
            "ipapermright": {"read", "search", "compare"},
            "ipapermdefaultattr": {
                "cn",
                "description",
                "ipauniqueid",
                "objectclass",
                "member",
            },
        },
        "System: Add FAS Agreement": {
            "ipapermright": {"add"},
            "default_privileges": {"Agreement Administrators"},
        },
        "System: Delete FAS Agreement": {
            "ipapermright": {"delete"},
            "default_privileges": {"Agreement Administrators"},
        },
        "System: Manage FAS Agreement Membership": {
            "ipapermright": {"write"},
            "ipapermdefaultattr": {"member"},
            "default_privileges": {"Agreement Administrators"},
        },
        "System: Modify FAS Agreement": {
            "ipapermright": {"write"},
            "ipapermdefaultattr": {"cn", "description", "ipaenabledflag",},
            "default_privileges": {"Agreement Administrators"},
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
    )


@register()
class agreement_add(LDAPCreate):
    __doc__ = _("Create a new User Agreement.")

    msg_summary = _('Added User Agreement "%(value)s"')

    def pre_callback(
        self, ldap, dn, entry_attrs, attrs_list, *keys, **options
    ):
        entry_attrs["ipaenabledflag"] = ["TRUE"]
        return dn


@register()
class agreement_del(LDAPDelete):
    __doc__ = _("Delete a User Agreement.")

    msg_summary = _('Deleted User Agreement "%(value)s"')


@register()
class agreement_mod(LDAPUpdate):
    __doc__ = _("Modify a User Agreement.")

    msg_summary = _('Modified User Agreement "%(value)s"')


@register()
class agreement_find(LDAPSearch):
    __doc__ = _("Search for User Agreements.")

    msg_summary = ngettext(
        "%(count)d User Agreement matched",
        "%(count)d User Agreements matched",
        0,
    )


@register()
class agreement_show(LDAPRetrieve):
    __doc__ = _("Display the properties of a User Agreeement.")


@register()
class agreement_add_user(LDAPAddMember):
    __doc__ = _("Add users to a User Agreement")

    member_attributes = ["memberuser"]
    member_count_out = (_("%i user added."), _("%i users added."))


@register()
class agreement_remove_user(LDAPRemoveMember):
    __doc__ = _("Remove users from a User Agreement")

    member_attributes = ["memberuser"]
    member_count_out = (_("%i user removed."), _("%i users removed."))
