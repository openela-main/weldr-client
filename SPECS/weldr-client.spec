# Pass --with tests to rpmbuild to build composer-cli-tests
%bcond_with tests
# Pass --without signed to skip gpg signed tar.gz (DO NOT DO THAT IN PRODUCTION)
%bcond_without signed

%global goipath         github.com/osbuild/weldr-client/v2

Name:      weldr-client
Version:   35.9
Release:   2%{?dist}
# Upstream license specification: Apache-2.0
License:   ASL 2.0
Summary:   Command line utility to control osbuild-composer

%gometa
Url:       %{gourl}
Source0:   https://github.com/osbuild/weldr-client/releases/download/v%{version}/%{name}-%{version}.tar.gz
%if %{with signed}
Source1:   https://github.com/osbuild/weldr-client/releases/download/v%{version}/%{name}-%{version}.tar.gz.asc
Source2:   https://keys.openpgp.org/vks/v1/by-fingerprint/117E8C168EFE3A7F#/gpg-117E8C168EFE3A7F.key
%endif

Obsoletes: composer-cli < 35.0
Provides: composer-cli = %{version}-%{release}

Requires: diffutils

BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
%if 0%{?fedora}
BuildRequires:  golang(github.com/BurntSushi/toml)
BuildRequires:  golang(github.com/spf13/cobra)
# Required for tests and %check
BuildRequires:  golang(github.com/stretchr/testify/assert)
BuildRequires:  golang(github.com/stretchr/testify/require)
%endif

BuildRequires: git-core
BuildRequires: make
BuildRequires: gnupg2


%description
Command line utility to control osbuild-composer

%prep
%if %{with signed}
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%endif
%if 0%{?rhel}
%forgeautosetup -p1
%else
%goprep
%endif

%build
export LDFLAGS="-X %{goipath}/cmd/composer-cli/root.Version=%{version} "

%if 0%{?rhel}
GO_BUILD_PATH=$PWD/_build
install -m 0755 -vd $(dirname $GO_BUILD_PATH/src/%{goipath})
ln -fs $PWD $GO_BUILD_PATH/src/%{goipath}
cd $GO_BUILD_PATH/src/%{goipath}
install -m 0755 -vd _bin
export PATH=$PWD/_bin${PATH:+:$PATH}
export GOPATH=$GO_BUILD_PATH:%{gopath}
export GOFLAGS=-mod=vendor
%else
export GOPATH="%{gobuilddir}:${GOPATH:+${GOPATH}:}%{?gopath}"
export GO111MODULE=off
%endif
%gobuild -o composer-cli %{goipath}/cmd/composer-cli


## TODO
##make man

%if %{with tests} || 0%{?rhel}
export BUILDTAGS="integration"

# Build test binaries with `go test -c`, so that they can take advantage of
# golang's testing package. The RHEL golang rpm macros don't support building them
# directly. Thus, do it manually, taking care to also include a build id.
#
# On Fedora go modules have already been turned off, and the path set to the one into which
# the golang-* packages install source code.
export LDFLAGS="${LDFLAGS:-} -linkmode=external -compressdwarf=false -B 0x$(od -N 20 -An -tx1 -w100 /dev/urandom | tr -d ' ')"
go test -c -tags=integration -buildmode pie -compiler gc -ldflags="${LDFLAGS}" -o composer-cli-tests %{goipath}/weldr
%endif

%install
make DESTDIR=%{buildroot} install

%if %{with tests} || 0%{?rhel}
make DESTDIR=%{buildroot} install-tests
%endif

%check
%if 0%{?fedora}
export GOPATH="%{gobuilddir}:${GOPATH:+${GOPATH}:}%{?gopath}"
export GO111MODULE=off
%endif

# Run the unit tests
export LDFLAGS="-X %{goipath}/cmd/composer-cli/root.Version=%{version} "
make test


%files
%license LICENSE
%doc examples HACKING.md README.md
%{_bindir}/composer-cli
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/bash_completion.d/composer-cli
%{_mandir}/man1/composer-cli*

%if %{with tests} || 0%{?rhel}
%package tests
Summary:    Integration tests for composer-cli

Requires: createrepo_c

%description tests
Integration tests to be run on a pristine-dedicated system to test the
composer-cli package.

%files tests
%license LICENSE
%{_libexecdir}/tests/composer-cli/
%endif


%changelog
* Tue Feb 14 2023 Brian C. Lane <bcl@redhat.com> - 35.9-2
- tests: Remove default repos before running tests
  Related: rhbz#2168666

* Wed Nov 30 2022 Brian C. Lane <bcl@redhat.com> - 35.9-1
- Copy rhel-88.json test repository from osbuild-composer
- Update osbuild-composer test repositories from osbuild-composer
- New release: 35.9 (bcl)
  Resolves: rhbz#2168666
- tests: Replace os.MkdirTemp with t.TempDir (bcl)
- blueprint save: Allow overriding bad blueprint names (bcl)
- tests: Clean up checking err in tests (bcl)
- composer-cli: Implement blueprints diff (bcl)
- saveBlueprint: Return the filename to the caller (bcl)
- composer-cli: Add tests for using --commit with old servers (bcl)
- weldr: Return error about the blueprints change route (bcl)
- weldr: Save the http status code as part of APIResponse (bcl)
- Add --commit support to blueprints save (bcl)
- Add --commit to blueprints show (bcl)
- gitleaks: Exclude the test password used in tests (bcl)
- ci: add tags to AWS instances (tlavocat)
- Update github.com/BurntSushi/toml to 1.2.1
- Update github.com/stretchr/testify to 1.8.1
- Update bump github.com/spf13/cobra to 1.6.1
- New release: 35.8 (bcl)
- completion: Remove providers from bash completion script (bcl)
- completion: Filter out new headers from compose list (bcl)
- docs: Remove unneeded Long descriptions (bcl)
- docs: Use a custom help template (bcl)
- docs: Add more command documentation (bcl)
- cmdline: Add package glob support to modules list command (bcl)
- workflow: Add govulncheck on go v1.18 (bcl)
- tests: Update to use golangci-lint 1.49.0 (bcl)
- New release: 35.7 (bcl)
- spec: Move %%gometa macro above %%gourl (bcl)
- weldr: When starting a compose pass size as bytes, not MiB (bcl)
- tests: Use correct size value in bytes for test (bcl)
- workflow: Add Go 1.18 to text matrix (bcl)
- Replace deprecated ioutil functions (bcl)
- New release: 35.6 (bcl)
- tests: Update tests for osbuild-composer changes (bcl)
- CMD: Compose status format (eloy.coto)
- CMD: Compose list format (eloy.coto)
- tests: Update tests to check for JSON list output (bcl)
- composer-cli: Change JSON output to be a list of objects (bcl)
- weldr: Simplify the old ComposeLog, etc. functions (bcl)
- composer-cli: Add --filename to blueprints freeze save command (bcl)
- composer-cli: Add --filename to blueprints save command (bcl)
- composer-cli: Add --filename to compose logs command (bcl)
- composer-cli: Add --filename to compose image command (bcl)
- composer-cli: Add --filename to compose metadata command (bcl)
- composer-cli: Add --filename to compose results command (bcl)
- weldr: Add saving to a new filename to GetFilePath function (bcl)
- github: Fix issue with codecov and forced pushes in PRs (bcl)
- Use golangci-lint 1.45.2 in workflow (bcl)
- Run workflow tests for go 1.16.x and 1.17.x (bcl)
- Move go.mod to go 1.16 (bcl)
- workflows/trigger-gitlab: run Gitlab CI in new image-builder project (jrusz)
- Update GitHub actions/setup-go to 3
- Update GitHub actions/checkout to 3

* Tue Aug 16 2022 Brian C. Lane <bcl@redhat.com> - 35.5-4
- tests: Update tests for osbuild composer changes
  Resolves: rhbz#2118829

* Tue Aug 16 2022 Brian C. Lane <bcl@redhat.com> - 35.5-3
- tests: Update repositories so tests will run
  Related: rhbz#2116773

* Tue Aug 16 2022 Brian C. Lane <bcl@redhat.com> - 35.5-2
- Rebuild with golang 1.18.4 for multiple golang CVEs
  Resolves: rhbz#2116773

* Tue Feb 15 2022 Brian C. Lane <bcl@redhat.com> - 35.5-1
- New release: 35.5 (bcl)
  Resolves: rhbz#2052604
- docs: Explain how to undo blueprints delete (bcl)
- test: server status no longer returns devel (bcl)
- Use GetFrozenBlueprintsTOML for blueprints freeze save (bcl)
- Add a test for float uid/gid in frozen blueprint (bcl)
- Use GetBlueprintsTOML for blueprints save (bcl)
- test: Add a test for float uid/gid in saved blueprint (bcl)
- build(deps): bump github.com/BurntSushi/toml from 0.4.1 to 1.0.0 (49699333+dependabot[bot])
- tests: trigger on push to main (jrusz)
- build(deps): bump github.com/spf13/cobra from 1.2.1 to 1.3.0 (49699333+dependabot[bot])
- ci: add keystore for sonarqube (jrusz)
- spec: Switch to using %%gobuild macro on Fedora (bcl)
- ci: change workflow name (jrusz)
- ci: add gitlab-ci and sonarqube (jrusz)
- doc: fix example links from the README (tdecacqu)
- build(deps): bump actions/checkout from 2.3.4 to 2.4.0 (49699333+dependabot[bot])
- ci: Enable Coverity Scan tool (atodorov)
