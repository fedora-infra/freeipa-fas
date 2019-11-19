# FreeIPA plugin for Fedora Account System

**PROOF OF CONCEPT**

The *freeip-fas* plugin provides schema extension of FreeIPA users for
the Fedora Account System. The plugin must be installed on all FreeIPA
servers, preferable before the server/replica is installed.

## Additional user attributes

User object is extended by the new *fasUser* object class.

* *fasTimeZone*: string, writable by self
* *fasLocale*: string, writable by self
* *fasIRCNick*: string, writable by self, indexed
* *fasGPGKeyId*: multi-valued string, writable by self, indexec
* *fasCreationTime*: timestamp, writable by admin
* *fasStatusNote*: string, writable by admin

### ACIs

* ``Read FAS user attributes``
* ``Users can modify their own FAS attributes``

## Indexes

* Index on ``fasIRCNick`` for presence and equality
* Index on ``fasGPGKeyId`` for presence and equality

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
