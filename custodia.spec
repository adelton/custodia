%global custodiaipa_version 0.1.0

Name:           custodia
Version:        0.3.1
Release:        4%{?dist}
Summary:        A service to manage, retrieve and store secrets for other processes

License:        GPLv3+
URL:            https://github.com/latchset/%{name}
Source0:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz.sha512sum.txt
Source2:        custodia.conf
Source5:        custodia.tmpfiles.conf
Patch1:         0001-Vendor-configparser-3.5.0.patch
Patch2:         0002-Patch-and-integrate-vendored-configparser.patch
Patch3:         0003-Remove-etcd-store.patch
Patch4:         0004-Vendor-custodia.ipa.patch
Patch5:         0005-Add-workaround-for-missing-kra_server_server.patch


BuildArch:      noarch

BuildRequires:      python-devel
BuildRequires:      python-jwcrypto
BuildRequires:      python-requests
BuildRequires:      python-setuptools
BuildRequires:      python-coverage
BuildRequires:      pytest
BuildRequires:      python-docutils
BuildRequires:      systemd-python
BuildRequires:      python-ipalib
Requires:           python-custodia = %{version}-%{release}

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


%check
export PYTHONPATH="%{buildroot}/%{python2_sitelib}"
py.test --skip-servertest --ignore=tests/test_ipa.py --ignore=tests/test_cli.py


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

%{__python2} setup.py install --skip-build --root %{buildroot}
mv %{buildroot}/%{_bindir}/custodia %{buildroot}/%{_sbindir}/custodia
install -m 644 -t "%{buildroot}/%{_mandir}/man7" man/custodia.7
install -m 644 -t "%{buildroot}/%{_defaultdocdir}/custodia" README README.custodia.ipa API.md
install -m 644 -t "%{buildroot}/%{_defaultdocdir}/custodia/examples" custodia.conf
install -m 600 %{SOURCE2} %{buildroot}%{_sysconfdir}/custodia
install -m 644 %{SOURCE5} %{buildroot}%{_tmpfilesdir}/custodia.conf
# Recently setuptools stopped installing namespace __init__.py
install -m 644 -t "%{buildroot}/%{python2_sitelib}/custodia" custodia/__init__.py


%post
%systemd_post custodia.socket
%systemd_post custodia.service

%preun
%systemd_preun custodia.socket
%systemd_preun custodia.service

%postun
%systemd_postun custodia.socket
%systemd_postun custodia.service


%files
%doc %{_defaultdocdir}/custodia/README
%doc %{_defaultdocdir}/custodia/API.md
%doc %{_defaultdocdir}/custodia/examples/custodia.conf
%license LICENSE
%{_mandir}/man7/custodia*
%{_sbindir}/custodia
%{_bindir}/custodia-cli
%dir %attr(0700,root,root) %{_sysconfdir}/custodia
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/custodia/custodia.conf
%dir %attr(0700,root,root) %{_localstatedir}/lib/custodia
%dir %attr(0700,root,root) %{_localstatedir}/log/custodia
%{_tmpfilesdir}/custodia.conf

%files -n python-custodia
%license LICENSE
%exclude %{python2_sitelib}/custodia/ipa
%{python2_sitelib}/*

%files -n python-custodia-ipa
%doc %{_defaultdocdir}/custodia/README.custodia.ipa
%{python2_sitelib}/custodia/ipa/*


%changelog
* Tue Jun 20 2017 Christian Heimes <cheimes@redhat.com> - 0.3.1-4
- Add workaround for missing kra_server_server key, resolves #1462403

* Mon Jun 12 2017 Christian Heimes <cheimes@redhat.com> - 0.3.1-3
- Remove custodia user from tmpfiles.d, resolves #1460735
- Add missing systemd hooks for service and socket files
- Drop dependency on python-mock and skip mock tests in check block,
  resolves #1447426

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
