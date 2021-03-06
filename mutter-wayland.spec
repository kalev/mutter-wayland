# NOTE: When editing mutter-wayland.spec, please try to keep it in sync with
# mutter.spec.
#
# mutter-wayland is a temporary fork of mutter, developed in a branch in the
# same upstream git repository as mutter.

Name:          mutter-wayland
Version:       3.9.91
Release:       4%{?dist}
Summary:       Mutter window manager with experimental Wayland support

Group:         User Interface/Desktops
License:       GPLv2+
#VCS:          git:git://git.gnome.org/mutter
URL:           https://wiki.gnome.org/ThreePointNine/Features/WaylandSupport
Source0:       http://download.gnome.org/sources/%{name}/3.9/%{name}-%{version}.tar.xz

BuildRequires: clutter-devel >= 1.13.5
BuildRequires: pango-devel
BuildRequires: startup-notification-devel
BuildRequires: gnome-desktop3-devel
BuildRequires: gtk3-devel >= 3.9.11
BuildRequires: pkgconfig
BuildRequires: gobject-introspection-devel
BuildRequires: libSM-devel
BuildRequires: libX11-devel
BuildRequires: libXdamage-devel
BuildRequires: libXext-devel
BuildRequires: libXrandr-devel
BuildRequires: libXrender-devel
BuildRequires: libXcursor-devel
BuildRequires: libXcomposite-devel
BuildRequires: upower-devel
BuildRequires: zenity
BuildRequires: desktop-file-utils
# Bootstrap requirements
BuildRequires: gtk-doc gnome-common intltool
BuildRequires: libcanberra-devel
BuildRequires: gsettings-desktop-schemas-devel
# Extra dependencies for the mutter-wayland branch
BuildRequires: pam-devel

# Make sure this can't be installed with an old gnome-shell build because of
# an ABI change.
Conflicts: gnome-shell < 3.9.90

# Depend on the mutter package as we are removing the files that overlap
# between mutter and mutter-wayland down below.
Requires: mutter%{?_isa}

Requires: control-center-filesystem
Requires: startup-notification
Requires: dbus-x11
Requires: zenity

%description
Mutter is a window and compositing manager that displays and manages
your desktop via OpenGL. Mutter combines a sophisticated display engine
using the Clutter toolkit with solid window-management logic inherited
from the Metacity window manager.

While Mutter can be used stand-alone, it is primarily intended to be
used as the display core of a larger system such as GNOME Shell. For
this reason, Mutter is very extensible via plugins, which are used both
to add fancy visual effects and to rework the window management
behaviors to meet the needs of the environment.

This package contains an experimental Mutter version with Wayland
support. It will eventually get merged back into the main Mutter
package and mutter-wayland is going to go away; in the mean time this
package is available for early adopters.

%package devel
Summary: Development package for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and libraries for developing Mutter plugins. Also includes
utilities for testing Metacity/Mutter themes.

%prep
%setup -q

%build
(if ! test -x configure; then NOCONFIGURE=1 ./autogen.sh; fi;
 %configure --disable-static --enable-compile-warnings=maximum)

SHOULD_HAVE_DEFINED="HAVE_SM HAVE_SHAPE HAVE_RANDR HAVE_STARTUP_NOTIFICATION"

for I in $SHOULD_HAVE_DEFINED; do
  if ! grep -q "define $I" config.h; then
    echo "$I was not defined in config.h"
    grep "$I" config.h
    exit 1
  else
    echo "$I was defined as it should have been"
    grep "$I" config.h
  fi
done

make %{?_smp_mflags} V=1

%install
%make_install

#Remove libtool archives.
rm -rf %{buildroot}/%{_libdir}/*.la

# Drop man pages for removed utilities; this is fixed in upstream git and won't
# be needed for 3.9.92
rm %{buildroot}%{_mandir}/man1/mutter-message.1*
rm %{buildroot}%{_mandir}/man1/mutter-theme-viewer.1*
rm %{buildroot}%{_mandir}/man1/mutter-window-demo.1*

# Drop files that overlap between the mutter and mutter-wayland packages
rm %{buildroot}%{_datadir}/GConf/gsettings/mutter-schemas.convert
rm %{buildroot}%{_datadir}/glib-2.0/schemas/org.gnome.mutter.gschema.xml
rm %{buildroot}%{_datadir}/gnome-control-center/keybindings/50-mutter-*.xml
rm %{buildroot}%{_datadir}/man/man1/mutter.1*

%find_lang %{name}

# Mutter contains a .desktop file so we just need to validate it
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%post -p /sbin/ldconfig

%postun
/sbin/ldconfig
if [ $1 -eq 0 ]; then
  glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi

%posttrans
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :

%files -f %{name}.lang
%doc README AUTHORS COPYING NEWS HACKING doc/theme-format.txt
%attr(4755,root,root) %{_bindir}/mutter-launch
%{_bindir}/mutter-wayland
%{_datadir}/applications/*.desktop
%{_libdir}/lib*.so.*
%{_libdir}/mutter-wayland/
%{_datadir}/glib-2.0/schemas/org.gnome.mutter.wayland.gschema.xml
%{_datadir}/mutter-wayland/


%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
# exclude as these should be in a devel package (if packaged at all)
%exclude %{_datadir}/gtk-doc

%changelog
* Tue Sep 17 2013 Kalev Lember <kalevlember@gmail.com> - 3.9.91-4
- Review fixes (#1007445)
- Drop the files that overlap between mutter and mutter-wayland and
  depend on the mutter package instead
- Make mutter-launch SUID root
- Update the description and add URL
- Tighten -devel subpackage deps with _isa
- Use the make_install macro

* Fri Sep 06 2013 Jasper St. Pierre <jstpierre@mecheye> - 3.9.91-3
- Initial mutter-wayland packaging based on the mutter package
