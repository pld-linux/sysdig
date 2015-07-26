Summary:	sysdig
Name:		sysdig
Version:	0.1.101
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	https://github.com/draios/sysdig/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	5fe96a3a0fd98b2157a40cb29af41afc
URL:		http://www.sysdig.org/
BuildRequires:	cmake >= 2.8
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Sysdig instruments your physical and virtual machines at the OS level
by installing into the Linux kernel and capturing system calls and
other OS events. Then, using sysdig's command line interface, you can
filter and decode these events in order to extract useful information.
Sysdig can be used to inspect systems live in real-time, or to
generate trace files that can be analyzed at a later stage.

%prep
%setup -q

%build
mkdir build
cd build
%cmake \
	-DBUILD_DRIVER=OFF \
	..
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_prefix}/src/sysdig* $RPM_BUILD_ROOT%{_prefix}/src/sysdig-%{version}
install -d $RPM_BUILD_ROOT%{_sysconfdir}
mv $RPM_BUILD_ROOT%{_prefix}/etc/bash_completion.d $RPM_BUILD_ROOT%{_sysconfdir}
rm -rf $RPM_BUILD_ROOT%{_datadir}/zsh

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/csysdig
%attr(755,root,root) %{_bindir}/sysdig
%attr(755,root,root) %{_bindir}/sysdig-probe-loader
%{_mandir}/man8/csysdig.8*
%{_mandir}/man8/sysdig.8*
%{_datadir}/%{name}
%{_prefix}/src/sysdig-%{version}
/etc/bash_completion.d/sysdig
