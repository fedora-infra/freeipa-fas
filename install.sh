#!/bin/sh
set -e

SITE_PACKAGES=$(python3 -c 'from sys import version_info as v; print(f"/usr/lib/python{v.major}.{v.minor}/site-packages")')

if [ -f /usr/share/ipa/schema.d/89-fasschema.ldif -a -f /usr/share/ipa/updates/89-fas.update ]; then
    NEEDS_UPGRADE=0;
else
    NEEDS_UPGRADE=1;
fi

cp schema.d/89-fasschema.ldif /usr/share/ipa/schema.d/
rm -f /usr/share/ipa/schema.d/99-fasschema.ldif

cp updates/89-fas.update /usr/share/ipa/updates/
rm -f /usr/share/ipa/updates/99-fas.update

mkdir -p -m 755 /usr/share/ipa/ui/js/plugins/userfas
cp ui/js/plugins/userfas/userfas.js /usr/share/ipa/ui/js/plugins/userfas/
mkdir -p -m 755 /usr/share/ipa/ui/js/plugins/groupfas
cp ui/js/plugins/groupfas/groupfas.js /usr/share/ipa/ui/js/plugins/groupfas/
mkdir -p -m 755 /usr/share/ipa/ui/js/plugins/fasagreement
cp ui/js/plugins/fasagreement/fasagreement.js \
    /usr/share/ipa/ui/js/plugins/fasagreement/

cp ipaserver/plugins/*.py ${SITE_PACKAGES}/ipaserver/plugins/
python3 -m compileall ${SITE_PACKAGES}/ipaserver/plugins/

mkdir -p /usr/local/bin
install -p -m 755 create-agreement.py /usr/local/bin/ipa-create-agreement

if [ $NEEDS_UPGRADE = 1 ]; then
    ipa-server-upgrade
else
    ipa-ldap-updater \
        -S /usr/share/ipa/schema.d/89-fasschema.ldif \
        /usr/share/ipa/updates/89-fas.update
    systemctl restart httpd.service
fi

echo "NOTE: $0 is a hack for internal development."
echo "Some changes require a proper ipa-server-upgrade or ipactl restart."
