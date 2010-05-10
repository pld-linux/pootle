# TODO
# - full webapp (all config to webapps dir)
%define		fullname Pootle
Summary:	Localization and translation management web application
Name:		pootle
Version:	2.0.3
Release:	0.1
License:	GPL v2+
Group:		Development/Tools
URL:		http://translate.sourceforge.net/wiki/pootle/index
Source0:	http://downloads.sourceforge.net/project/translate/%{fullname}/%{version}/%{fullname}-%{version}.tar.bz2
# Source0-md5:	6a64e49c0d19ba0d7392bb87efa213b5
Source1:	apache.conf
Patch0:		%{name}-settings.patch
BuildRequires:	python-devel
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	translate-toolkit >= 1.4.1
Requires(post,preun):	/sbin/chkconfig
Requires:	apache-mod_wsgi
Requires:	group(http)
Requires:	iso-codes
Requires:	memcached
Requires:	python-Levenshtein
Requires:	python-django >= 1.0
Requires:	python-djblets
Requires:	python-lxml
Requires:	python-memcached
Requires:	python-xapian >= 1.0.13
Requires:	rc-scripts
Requires:	translate-toolkit >= 1.5.1
Requires:	xapian-core
Requires:	zip
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}

%description
Pootle is web application for managing distributed or crowdsourced
translation.

It's features include::
- Translation of Gettext PO and XLIFF files.
- Submitting to remote version control systems (VCS).
- Managing groups of translators
- Online webbased or offline translation
- Quality checks

%prep
%setup -q -n %{fullname}-%{version}
%patch0 -p1

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install \
	--skip-build \
	--optimize=2 \
	--root=$RPM_BUILD_ROOT

# Create the manpages
install -d $RPM_BUILD_ROOT%{_mandir}/man1
for program in $RPM_BUILD_ROOT%{_bindir}/*; do
	case $(basename $program) in
	PootleServer|import_pootle_prefs)
		;;
	*)
		LC_ALL=C PYTHONPATH=. $program --manpage \
		>  $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $program).1 \
		|| rm -f $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $program).1
		;;
	esac
done

install -d $RPM_BUILD_ROOT{%{_sbindir},%{_datadir}/pootle,%{_sharedstatedir}/pootle,%{_sysconfdir}/pootle}
install -p $RPM_BUILD_ROOT%{_bindir}/PootleServer $RPM_BUILD_ROOT%{_sbindir}
rm $RPM_BUILD_ROOT%{_bindir}/PootleServer
rm -r $RPM_BUILD_ROOT%{py_sitescriptdir}/djblets
install -p wsgi.py $RPM_BUILD_ROOT%{_datadir}/pootle

install -d $RPM_BUILD_ROOT%{_webapps}/%{_webapp}
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service httpd restart
%service -q memcached restart

%postun
if [ "$1" -ge "1" ] ; then
	%service httpd condrestart
	%service -q memcached condrestart
fi

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc ChangeLog README
# We exclude docs as the Pootle installer doesn't do ${name}-${version} as expected in Fedora
%exclude %{_datadir}/doc/pootle
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man1/*
%dir %{_sysconfdir}/pootle
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pootle/localsettings.py
%{_datadir}/pootle
%attr(770,root,http) %{_sharedstatedir}/pootle

%{py_sitescriptdir}/*
