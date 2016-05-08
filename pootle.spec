# TODO
# - move %{_datadir}/pootle/mo/* to system localedir as pootle.mo
%define		fullname Pootle
Summary:	Localization and translation management web application
Name:		pootle
Version:	2.7.3
Release:	0.8
License:	GPL v2
Group:		Development/Tools
Source0:	https://github.com/translate/pootle/releases/download/%{version}/Pootle-%{version}.tar.bz2
# Source0-md5:	b1bac7ae18dc3632c471c63e72852949
Source1:	apache.conf
Patch0:		settings.patch
Patch1:		paths.patch
Patch2:		homedir.patch
URL:		http://pootle.translatehouse.org/
BuildRequires:	python-modules >= 1:2.7
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
BuildRequires:	sed >= 4.0
BuildRequires:	translate-toolkit >= 1.4.1
Requires:	apache-mod_alias
Requires:	apache-mod_authz_host
Requires:	apache-mod_mime
Requires:	apache-mod_wsgi
Requires:	group(http)
Requires:	iso-codes
Requires:	zip
Suggests:	memcached
Suggests:	python(sqlite)
Suggests:	python-memcached
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}

# no appropriate packages in pld
%define		_noautoreq_pyegg	django.*

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
#%patch1 -p1
#%patch2 -p1

#%{__sed} -i -e '1s,#!.*env python,#!%{__python},' wsgi.py

# not packaging for Travis CI
rm pootle/settings/91-travis.conf

rm pootle/log/README
rm pootle/dbs/README

%build
%py_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_datadir}/%{name},%{_sharedstatedir}/%{name}/{dbs,po/.tmp},/var/log/%{name},%{_sysconfdir}}

%py_install
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/tests

# move these to /var/lib/pootle/po
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}/translations/{terminology,tutorial} \
	$RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/po
rmdir $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}/translations

# move to /usr/share
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}/{locale,static,assets} \
	$RPM_BUILD_ROOT%{_datadir}/%{name}

# install_dirs.py was modified _after_ install completed, so compile again
# before py_postclean
# TODO. compile only install_dirs.py
%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

> %{name}.lang
# application language
%if 0
for a in $RPM_BUILD_ROOT%{_datadir}/pootle/mo/[a-z]*; do
	# path file and lang
	p=${a#$RPM_BUILD_ROOT} l=${a##*/}
	echo "%lang($l) $p" >> %{name}.lang
done
%endif

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
			attr='%attr(660,root,http) %config(noreplace) %verify(not md5 mtime size)'
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
scan_mo $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/po/{pootle,terminology,tutorial}/* >> %{name}.lang

# don't clobber user $PATH
#mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/PootleServer
#install -p manage.py $RPM_BUILD_ROOT%{_sbindir}/pootle-manage
#install -p wsgi.py $RPM_BUILD_ROOT%{_datadir}/pootle

install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

# we do doc in rpm
rm -rf $RPM_BUILD_ROOT%{_docdir}/%{name}

# external pkg
#rm -r $RPM_BUILD_ROOT%{py_sitescriptdir}/djblets

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README.rst
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
#%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/localsettings.py
%attr(755,root,root) %{_bindir}/pootle

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/assets
%{_datadir}/%{name}/static
%if 0
%{_datadir}/pootle/mo/README
%attr(755,root,root) %{_datadir}/pootle/wsgi.py
%{_datadir}/pootle/templates
%dir %{_datadir}/pootle/mo
%endif

%{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/Pootle-%{version}-py*.egg-info

%dir %{_sharedstatedir}/%{name}
%dir %attr(770,root,http) %{_sharedstatedir}/%{name}/dbs
%dir %attr(770,root,http) %{_sharedstatedir}/%{name}/po
# setup a tempdir inside the PODIRECTORY heirarchy, this way we have
# reasonable guarantee that temp files will be created on the same
# filesystem as translation files (required for save operations).
%dir %attr(770,root,http) %{_sharedstatedir}/%{name}/po/.tmp

# base translations from pootle itself
#%dir %attr(770,root,http) %{_sharedstatedir}/pootle/po/pootle
# terminology and tutorial po files
%dir %attr(770,root,http) %{_sharedstatedir}/%{name}/po/terminology
%dir %attr(770,root,http) %{_sharedstatedir}/%{name}/po/tutorial

%dir %attr(770,root,http) /var/log/%{name}
