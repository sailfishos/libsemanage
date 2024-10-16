# based on work by The Fedora Project (2017)
# Copyright (c) 1998, 1999, 2000 Thai Open Source Software Center Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

%define libsepolver 3.7
%define libselinuxver 3.7

Summary: SELinux binary policy manipulation library
Name: libsemanage
Version: 3.7
Release: 1
License: LGPLv2+
URL: https://github.com/SELinuxProject/selinux/wiki
Source: %{name}-%{version}.tar.bz2
Source1: semanage.conf
BuildRequires: audit-libs-devel
BuildRequires: bison
BuildRequires: bzip2-devel
BuildRequires: dbus-glib-devel
BuildRequires: flex
BuildRequires: libselinux-devel >= %{libselinuxver}
BuildRequires: libsepol-devel >= %{libsepolver}
BuildRequires: swig

BuildRequires: python3-base
BuildRequires: python3-devel

Requires: bzip2-libs audit-libs
Requires: libselinux >= %{libselinuxver}

%description
Security-enhanced Linux is a feature of the Linux® kernel and a number
of utilities with enhanced security functionality designed to add
mandatory access controls to Linux.  The Security-enhanced Linux
kernel contains new architectural components originally developed to
improve the security of the Flask operating system. These
architectural components provide general support for the enforcement
of many kinds of mandatory access control policies, including those
based on the concepts of Type Enforcement®, Role-based Access
Control, and Multi-level Security.

libsemanage provides an API for the manipulation of SELinux binary policies.
It is used by checkpolicy (the policy compiler) and similar tools, as well
as by programs like load_policy that need to perform specific transformations
on binary policies such as customizing policy boolean settings.

%package static
Summary: Static library used to build policy manipulation tools
Requires: libsemanage-devel = %{version}-%{release}

%description static
The semanage-static package contains the static libraries
needed for developing applications that manipulate binary policies.

%package devel
Summary: Header files and libraries used to build policy manipulation tools
Requires: %{name} = %{version}-%{release}

%description devel
The semanage-devel package contains the libraries and header files
needed for developing applications that manipulate binary policies.

%package -n python3-libsemanage
Summary: semanage python 3 bindings for libsemanage
Requires: %{name} = %{version}-%{release}
Requires: libselinux-python3
Provides: %{name}-python3 = %{version}-%{release}
Provides: %{name}-python3 = %{version}-%{release}

%description -n python3-libsemanage
The libsemanage-python3 package contains the python 3 bindings for developing
SELinux management applications.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
# To support building the Python wrapper against multiple Python runtimes
# Define a function, for how to perform a "build" of the python wrapper against
# a specific runtime:
BuildPythonWrapper() {
  BinaryName=$1

  # Perform the build from the upstream Makefile:
  make \
    PYTHON=$BinaryName \
    CFLAGS="%{optflags}" LIBDIR="%{_libdir}" SHLIBDIR="%{_libdir}" \
    pywrap
}

make clean
# only build libsemanage
cd %{name}
make CFLAGS="%{optflags}" swigify
make CFLAGS="%{optflags}" LIBDIR="%{_libdir}" SHLIBDIR="%{_libdir}" all

BuildPythonWrapper \
  %{__python3}

%install
InstallPythonWrapper() {
  BinaryName=$1

  make \
    PYTHON=$BinaryName \
    DESTDIR="${RPM_BUILD_ROOT}" LIBDIR="%{_libdir}" SHLIBDIR="%{_libdir}" \
    install-pywrap
}

# only install libsemanage
cd %{name}
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}
mkdir -p ${RPM_BUILD_ROOT}%{_sharedstatedir}/selinux
mkdir -p ${RPM_BUILD_ROOT}%{_sharedstatedir}/selinux/tmp
make DESTDIR="${RPM_BUILD_ROOT}" LIBDIR="%{_libdir}" SHLIBDIR="%{_libdir}" install

InstallPythonWrapper \
  %{__python3} \
  $(python3-config --extension-suffix)

cp %{SOURCE1} ${RPM_BUILD_ROOT}/etc/selinux/semanage.conf

sed -i '1s%\(#! */usr/bin/python\)\([^3].*\|\)$%\13\2%' %{buildroot}%{_libexecdir}/selinux/semanage_migrate_store

%post
/sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license LICENSE
%dir %{_sysconfdir}/selinux
%config %{_sysconfdir}/selinux/semanage.conf
%{_libdir}/libsemanage.so.2
%dir %{_libexecdir}/selinux
%dir %{_sharedstatedir}/selinux
%dir %{_sharedstatedir}/selinux/tmp

%files static
%{_libdir}/libsemanage.a

%files devel
%{_libdir}/libsemanage.so
%{_libdir}/pkgconfig/libsemanage.pc
%dir %{_includedir}/semanage
%{_includedir}/semanage/*.h
%{_mandir}/man3/*
%{_mandir}/man5/*

%files -n python3-libsemanage
%{python3_sitearch}/*.so
%{python3_sitearch}/semanage.py*
%{python3_sitearch}/__pycache__/semanage*
%{_libexecdir}/selinux/semanage_migrate_store
