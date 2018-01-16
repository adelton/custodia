Name:           custodia
Version:        0.5.0
Release:        1.1%{?dist}
Summary:        A service to manage, retrieve and store secrets for other processes

License:        GPLv3+
URL:            https://github.com/latchset/%{name}
Source0:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz.sha512sum.txt
Source2:        custodia.conf
Source3:        custodia@.service
Source4:        custodia@.socket
Source5:        custodia.tmpfiles.conf
Patch1:         0001-Vendor-configparser-3.5.0.patch
Patch2:         0002-Patch-and-integrate-vendored-configparser.patch
Patch3:         0003-Remove-etcd-store.patch
Patch4:         0004-Vendor-custodia.ipa.patch
Patch5:         0005-Add-workaround-for-missing-kra_server_server-0.5.patch


BuildArch:      noarch

BuildRequires:      python-devel
BuildRequires:      python-jwcrypto
BuildRequires:      python-requests
BuildRequires:      python-requests-gssapi
BuildRequires:      python-setuptools
BuildRequires:      python-coverage
BuildRequires:      pytest
BuildRequires:      python-virtualenv
BuildRequires:      python-docutils
BuildRequires:      systemd-python
BuildRequires:      python-ipalib
BuildRequires:      python-ipaclient

Requires:           python-custodia = %{version}-%{release}

Requires(pre):      shadow-utils
Requires(preun):    systemd-units
Requires(postun):   systemd-units
Requires(post):     systemd-units

%global overview                                                           \
Custodia is a Secrets Service Provider, it stores or proxies access to     \
keys, password, and secret material in general. Custodia is built to       \
use the HTTP protocol and a RESTful API as an IPC mechanism over a local   \
Unix Socket. It can also be exposed to a network via a Reverse Proxy       \
service assuming proper authentication and header validation is            \
implemented in the Proxy.                                                  \
                                                                           \
Custodia is modular, the configuration file controls how authentication,   \
authorization, storage and API plugins are combined and exposed.


%description
A service to manage, retrieve and store secrets for other processes

%{overview}

%package -n python-custodia
Summary:    Sub-package with python2 custodia modules
Provides:   python2-custodia = %{version}-%{release}
Requires:   python-jwcrypto
Requires:   python-requests
Requires:   python-requests-gssapi
Requires:   python-setuptools
Requires:   systemd-python

%description -n python-custodia
Sub-package with python2 custodia modules

%{overview}

%package -n python-custodia-ipa
Summary:    Sub-package with python2 custodia.ipa vault module
Requires:   python-custodia = %{version}-%{release}
Requires:   python-ipalib
Requires:   ipa-client

%description -n python-custodia-ipa
Sub-package with python2 custodia.ipa vault module

%{overview}

%prep
grep `sha512sum %{SOURCE0}` %{SOURCE1} || (echo "Checksum invalid!" && exit 1)
%setup
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1


%build
%{__python2} setup.py egg_info build


%install
mkdir -p %{buildroot}/%{_sbindir}
mkdir -p %{buildroot}/%{_mandir}/man7
mkdir -p %{buildroot}/%{_defaultdocdir}/custodia
mkdir -p %{buildroot}/%{_defaultdocdir}/custodia/examples
mkdir -p %{buildroot}/%{_sysconfdir}/custodia
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}/%{_tmpfilesdir}
mkdir -p %{buildroot}/%{_localstatedir}/lib/custodia
mkdir -p %{buildroot}/%{_localstatedir}/log/custodia
mkdir -p %{buildroot}/%{_localstatedir}/run/custodia

%{__python2} setup.py install --skip-build --root %{buildroot}
mv %{buildroot}/%{_bindir}/custodia %{buildroot}/%{_sbindir}/custodia
install -m 644 -t "%{buildroot}/%{_mandir}/man7" man/custodia.7
install -m 644 -t "%{buildroot}/%{_defaultdocdir}/custodia" README README.custodia.ipa API.md
install -m 644 -t "%{buildroot}/%{_defaultdocdir}/custodia/examples" custodia.conf
install -m 600 %{SOURCE2} %{buildroot}%{_sysconfdir}/custodia
install -m 644 %{SOURCE3} %{buildroot}%{_unitdir}
install -m 644 %{SOURCE4} %{buildroot}%{_unitdir}
install -m 644 %{SOURCE5} %{buildroot}%{_tmpfilesdir}/custodia.conf


%check
# create a virtual env like tox
mkdir -p build
virtualenv --system-site-packages --python=%{__python2} build/testenv
# copy package files into virtual env
cp -R %{buildroot}%{python2_sitelib}/* build/testenv/lib/python2.7/site-packages/
cp %{buildroot}%{_bindir}/custodia-cli build/testenv/bin
cp %{buildroot}%{_sbindir}/custodia build/testenv/bin
# test
build/testenv/bin/python build/testenv/bin/custodia --help
build/testenv/bin/python build/testenv/bin/custodia-cli --help
build/testenv/bin/python build/testenv/bin/custodia-cli plugins
build/testenv/bin/python -m py.test --skip-servertest
# cleanup
rm -rf build/testenv


%pre
getent group custodia >/dev/null || groupadd -r custodia
getent passwd custodia >/dev/null || \
    useradd -r -g custodia -d / -s /sbin/nologin \
    -c "User for custodia" custodia
exit 0

%post
%systemd_post custodia@\*.socket
%systemd_post custodia@\*.service

%preun
%systemd_preun custodia@\*.socket
%systemd_preun custodia@\*.service

%postun
%systemd_postun custodia@\*.socket
%systemd_postun custodia@\*.service


%files
%doc %{_defaultdocdir}/custodia/README
%doc %{_defaultdocdir}/custodia/API.md
%doc %{_defaultdocdir}/custodia/examples/custodia.conf
%license LICENSE
%{_mandir}/man7/custodia*
%{_sbindir}/custodia
%{_bindir}/custodia-cli
%dir %attr(0700,custodia,custodia) %{_sysconfdir}/custodia
%config(noreplace) %attr(600,custodia,custodia) %{_sysconfdir}/custodia/custodia.conf
%attr(644,root,root) %{_unitdir}/custodia@.socket
%attr(644,root,root) %{_unitdir}/custodia@.service
%dir %attr(0700,custodia,custodia) %{_localstatedir}/lib/custodia
%dir %attr(0700,custodia,custodia) %{_localstatedir}/log/custodia
%dir %attr(0755,custodia,custodia) %{_localstatedir}/run/custodia
%attr(644,root,root) %{_tmpfilesdir}/custodia.conf


%files -n python-custodia
%license LICENSE
%exclude %{python2_sitelib}/custodia/ipa
%{python2_sitelib}/*


%files -n python-custodia-ipa
%doc %{_defaultdocdir}/custodia/README.custodia.ipa
%{python2_sitelib}/custodia/ipa


%changelog
* Tue Jul 04 2017 Jan Pazdziora - 0.5.0-1.1
- 1462403 - Add 0005-Add-workaround-for-missing-kra_server_server.patch.

* Thu May 11 2017 Christian Heimes <cheimes@redhat.com> - 0.5.0-1
- Rebase to Custodia 0.5.0
- Vendor custodia.ipa 0.4.1
- Create custodia user and group
- Introduced named systemd instances
- related: #1403214

* Fri Mar 31 2017 Christian Heimes <cheimes@redhat.com> - 0.3.1-2
- Exclude empty directory custodia/ipa from python-custodia

* Fri Mar 31 2017 Christian Heimes <cheimes@redhat.com> - 0.3.1-1
- Rebase to Custodia 0.3.1
- Vendor custodia.ipa 0.1.0
- Vendor backports.configparser 3.5.0 final
- related: #1403214

* Tue Mar 28 2017 Christian Heimes <cheimes@redhat.com> - 0.3.0-4
- Fix whitespace handling in URLs
- Use upstream patches to replace patches for setuptools and configparser
- resolves: #1436763

* Fri Mar 17 2017 Christian Heimes <cheimes@redhat.com> - 0.3.0-3
- custodia depends on python-custodia

* Fri Mar 17 2017 Christian Heimes <cheimes@redhat.com> - 0.3.0-2
- Fix package dependencies and package names to use python prefix

* Wed Mar 15 2017 Christian Heimes <cheimes@redhat.com> - 0.3.0-1
- Update to custodia 0.3.0
- Vendor backports.configparser 3.5.0b2
- Fix compatibility issues with old setuptools
- Add tmpfiles.d config for /run/custodia

* Wed Sep 07 2016 Christian Heimes <cheimes@redhat.com> - 0.1.0-4
- Disable tests (broken on build machines)
- related: #1371902

* Wed Sep 07 2016 Simo Sorce <simo@redhat.com> - 0.1.0-3
- Change default to use RSA OAEP padding
- resolves: #1371902

* Mon Apr 04 2016 Christian Heimes <cheimes@redhat.com> - 0.2.1-2
- Correct download link

* Thu Mar 31 2016 Christian Heimes <cheimes@redhat.com> - 0.1.0-1
- Initial packaging
