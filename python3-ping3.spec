%global pypi_name python3-ping3
%global srcname ping3

Name:		%{pypi_name}
Version:	5.1.5
Release:	1%{?dist}
Summary:	python3 ICMP ping command and library

License:	MIT
URL:		https://github.com/kyan001/ping3
Source0:	%{srcname}-%{version}.tar.gz
BuildArch:	noarch

BuildRequires: python3-devel

Provides:	%{pypi_name} = %{version}-%{release}

%generate_buildrequires
%pyproject_buildrequires

%description
Ping3 is a pure python3 version of ICMP ping implementation using raw socket.

%prep
%autosetup -n %{srcname}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files ping3

%files -n %{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/ping3

%changelog
* Wed Dec 3 2025 Laurent Vivier <laurent@vivier.eu> - 5.1.5-1
- Initial packaging with pyproject macros
