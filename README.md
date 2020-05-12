# FreeIPA plugin for Fedora Account System

**PROOF OF CONCEPT**

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
* *fasGPGKeyId*: multi-valued string, writable by self, indexec
* *fasCreationTime*: timestamp, writable by admin
* *fasStatusNote*: string, writable by admin
* *fasRHBZEmail*: string, writable by self
* *fasGitHubUsername*: string, writable by self
* *fasGitLabUsername*: string, writable by self
* *fasUserAgreements*: string, writable by self

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

## ACIs

* ``Read FAS user attributes``
* ``Users can modify their own FAS attributes``
* ``Users can modify their own Email address``
* ``Users can remove themselves as members of groups``
* ``Member managers can remove themselves as member managers of groups``

## User settings

* OTP set as default authentication method.

## Indexes

* Index on ``fasIRCNick`` for presence and equality
* Index on ``fasGPGKeyId`` for presence and equality
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
  --fasuseragreements=STR
                        user agreements signed
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
