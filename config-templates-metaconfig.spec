%define tplroot %{?_datarootdir}%{!?_datarootdir:%{_datadir}}
%define tpldir %{tplroot}/quattor/templates/metaconfig}

Name: config-templates-metaconfig
Version: 0.1.0
Release: 1%{?dist}
Summary: Templates for services configured with ncm-metaconfig and Template::Toolkit
Group: Applications/System
License: Apache 2
URL: http://www.ugent.be/hpc
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Requires: perl(Template)

%description

Skeletons of configuration files for services that will be configured
with ncm-metaconfig.

%prep
%setup -q


%build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{tpldir}/perfsonar/
install lookup_service.tt $RPM_BUILD_ROOT/%{tpldir}/perfsonar/


%files
%{tpldir}/*



%changelog
* Tue Sep 11 2012 Luis Fernando Muñoz Mejías <munoz@Luis.Munoz@UGent.be> - 0.1.0-1
- Initial build.
