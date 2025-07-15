# TODO
# - move %{_datadir}/pootle/mo/* to system localedir as pootle.mo
%define		subver	b3
%define		fullname Pootle
Summary:	Localization and translation management web application
Name:		pootle
Version:	2.8.0
Release:	0.10
License:	GPL v2
Group:		Development/Tools
Source0:	https://github.com/translate/pootle/releases/download/%{version}%{subver}/Pootle-%{version}%{subver}.tar.bz2
# Source0-md5:	c7e86066f78f8a04823309c1b3cf0134
Source1:	apache.conf
Source2:	find-lang.sh
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
Requires:	apache(mod_wsgi)
Requires:	group(http)
Requires:	iso-codes
Requires:	zip
Suggests:	memcached
Suggests:	python(sqlite)
Suggests:	python-memcached
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		find_lang	sh %{_sourcedir}/find-lang.sh %{buildroot}

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
%setup -q -n %{fullname}-%{version}%{?subver}
%patch -P0 -p1
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
%{__rm} -r $RPM_BUILD_ROOT%{py_sitescriptdir}/pytest_pootle

# move these to /var/lib/pootle/po
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}/translations/{terminology,tutorial} \
	$RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/po
rmdir $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}/translations

# move to data dir
mv $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}/{locale,static,assets} \
	$RPM_BUILD_ROOT%{_datadir}/%{name}

# install_dirs.py was modified _after_ install completed, so compile again
# before py_postclean
# TODO. compile only install_dirs.py
%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%find_lang %{name}.lang

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
%doc README.rst INSTALL CONTRIBUTING.rst
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
#%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/localsettings.py
%attr(755,root,root) %{_bindir}/pootle

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/assets
%{_datadir}/%{name}/static
%dir %{_datadir}/%{name}/locale
%{_datadir}/%{name}/locale/LINGUAS
%{_datadir}/%{name}/locale/templates
%if 0
%attr(755,root,root) %{_datadir}/pootle/wsgi.py
%endif

%{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/Pootle-%{version}%{?subver}-py*.egg-info

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
