Summary:	sysdig
Name:		sysdig
Version:	0.1.101
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	https://github.com/draios/sysdig/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	5fe96a3a0fd98b2157a40cb29af41afc
URL:		http://www.sysdig.org/
BuildRequires:	cmake >= 2.8.2
BuildRequires:	jsoncpp-devel
BuildRequires:	libstdc++-devel >= 6:4.4
BuildRequires:	luajit-devel >= 2.0.3
BuildRequires:	ncurses-devel >= 5.9
BuildRequires:	zlib-devel >= 1.2.8
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		zshdir %{_datadir}/zsh/site-functions

%description
Sysdig instruments your physical and virtual machines at the OS level
by installing into the Linux kernel and capturing system calls and
other OS events. Then, using sysdig's command line interface, you can
filter and decode these events in order to extract useful information.
Sysdig can be used to inspect systems live in real-time, or to
generate trace files that can be analyzed at a later stage.

%package -n bash-completion-%{name}
Summary:	bash-completion for sysdig
Summary(pl.UTF-8):	Bashowe dopełnianie składni dla sysdig
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-%{name}
bash-completion for sysdig.

%package -n zsh-completion-%{name}
Summary:	zsh-completion for sysdig
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n zsh-completion-%{name}
zsh-completion for sysdig.

%prep
%setup -q

%build
install -d build
cd build
%cmake \
	-DDIR_ETC=%{_sysconfdir} \
	-DBUILD_DRIVER=OFF \
	-DUSE_BUNDLED_JSONCPP=OFF \
	-DUSE_BUNDLED_LUAJIT=OFF \
	-DUSE_BUNDLED_NCURSES=OFF \
	-DUSE_BUNDLED_ZLIB=OFF \
	..
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

# rename "sysdig-0.1.1-dev" to "sysdig-%{version}"
mv $RPM_BUILD_ROOT%{_usrsrc}/{%{name}*,%{name}-%{version}}

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

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
/etc/bash_completion.d/sysdig

%files -n zsh-completion-%{name}
%defattr(644,root,root,755)
%{zshdir}/_sysdig
%{_datadir}/zsh/vendor-completions/_sysdig
