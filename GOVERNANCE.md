# Governance

## Project scope

This repository is an open-source **LitmusChaos quickstart kit**: curated experiments, automation, documentation, and CI examples. It is not a standalone chaos control plane.

## Decision making

- **Routine changes** (bug fixes, docs, new experiments) merge via pull request after maintainer review.
- **Breaking changes** (CLI flags, default paths, experiment contracts) require a changelog entry and at least one maintainer approval.
- **Release versioning** follows [Semantic Versioning](https://semver.org/) documented in [CHANGELOG.md](CHANGELOG.md).

## Releases

- Release tags use the form `vMAJOR.MINOR.PATCH`.
- Release artifacts: GitHub release notes, Helm chart tarball, SPDX SBOM (see `.github/workflows/release.yml`).
- Only maintainers publish tags.

## Security

Report vulnerabilities per [SECURITY.md](SECURITY.md). Do not open public issues for exploitable security bugs.

## Code of conduct

All participants must follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Contributors

Contributors are recognized in release notes and git history. Organizations using this project in production may list themselves in [ADOPTERS.md](ADOPTERS.md).

## Contact

| | |
|---|---|
| **Lead maintainer** | Olúmáyòwá Akinkuehinmi |
| **Email** | [akintunero101@gmail.com](mailto:akintunero101@gmail.com) |
| **GitHub** | [@akintunero](https://github.com/akintunero) |

Security reports: [SECURITY.md](SECURITY.md). Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
