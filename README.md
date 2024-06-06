# FreeIPA plugin for Fedora Account System

The *freeip-fas* plugin provides schema extension of FreeIPA users for
the Fedora Account System. The plugin must be installed on all FreeIPA
servers, preferable before the server/replica is installed.

If the plugin is installed later, then the local schema cache may be
outdated and ``ipa`` command may not be aware of the new attributes.
In that case the local schema cache can be refreshed by enforcing
a schema check ``ipa -eforce_schema_check=True ping`` or by purging
the cache with ``rm -rf ~/.cache/ipa``.

Installation requires a server upgrade ``ipa-server-upgrade`` and
restart of services ``ipactl restart``. The post transaction hook
of the RPM package takes care of both. A server upgrade can take a
while and can disrupt normal operations on the machine. It is advised
to serialize the operation and install the plugin on one server at a
time.

## Additional user attributes

User object is extended by a new *fasUser* object class.

* *fasTimeZone*: string, writable by self
* *fasLocale*: string, writable by self
* *fasIRCNick*: multi-valued string, writable by self, indexed
* *fasGPGKeyId*: multi-valued string, writable by self, indexed
* *fasCreationTime*: timestamp, writable by admin
* *fasStatusNote*: string, writable by admin
* *fasRHBZEmail*: string, writable by self
* *fasGitHubUsername*: string, writable by self
* *fasGitLabUsername*: string, writable by self
* *fasWebsiteURL*: multi-valued string, writable by self
* *fasIsPrivate*: boolean, writable by self
* *fasPronoun*: String, writable by self
* *fasRssUrl*: multi-valued string, writable by self

This also applies to stage users.

## Groups

Group object is extended by a new, optional *fasGroup* object class.
The object class also acts as a marker and filter to hide internal
groups.

* ``group_add`` and ``group_mod`` have option ``fasgroup`` to add
  *fasGroup* object class.
* ``group_find`` has option ``fasgroup`` to filter out groups that
  don't have the *fasGroup* object class.
* ``group_remove_member`` also removes member managers

Groups with the *fasGroup* object class have the following optional attributes:

* *fasURL*: multi-valued string
* *fasIRCChannel*: string
* *fasMailingList*: string
* *fasDiscussionURL*: string

## Group / User Agreement check

The ``group_add_member`` command checks user agreements. Users must
consent to all linked agreements before they are permitted to join a
group. The ``fasagreement-remove-user`` command removes users from
groups.


## ACIs

* ``Read FAS user attributes``
* ``Users can modify their own FAS attributes``
* ``Users can modify their own Email address``
* ``Users can remove themselves as members of groups``
* ``Member managers can remove themselves as member managers of groups``
* ``Read FAS group attributes``

## User settings

* OTP set as default authentication method.
* User search uses login, given name, surname, mail, and IRC nick.

## Indexes

* Index on ``fasIRCNick`` for presence and equality
* Index on ``fasGPGKeyId`` for presence and equality
* Index on ``fasRssUrl`` for presence
* Index on ``nsAccountLock`` for equality
* Uniqueness of ``mail`` attributes

## Command line extension

```
$ ipa user-mod --help
...
  --fastimezone=STR     user timezone
  --faslocale=STR       user locale
  --fasircnick=STR      IRC nick name
  --fasgpgkeyid=STR     GPG Key ids
  --fasstatusnote=STR   User status note
  --fascreationtime=DATETIME
                        user creation time
  ...
```

The `ipa stageuser-add` command is extended in the same way.

Stage user plugin ensures that a stage user does not have the same
login or email address as another user (active, staged, or deleted).

The group add, modification, and find commands have an additional
option ``--fasgroup``.

```
$ ipa group-add --help
...
--fasgroup     create a FAS group
...
$ ipa group-find --help
...
--fasgroup     search for FAS groups
...
$ ipa group-mod --help
...
--fasgroup     change to a FAS group
...
```

The group find and show commands also show FAS group membership.

```
$ ipa group-show somegroup
  Group name: somegroup
  GID: 54400007
  FAS group: True
$ ipa group-find somegroup
---------------
1 group matched
---------------
  Group name: somegroup
  GID: 54400007
  FAS group: True
----------------------------
Number of entries returned 1
----------------------------
```

## User Agreements

User agreements are handled by a new object type ``fasagreement``.
Agreements can be linked to 0..n groups. Users are able to consent to
any enabled user agreement. They can neither consent to disabled user
agreement nor retract consent. User agreements can be managed by
admins and any user with *FAS Agreement Administrators* privilege.

```
  fasagreement-add           Create a new User Agreement.
  fasagreement-add-group     Add group to a User Agreement
  fasagreement-add-user      Add users to a User Agreement
  fasagreement-del           Delete a User Agreement.
  fasagreement-disable       Disable a User Agreement
  fasagreement-enable        Enable a User Agreement
  fasagreement-find          Search for User Agreements.
  fasagreement-mod           Modify a User Agreement.
  fasagreement-remove-group  Remove group from a User Agreement
  fasagreement-remove-user   Remove users from a User Agreement
  fasagreement-show          Display the properties of a User Agreeement.
```

Permissions for privilege *FAS Agreement Administrators*:

- System: Add FAS Agreement
- System: Delete FAS Agreement
- System: Manage FAS Agreement user membership
- System: Modify FAS Agreement

Permissions for all authenticated users:

- System: Read FAS Agreements

Additional ACIs:

- Forbid users to retract an agreement
- Allow users to consent to an agreement

### User Agreement example

Create group as admin
```
$ kinit admin
Password for admin@FAS.EXAMPLE:
$ ipa group-add myfasgroup
------------------------
Added group "myfasgroup"
------------------------
  Group name: myfasgroup
  GID: 1632000010
$ ipa fasagreement-add myagreement --desc="Agreement for myfasgroup"
----------------------------------
Added User Agreement "myagreement"
----------------------------------
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
$ ipa fasagreement-add-group myagreement --groups=myfasgroup
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
  Member groups: myfasgroup
-------------------------
Number of members added 1
-------------------------
$ ipa group-add-member myfasgroup --user=fasuser1
  Group name: myfasgroup
  GID: 1632000010
  Member users: fasgroupadmin, fasuser1
  Failed members:
    member user: fasuser2: missing user agreements: myagreement
    member group:
    member service:
-------------------------
Number of members added 0
-------------------------
```

Consent to agreement as normal user

```
$ kinit fasuser1
Password for fasuser1@FAS.EXAMPLE:
$ ipa fasagreement-add-user myagreement --user=fasuser1
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
  Member groups: myfasgroup
-------------------------
Number of members added 1
-------------------------
$ ipa fasagreement-show myagreement
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
  Member groups: myfasgroup
  Agreement users: fasuser1
```

Normal users can neither retract an agreement nor agree on behalf of
another user:

```
$ ipa fasagreement-add-user myagreement --user=fasuser2
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
  Failed users/groups:
    member user: fasuser2: Insufficient access: Insufficient 'write' privilege to the 'memberUser' attribute of entry 'cn=myagreement,cn=fasagreements,dc=fas,dc=example'.
-------------------------
Number of members added 0
-------------------------
$ ipa fasagreement-remove-user myagreement --user=fasuser1
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
  Member groups: myfasgroup
  Failed users/groups:
    member user: fasuser1: Insufficient access: Insufficient 'write' privilege to the 'memberUser' attribute of entry 'cn=myagreement,cn=fasagreements,dc=fas,dc=example'.
---------------------------
Number of members removed 0
---------------------------
```

Agreements cannot be removed as long as any group is linked to an
agreement:

```
$ kinit admin
Password for admin@FAS.EXAMPLE:
$ ipa fasagreement-del myagreement
ipa: ERROR: Insufficient access: Not allowed to delete User Agreement with linked groups
$ ipa fasagreement-remove-group myagreement --groups=myfasgroup
  Agreement name: myagreement
  Agreement Description: Agreement for myfasgroup
---------------------------
Number of members removed 1
---------------------------
$ ipa fasagreement-del myagreement
------------------------------------
Deleted User Agreement "myagreement"
------------------------------------
```

Admins and user agreement managers can remove users from an agreement.
The operation also removes users all linked groups

```
$ ipa group-show myfasgroup
  Group name: myfasgroup
  GID: 1632000010
  Member users: fasuser1
  Member of user agreement: myagreement
$ ipa fasagreement-remove-user myagreement --user=fasuser1
  Agreement name: myagreement
  Member groups: myfasgroup
---------------------------
Number of members removed 1
---------------------------
$ ipa group-show myfasgroup
  Group name: myfasgroup
  GID: 1632000010
```


## Service delegation

The s4u2proxy service delegation rule ``fasjson-http-delegation``
allows fasjson services to impersonate users when talking to IPA's
LDAP servers. All fasjson services must be added to the rule with:

```
$ ipa servicedelegationrule-add-member \
      --principals=HTTP/$(hostname) fasjson-http-delegation
```


## Server limits

With FASJSON we want to be able to list all users, using a SimplePage query. At
the moment we have about 120k users and we're hitting the default
``lookThroughLimit``. We are thus increasing the ``pagedLookThroughLimit`` to
500k.


## License

See file 'COPYING' for use and warranty information

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
