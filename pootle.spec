# TODO
# - move %{_datadir}/pootle/mo/* to system localedir as pootle.mo
# - Can't find the ISO codes package. Pootle uses ISO codes to translate language names.
%define		fullname Pootle
Summary:	Localization and translation management web application
Name:		pootle
Version:	2.0.3
Release:	1
License:	GPL v2+
Group:		Development/Tools
URL:		http://translate.sourceforge.net/wiki/pootle/index
Source0:	http://downloads.sourceforge.net/project/translate/%{fullname}/%{version}/%{fullname}-%{version}.tar.bz2
# Source0-md5:	6a64e49c0d19ba0d7392bb87efa213b5
Source1:	apache.conf
Patch0:		settings.patch
Patch1:		paths.patch
Patch2:		homedir.patch
BuildRequires:	python-devel
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sed >= 4.0
BuildRequires:	translate-toolkit >= 1.4.1
Requires:	apache-mod_mime
Requires:	apache-mod_wsgi
Requires:	group(http)
Requires:	iso-codes
Requires:	python-Levenshtein
Requires:	python-django >= 1.0
Requires:	python-djblets
Requires:	python-lxml
Requires:	translate-toolkit >= 1.5.1
Requires:	zip
Suggests:	memcached
Suggests:	python(sqlite)
Suggests:	python-memcached
Suggests:	python-xapian
Conflicts:	python-xapian < 1.0.13
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
%patch1 -p1
%patch2 -p1

%{__sed} -i -e '1s,#!.*env python,#!%{__python},' wsgi.py

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_datadir}/pootle,%{_sharedstatedir}/pootle/po/.tmp,%{_sysconfdir}}

%{__python} setup.py install \
	--skip-build \
	--optimize=2 \
	--root=$RPM_BUILD_ROOT

# install_dirs.py was modified _after_ install completed, so compile again
# before py_postclean
# TODO. compile only install_dirs.py
%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
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

> %{name}.lang
# application language
for a in $RPM_BUILD_ROOT%{_datadir}/pootle/mo/[a-z]*; do
	# path file and lang
	p=${a#$RPM_BUILD_ROOT} l=${a##*/}
	echo "%lang($l) $p" >> %{name}.lang
done

# such recursive magic is because we need to have different permissions for
# directories and files and we want to language tag both of them
scan_mo() {
	for obj in "$@"; do
		# skip bad globs (happens when we recurse)
		[ -e "$obj" ] || continue
		# path file and lang
		path=${obj#$RPM_BUILD_ROOT} lang=${MO_LANG:-${obj##*/}}

		if [ -d $obj ]; then
			attr='%dir %attr(770,root,http)'
		else
			attr='%attr(660,root,http)'
		fi
		case $lang in
		templates)
			echo "$attr $path" >> %{name}.lang
			;;
		*)
			echo "%lang($lang) $attr $path" >> %{name}.lang
			;;
		esac
		if [ -d $obj ]; then
			MO_LANG=$lang scan_mo $obj/*
			unset MO_LANG
		fi
	done
}
scan_mo $RPM_BUILD_ROOT%{_sharedstatedir}/pootle/po/{pootle,terminology}/* >> %{name}.lang

# don't clobber user $PATH
mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/PootleServer
install -p wsgi.py $RPM_BUILD_ROOT%{_datadir}/pootle

install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

# we do doc in rpm
rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/pootle

# external pkg
rm -r $RPM_BUILD_ROOT%{py_sitescriptdir}/djblets

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files -f %{name}.lang
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
# setup a tempdir inside the PODIRECTORY heirarchy, this way we have
# reasonable guarantee that temp files will be created on the same
# filesystem as translation files (required for save operations).
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/.tmp

# base translations from pootle itself
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/terminology
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/tutorial
%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/tutorial/templates
%attr(660,root,http) %{_sharedstatedir}/pootle/po/tutorial/templates/tutorial.pot
