# Packaging History

Packaging releases share the upstream major/minor version. Their patch is at
least the upstream patch and increases for every new packaging release in that
line, including build-only changes. See [the version policy](README.md#updating-versions)
for version selection and collision handling.

For every release, add a row recording the packaging version, upstream version,
Go toolchain, and changes. Keep previous rows unchanged. Review retained build
overrides or source patches when adopting upstream and record whether each is
still needed. Use the source descriptor, [`.ocm/upstream-source.json`](.ocm/upstream-source.json),
at the packaging release tag for the exact upstream commit; this table does not
replace that descriptor.

## Release Mapping

| Packaging version | Upstream version | Go toolchain | Changes / status |
| --- | --- | --- | --- |
| Unreleased (version pending) | vX.Y.Z | X.Y.Z | Pin and verify upstream source, attach provenance and gosec analysis, and enforce the packaging version policy. |
| v1.37.0 | v1.37.0 (requested reference) | 1.26.8 | Historical baseline before source pinning; the resolved upstream commit was not recorded. |

When preparing a release, fill in all three version columns:

- Replace `Unreleased (version pending)` with the packaging version.
- Replace upstream `vX.Y.Z` with the selected upstream version.
- Replace Go toolchain `X.Y.Z` with the Go version used for the release build.

Update
[`.ocm/upstream-source.json`](.ocm/upstream-source.json) to match the selected
upstream release and commit.
Earlier packaging releases have not been backfilled.

## Active Downstream Differences

- The build selects Go 1.26.8 in the Dockerfile and analysis workflow. Review the
  toolchain against upstream requirements and security updates for each release.
- No downstream source patches or dependency overrides are applied.
