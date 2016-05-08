#!/bin/sh
PROG=${0##*/}

# application language
scan_locale() {
	local dir path lang
	for dir in "$@"; do
		dir=${dir%/}
		path=${dir#$RPM_BUILD_ROOT}
		lang=${dir##*/}

		case "$lang" in
		templates)
			continue
			;;
		esac

		echo "%lang($lang) $path"
	done
}

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
			echo "$attr $path"
			;;
		*)
			echo "%lang($lang) $attr $path"
			;;
		esac
		if [ -d $obj ]; then
			MO_LANG=$lang scan_mo $obj/*
			unset MO_LANG
		fi
	done
}

if [ $# = 2 ]; then
	# for using same syntax as rpm own find-lang
	RPM_BUILD_ROOT=$1
	shift
fi

langfile=$1
localedir=$RPM_BUILD_ROOT/usr/share/pootle/locale
podir=$RPM_BUILD_ROOT/var/lib/pootle/po

echo '%defattr(644,root,root,755)' > $langfile

scan_locale $localedir/*/ >> $langfile
scan_mo $podir/terminology/* >> $langfile
scan_mo $podir/tutorial/* >> $langfile

if [ "$(grep -Ev '(^%defattr|^$)' $langfile | wc -l)" -le 0 ]; then
	echo >&2 "$PROG: Error: international files not found!"
	exit 1
fi

exit 0
