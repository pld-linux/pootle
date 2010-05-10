# TODO
# - move %{_datadir}/pootle/mo/* to system localedir as pootle.mo
# - lang tag languages in /var
%define		fullname Pootle
Summary:	Localization and translation management web application
Name:		pootle
Version:	2.0.3
Release:	0.3
License:	GPL v2+
Group:		Development/Tools
URL:		http://translate.sourceforge.net/wiki/pootle/index
Source0:	http://downloads.sourceforge.net/project/translate/%{fullname}/%{version}/%{fullname}-%{version}.tar.bz2
# Source0-md5:	6a64e49c0d19ba0d7392bb87efa213b5
Source1:	apache.conf
Patch0:		%{name}-settings.patch
BuildRequires:	python-devel
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sed >= 4.0
BuildRequires:	translate-toolkit >= 1.4.1
Requires:	apache-mod_wsgi
Requires:	group(http)
Requires:	iso-codes
Requires:	python-Levenshtein
Requires:	python-django >= 1.0
Requires:	python-djblets
Requires:	python-lxml
Requires:	python-xapian >= 1.0.13
Requires:	translate-toolkit >= 1.5.1
Requires:	xapian-core
Requires:	zip
Suggests:	memcached
Suggests:	python-memcached
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}

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

%{__sed} -i -e 's,^\(INSTALL_CONFIG_DIR\) =.*,\1 = "%{_sysconfdir}",' setup.py

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_datadir}/pootle,%{_sharedstatedir}/pootle,%{_sysconfdir}}
%{__python} setup.py install \
	--skip-build \
	--optimize=2 \
	--root=$RPM_BUILD_ROOT

%py_postclean

# Create the manpages
install -d $RPM_BUILD_ROOT%{_mandir}/man1
for program in $RPM_BUILD_ROOT%{_bindir}/*; do
	case $(basename $program) in
	PootleServer|import_pootle_prefs)
		;;
	*)
		LC_ALL=C PYTHONPATH=. $program --manpage \
		> $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $program).1 \
		|| rm -f $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $program).1
		;;
	esac
done

rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/pootle

mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/PootleServer
rm -r $RPM_BUILD_ROOT%{py_sitescriptdir}/djblets
install -p wsgi.py $RPM_BUILD_ROOT%{_datadir}/pootle

install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc ChangeLog README
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/localsettings.py
%attr(755,root,root) %{_bindir}/import_pootle_prefs
%attr(755,root,root) %{_bindir}/updatetm
%attr(755,root,root) %{_sbindir}/PootleServer
%{_mandir}/man1/updatetm.1*

%dir %{_datadir}/pootle
%{_datadir}/pootle/mo/README
%attr(755,root,root) %{_datadir}/pootle/wsgi.py
%{_datadir}/pootle/html
%{_datadir}/pootle/templates
%dir %{_datadir}/pootle/mo
# TODO: %lang
%{_datadir}/pootle/mo/[a-z]*

%{py_sitescriptdir}/pootle
%{py_sitescriptdir}/pootle_app
%{py_sitescriptdir}/pootle_autonotices
%{py_sitescriptdir}/pootle_misc
%{py_sitescriptdir}/pootle_notifications
%{py_sitescriptdir}/pootle_store
%{py_sitescriptdir}/profiles
%{py_sitescriptdir}/registration
%if "%{py_ver}" > "2.4"
%{py_sitescriptdir}/Pootle-*.egg-info
%endif

%dir %{_sharedstatedir}/pootle
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/dbs
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle/templates
%attr(660,root,http) %{_sharedstatedir}/pootle/po/pootle/templates/pootle.pot

%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/terminology
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/tutorial
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/tutorial/templates
%attr(660,root,http) %{_sharedstatedir}/pootle/po/tutorial/templates/tutorial.pot

# TODO %lang
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle/[a-z][a-z]
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle/[a-z][a-z][a-z]
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle/*[@_]*

%attr(660,root,http) %{_sharedstatedir}/pootle/po/pootle/*/*.po

%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/terminology/*
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/terminology/*/gnome
%attr(660,root,http) %{_sharedstatedir}/pootle/po/terminology/*/gnome/*.po
