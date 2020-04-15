#
# FreeIPA plugin for Fedora Account System
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""FreeIPA plugin for Fedora Account System
"""
from ipalib import _, ngettext
from ipalib import errors

from ipapython.dn import DN

from ipaserver.plugins.baseldap import LDAPSearch
from ipaserver.plugins.user import register as user_register
from ipaserver.plugins.user import user
from ipaserver.plugins.user import user_add
from ipaserver.plugins.user import user_find
from ipaserver.plugins.user import user_mod
from ipaserver.plugins.user import user_show

from .baseruserfas import takes_params, fas_user_attributes
from .fasagreement import fasagreement_member_output_params
from .baseruserfas import PRONOUNS, OTHER_PRONOUNS

user.takes_params += takes_params

# show FAS Agreement relationship
user_find.has_output_params += fasagreement_member_output_params
user_mod.has_output_params += fasagreement_member_output_params
user_show.has_output_params += fasagreement_member_output_params

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


@user_register()
class user_find_pronoun_variations(LDAPSearch):
    __doc__ = _("Search for pronoun variations.")

    msg_summary = ngettext(
        "%(count)d user matched", "%(count)d users matched", 0
    )

    def pre_callback(
        self, ldap, filter, attrs_list, base_dn, scope, *args, **options
    ):
        assert isinstance(base_dn, DN)
        # include pronoun in output
        if "faspronoun" not in attrs_list:
            attrs_list.insert(0, "faspronoun")
        # only users with non-empty pronouns
        pronoun_filter = "(faspronoun=*)"
        # filter out users with known pronouns
        known_pronouns = set(PRONOUNS).union(OTHER_PRONOUNS)
        known_pronoun_filter = ldap.make_filter(
            {"faspronoun": sorted(known_pronouns)}, rules=ldap.MATCH_NONE
        )
        filter = ldap.combine_filters(
            (pronoun_filter, known_pronoun_filter, filter),
            rules=ldap.MATCH_ALL,
        )
        return filter, base_dn, scope
