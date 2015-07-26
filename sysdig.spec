#
# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_without	dkms		# build dkms package

%if "%{?alt_kernel}" != "" && 0%{?build_kernels:1}
	%{error:alt_kernel (%{?alt_kernel}) and build_kernels (%{?build_kernels}) defined}
%endif

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
%undefine	with_dkms
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	0.3
%define		pname	sysdig
Summary:	sysdig, a system-level exploration and troubleshooting tool
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	0.1.101
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2
Group:		Applications/System
Source0:	https://github.com/draios/sysdig/archive/%{version}/%{pname}-%{version}.tar.gz
# Source0-md5:	5fe96a3a0fd98b2157a40cb29af41afc
URL:		http://www.sysdig.org/
BuildRequires:	rpmbuild(macros) >= 1.701
%if %{with userspace}
BuildRequires:	cmake >= 2.8.2
BuildRequires:	jsoncpp-devel
BuildRequires:	libstdc++-devel >= 6:4.4
BuildRequires:	luajit-devel >= 2.0.3
BuildRequires:	ncurses-devel >= 5.9
BuildRequires:	zlib-devel >= 1.2.8
%endif
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
ExclusiveArch:	%{ix86} %{x8664}
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

%package -n dkms-%{name}
Summary:	DKMS-ready driver for sysdig
License:	GPL v2+
Group:		Base/Kernel
Requires(pre,post):	dkms >= 2.1.0.0
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n dkms-%{name}
This package contains a DKMS-ready driver for sysdig.

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

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-misc-%{pname}\
Summary:	Linux driver for sysdig\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-misc-%{pname}\
This is driver for sysdig-probe for Linux.\
\
This package contains Linux module.\
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

# we need just obj-m from the file
cp driver/Makefile{.in,}
%{__sed} -i -e 's/@KBUILD_FLAGS@//' driver/Makefile

%build
%{?with_kernel:%{expand:%build_kernel_packages}}

%if %{with userspace}
install -d build
cd build
%cmake \
	-DDIR_ETC=%{_sysconfdir} \
	-DSYSDIG_VERSION=%{version}-%{release} \
	-DBUILD_DRIVER=OFF \
	-DUSE_BUNDLED_JSONCPP=OFF \
	-DUSE_BUNDLED_LUAJIT=OFF \
	-DUSE_BUNDLED_NCURSES=OFF \
	-DUSE_BUNDLED_ZLIB=OFF \
	..
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with userspace}
%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n dkms-%{name}
%{_sbindir}/dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade && \
%{_sbindir}/dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade && \
%{_sbindir}/dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade || :

%preun -n dkms-%{name}
%{_sbindir}/dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all || :

%if %{with userspace}
%files
%defattr(644,root,root,755)
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
%{_datadir}/zsh/vendor-completions/_sysdig
%endif

%if %{with dkms}
%files -n dkms-%{name}
%defattr(644,root,root,755)
%{_usrsrc}/%{name}-%{version}-%{release}
%endif
