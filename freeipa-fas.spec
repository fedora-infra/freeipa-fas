%global debug_package %{nil}
%global plugin_name fas
%global ipa_version 4.8.2

%if 0%{?rhel}
Name:           ipa-%{plugin_name}
%else
Name:           freeipa-%{plugin_name}
%endif
Version:        0.0.4
Release:        1%{?dist}
Summary:        Fedora Account System extension for FreeIPA

BuildArch:      noarch

License:        GPLv3+
URL:            https://github.com/fedora-infra/freeipa-fas
Source0:        https://github.com/fedora-infra/freeipa-fas/archive/%{version}/freeipa-fas-%{version}.tar.gz

BuildRequires: python3-devel
BuildRequires: systemd

%if 0%{?rhel}
Requires:        ipa-server >= %{ipa_version}
Requires(post):  ipa-server >= %{ipa_version}
%else
Provides:        ipa-%{plugin_name} = %{version}-%{release}
Requires:        freeipa-server >= %{ipa_version}
Requires(post):  freeipa-server >= %{ipa_version}
%endif

%description
A module for FreeIPA with extensions for Fedora Account System.

%prep
%autosetup -n freeipa-%{plugin_name}-%{version}

%build
touch debugfiles.list

%install
rm -rf $RPM_BUILD_ROOT

%__mkdir_p %{buildroot}%{python3_sitelib}/ipaserver/plugins
for j in $(find ipaserver/plugins -name '*.py') ; do
    %__cp $j %{buildroot}%{python3_sitelib}/ipaserver/plugins
done

%__mkdir_p %buildroot/%_datadir/ipa/schema.d
for j in $(find schema.d/ -name '*.ldif') ; do
    %__cp $j %buildroot/%_datadir/ipa/schema.d/
done

%__mkdir_p %buildroot/%_datadir/ipa/updates
for j in $(find updates/ -name '*.update') ; do
    %__cp $j %buildroot/%_datadir/ipa/updates/
done

%__mkdir_p %buildroot/%_datadir/ipa/ui/js/plugins
for j in $(find ui/ -name '*.js') ; do
    destdir=%buildroot/%_datadir/ipa/ui/js/plugins/$(basename ${j%.js})
    %__mkdir_p $destdir
    %__cp $j $destdir/
done

%__mkdir_p %buildroot/%_bindir
install -p -m 755 create-agreement.py %buildroot/%_bindir/ipa-create-agreement


%posttrans
python3 -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # This must be run in posttrans so that updates from previous
    # execution that may no longer be shipped are not applied.
    /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

    # Restart IPA processes. This must be also run in postrans so that plugins
    # and software is in consistent state
    # NOTE: systemd specific section

    /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
    if [  $? -eq 0 ]; then
        /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
    fi
fi

%files
%license COPYING
%doc README.md CONTRIBUTORS.txt
%{python3_sitelib}/ipaserver/plugins/*.py
%{python3_sitelib}/ipaserver/plugins/__pycache__/*.pyc
%_datadir/ipa/schema.d/*.ldif
%_datadir/ipa/updates/*.update
%_datadir/ipa/ui/js/plugins/*

%changelog
* Sun Oct 25 2020 Aurelien Bompard <abompard@fedoraproject.org> - 0.0.4-1
- Version 0.0.4

* Mon Aug 17 2020 Aurelien Bompard <abompard@fedoraproject.org> - 0.0.3-1
- Packaging update

* Wed Feb 12 2020 Christian Heimes <cheimes@redhat.com> - 0.0.2-1
- Make new fields readable
- Make mail attribute writeable

* Tue Nov 19 2019 Christian Heimes <cheimes@redhat.com> - 0.0.1-1
- Initial release
