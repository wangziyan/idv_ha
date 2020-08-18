Name:		ovp-idv-ha
Version:	%{VCS_VERSION}
Release:	%{VCS_RELEASE}%{?dist}
License:	GPLv3
Group:		Applications/System
URL:		http://www.acer.com
Summary:	ovp idv ha

Requires: python-libs, python, python-thrift, python2-scapy

%description
Implementation of Acer AVD Server IDV HA

%post
ln -sf /usr/share/ovp-idv-ha/idv_ha_client /usr/bin/idv_ha_client
ln -sf /usr/share/ovp-idv-ha/idv_ha_server /usr/bin/idv_ha_server

#systemctl disable keepalived drbd
systemctl daemon-reload
systemctl enable ovp-idv-ha
systemctl start ovp-idv-ha

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service
rm -f /usr/bin/idv_ha_client
rm -f /usr/bin/idv_ha_server

%install
cd %{_builddir}/%{name}

mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_datarootdir}/ovp-idv-ha/
mkdir -p %{buildroot}%{_sysconfdir}/keepalived/
mkdir -p %{buildroot}%{_sysconfdir}/ovp/idv_ha/

cp -rf idv_ha %{buildroot}%{_datarootdir}/ovp-idv-ha/
cp *.py %{buildroot}%{_datarootdir}/ovp-idv-ha/
cp -f idv_ha_client %{buildroot}%{_datarootdir}/ovp-idv-ha/
cp -f idv_ha_server %{buildroot}%{_datarootdir}/ovp-idv-ha/
cp -f ovp-idv-ha.service %{buildroot}%{_unitdir}
cp -f idv_ha.conf %{buildroot}%{_datarootdir}/ovp-idv-ha/idv_ha.conf
cp -f keepalived.conf %{buildroot}%{_sysconfdir}/keepalived/keepalived.conf

%files
%defattr (-,root,root,0644)

%{_unitdir}/ovp-idv-ha.service
%{_sysconfdir}/keepalived/keepalived.conf
%{_sysconfdir}/ovp/idv_ha/idv_ha.conf
%{_datadir}/ovp-idv-ha/*

%attr(755, root, root) %{_datadir}/ovp-idv-ha/idv_ha_server
%attr(755, root, root) %{_datadir}/ovp-idv-ha/idv_ha_client

%changelog
* Fri Aug 14 2020 wzy <Ziyan.Wang@acer.com> - 1.0
- build init version.
