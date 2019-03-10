#
# NOTES:
# - https://github.com/draios/sysdig/wiki/How-to-Install-Sysdig-from-the-Source-Code
#
# Conditional build:
%bcond_without	kernel		# kernel modules
%bcond_without	userspace	# userspace packages
%bcond_without	dkms		# DKMS package
%bcond_without	luajit		# use plain lua5.1 instead of luajit

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
%undefine	with_dkms
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif
%ifnarch %{ix86} %{x8664} %{arm} mips ppc
%undefine	with_luajit
%endif

%define		rel	0.1
%define		pname	sysdig
Summary:	sysdig, a system-level exploration and troubleshooting tool
Summary(pl.UTF-8):	sysdig - narzędzie do przeglądu i rozwiązywania problemów na poziomie systemowym
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	0.24.2
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2
Group:		Applications/System
#Source0Download: https://github.com/draios/sysdig/releases
Source0:	https://github.com/draios/sysdig/archive/%{version}/%{pname}-%{version}.tar.gz
# Source0-md5:	ea98fc19fea18f02651a7955d069dcf1
Patch0:		kernel-5.0.patch
URL:		http://www.sysdig.org/
BuildRequires:	rpmbuild(macros) >= 1.701
BuildRequires:	cmake >= 2.8.2
BuildRequires:	curl-devel >= 7.45.0
BuildRequires:	jq-devel >= 1.5
BuildRequires:	jsoncpp-devel
BuildRequires:	libb64-devel >= 1.2.1
BuildRequires:	libstdc++-devel >= 6:4.4
%{!?with_luajit:BuildRequires:	lua51-devel >= 5.1}
%{?with_luajit:BuildRequires:	luajit-devel >= 2.0.3}
BuildRequires:	ncurses-devel >= 5.9
BuildRequires:	openssl-devel >= 1.0.2
BuildRequires:	zlib-devel >= 1.2.8
%{!?with_luajit:BuildConflicts:	luajit-devel}
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
ExclusiveArch:	%{ix86} %{x8664} x32
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# constify %{name}
%{expand:%%global name %{pname}}

%define		zshdir %{_datadir}/zsh/site-functions

%description
Sysdig instruments your physical and virtual machines at the OS level
by installing into the Linux kernel and capturing system calls and
other OS events. Then, using sysdig's command line interface, you can
filter and decode these events in order to extract useful information.
Sysdig can be used to inspect systems live in real-time, or to
generate trace files that can be analyzed at a later stage.

%description -l pl.UTF-8
Sysdig obsługuje maszyny fizyczne i wirtualne na poziomie systemu
operacyjnego, instalując się w jądrze Linuksa i przechwytując
wywołania systemowe oraz inne zdarzenia systemu. Następnie, przy
użyciu interfejsu linii poleceń sysdiga można odfiltrować i zdekodować
te zdarzenia, aby wydobyć z nich przydatne informacje. Sysdiga można
używać do dozorowania systemów w czasie rzeczywistym albo generowania
plików śladów do późniejszej analizy.

%package -n dkms-%{name}
Summary:	DKMS-ready driver for sysdig
Summary(pl.UTF-8):	Sterownik sysdiga zgodny z DKMS
License:	GPL v2+
Group:		Base/Kernel
Requires(pre,post):	dkms >= 2.1.0.0
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n dkms-%{name}
This package contains a DKMS-ready driver for sysdig.

%description -n dkms-%{name} -l pl.UTF-8
Ten pakiet zawiera sterownik sysdiga w postaci zgodnej z DKMS.

%package -n bash-completion-%{name}
Summary:	bash-completion for sysdig command
Summary(pl.UTF-8):	Bashowe dopełnianie składni polecenia sysdig
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{rel}
Requires:	bash-completion
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-%{name}
bash-completion for sysdig command.

%description -n bash-completion-%{name} -l pl.UTF-8
Bashowe dopełnianie składni polecenia sysdig.

%package -n zsh-completion-%{name}
Summary:	zsh-completion for sysdig command
Summary(pl.UTF-8):	Dopełnianie składni polecenia sysdig w powłoce zsh
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{rel}
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n zsh-completion-%{name}
zsh-completion for sysdig command.

%description -n zsh-completion-%{name} -l pl.UTF-8
Dopełnianie składni polecenia sysdig w powłoce zsh.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-misc-%{pname}\
Summary:	Linux driver for sysdig\
Summary(pl.UTF-8):	Sterownik jądra Linuksa dla sysdiga\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-misc-%{pname}\
This is sysdig-probe module for Linux.\
\
%description -n kernel%{_alt_kernel}-misc-%{pname} -l pl.UTF-8\
Ten pakiet zawiera moduł sysdig-probe for jądra Linuksa.\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-misc-%{pname}\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/misc/*.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-misc-%{pname}\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-misc-%{pname}\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -C driver -m sysdig-probe\
%install_kernel_modules -D installed -m driver/sysdig-probe -d misc\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1

%build
install -d build
cd build
%cmake .. \
	-DDIR_ETC=%{_sysconfdir} \
	-DSYSDIG_VERSION=%{version}-%{rel} \
	-DBUILD_DRIVER=OFF \
	-DUSE_BUNDLED_B64=OFF \
	-DUSE_BUNDLED_CURL=OFF \
	-DUSE_BUNDLED_JQ=OFF \
	-DUSE_BUNDLED_JSONCPP=OFF \
	-DUSE_BUNDLED_LUAJIT=OFF \
	-DUSE_BUNDLED_NCURSES=OFF \
	-DUSE_BUNDLED_OPENSSL=OFF \
	-DUSE_BUNDLED_ZLIB=OFF
cd ..

%if %{with kernel}
cp -f build/driver/Makefile.dkms driver/Makefile
%{expand:%build_kernel_packages}
%endif

%if %{with userspace}
%{__make} -C build
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

# already installed as %{zshdir}/_sysdig
%{__rm} $RPM_BUILD_ROOT%{_datadir}/zsh/vendor-completions/_sysdig
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n dkms-%{name}
%{_sbindir}/dkms add -m %{name} -v %{version}-%{rel} --rpm_safe_upgrade && \
%{_sbindir}/dkms build -m %{name} -v %{version}-%{rel} --rpm_safe_upgrade && \
%{_sbindir}/dkms install -m %{name} -v %{version}-%{rel} --rpm_safe_upgrade || :

%preun -n dkms-%{name}
%{_sbindir}/dkms remove -m %{name} -v %{version}-%{rel} --rpm_safe_upgrade --all || :

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/csysdig
%attr(755,root,root) %{_bindir}/sysdig
%attr(755,root,root) %{_bindir}/sysdig-probe-loader
%{_mandir}/man8/csysdig.8*
%{_mandir}/man8/sysdig.8*
%{_datadir}/%{name}

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
/etc/bash_completion.d/sysdig

%files -n zsh-completion-%{name}
%defattr(644,root,root,755)
%{zshdir}/_sysdig
%endif

%if %{with dkms}
%files -n dkms-%{name}
%defattr(644,root,root,755)
%{_usrsrc}/%{name}-%{version}-%{rel}
%endif
