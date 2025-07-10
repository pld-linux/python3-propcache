#
# Conditional build:
%bcond_without	doc	# API documentation
%bcond_without	tests	# unit tests

%define		module	propcache
Summary:	Accelerated property cache
Summary(pl.UTF-8):	Akcelerowana pamięć podręczna własności
Name:		python3-%{module}
Version:	0.3.2
Release:	1
License:	Apache v2.0
Group:		Libraries/Python
#Source0Download: https://pypi.org/simple/propcache/
Source0:	https://files.pythonhosted.org/packages/source/p/propcache/%{module}-%{version}.tar.gz
# Source0-md5:	1c073b491620a9f6d568276d61f80277
URL:		https://pypi.org/project/propcache/
BuildRequires:	python3-Cython >= 3.1.2
BuildRequires:	python3-build
BuildRequires:	python3-expandvars
BuildRequires:	python3-installer
BuildRequires:	python3-modules >= 1:3.9
BuildRequires:	python3-setuptools >= 1:47
%if "%{_ver_lt %{py3_ver} 3.11}" == "1"
BuildRequires:	python3-tomli
%endif
%if %{with tests}
BuildRequires:	python3-covdefaults
BuildRequires:	python3-mdit-py-plugins
BuildRequires:	python3-pytest >= 8.3.5
BuildRequires:	python3-pytest-benchmark
BuildRequires:	python3-pytest_codspeed >= 3.2.0
BuildRequires:	python3-pytest-xdist
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
%if %{with doc}
BuildRequires:	python3-myst_parser >= 0.10.0
BuildRequires:	python3-sphinxcontrib-towncrier
BuildRequires:	sphinx-pdg-3 >= 8.2.3
%endif
Requires:	python3-modules >= 1:3.9
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The module provides a fast implementation of cached properties for
Python 3.9+.

%description -l pl.UTF-8
Ten moduł dostarcza szybką implementację własności z pamięcią
podręczną dla Pythona 3.9+.

%package apidocs
Summary:	API documentation for Python %{module} module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona %{module}
Group:		Documentation

%description apidocs
API documentation for Python %{module} module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona %{module}.

%prep
%setup -q -n %{module}-%{version}

# keep *.c files so debuginfo will pick it up
sed -i -e 's#build_inplace: bool = False,#build_inplace: bool = True,#g' -e 's#build_inplace=False#build_inplace=True#g' packaging/pep517_backend/_backend.py

%build
%py3_build_pyproject

%if %{with tests}
%{__python} -m zipfile -e build-3/*.whl build-3-test
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS=pytest_codspeed,xdist,benchmark \
%{__python3} -m pytest -o pythonpath="$PWD/build-3-test" tests
%endif

%if %{with doc}
%{__python} -m zipfile -e build-3/*.whl build-3-doc
PYTHONPATH="$PWD/build-3-doc" \
%{__make} -C docs html \
	SPHINXBUILD=sphinx-build-3
%endif

%install
rm -rf $RPM_BUILD_ROOT

%py3_install_pyproject

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGES.rst README.rst
%dir %{py3_sitedir}/%{module}
%{py3_sitedir}/%{module}/*.py
%{py3_sitedir}/%{module}/*.pyx
%{py3_sitedir}/%{module}/py.typed
%{py3_sitedir}/%{module}/__pycache__
%attr(755,root,root) %{py3_sitedir}/%{module}/*.so
%{py3_sitedir}/%{module}-%{version}.dist-info

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/{_modules,_static,contributing,*.html,*.js}
%endif
