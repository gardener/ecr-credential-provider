# ECR-credential-provider

This repository builds container images of the Amazon ECR credential provider from
[cloud-provider-aws](https://github.com/kubernetes/cloud-provider-aws) source code.
Gardener's node agent extracts the binary from the image, and kubelet uses it to
authenticate when pulling private ECR images on AWS.

## Upstream Source

`.ocm/upstream-source.json` selects the upstream source used by snapshot and release
builds. Its `version` names a released upstream version, and `access.commit` records
the full commit ID identifying the source code to build. The `access.ref` value,
such as `refs/tags/v1.37.0`, tells Git to fetch the tag named `v1.37.0`.

Each build fetches that tag, checks that it points to the recorded commit, and
builds the credential-provider binary from that commit. The image contains the
binary at `/bin/ecr-credential-provider` and supports Linux amd64 and arm64.

The release's Open Component Model (OCM) descriptor records where its source code
comes from. It lists this repository as the main source and the selected upstream
release and commit as an additional source.

## Updating Versions

This repository packages upstream code into an image, so it has two version values:

- `VERSION` sets this repository's image and component version.
- `.ocm/upstream-source.json` selects the upstream release and commit to build.

To adopt an upstream release, review its source changes and update `version`,
`access.ref`, and `access.commit` in `.ocm/upstream-source.json` together. Obtain 
the upstream commit ID with:

```sh
git ls-remote https://github.com/kubernetes/cloud-provider-aws.git \
  'refs/tags/v1.37.0' 'refs/tags/v1.37.0^{}'
```

Some Git tags include a message and author information; these are called annotated
tags. Git gives this tag record its own ID, separate from the source commit's ID.
For such tags, the command returns two lines: the tag record followed by the source
commit, whose line ends in `^{}`. Copy the commit ID from the `^{}` line into
`access.commit`. For a tag that returns one line, use the ID from that line.

The release workflow reads the intended image version from `VERSION`, removes
the `-dev` suffix, and publishes the release. After publishing, it advances
`VERSION` to the next development version according to the selected `next-version`
input (`bump-minor` or `bump-patch`). For example, releasing `v1.37.0` with
`bump-minor` writes `v1.38.0-dev` to `VERSION`.

To prepare a release, check that `VERSION` names the intended image version and
adjust it if needed. When adopting new upstream code, also update
`.ocm/upstream-source.json` to the reviewed upstream release and commit.
Release builds require the image and upstream versions to have the same major
and minor numbers (`1.37`, for example). The packaging patch number must be
greater than or equal to the upstream patch number. `VERSION` must be a stable
`vX.Y.Z` version, optionally followed by `-dev`; other suffixes are not accepted
for release builds.

For each new release within a major/minor line, choose the packaging patch as
`max(upstream patch, latest published packaging patch + 1)`. If the line has no
published packaging release, use the upstream patch. This keeps versions equal
when possible, gives build-only changes a new version, and avoids reusing or
decreasing published versions. For example, if packaging `v1.37.1` already builds
upstream `v1.37.0` with a newer Go toolchain, adopting upstream `v1.37.1` requires
packaging `v1.37.2`. Adopting upstream `v1.37.5` next can use packaging `v1.37.5`.

The validator enforces major/minor equality and the patch lower bound; it does
not look up previously published versions. Check published releases and image
tags before selecting a version, and never overwrite an existing release.
The automatic `next-version` bump does not select or update upstream source;
adjust `VERSION` again if needed when adopting an upstream release.

Update the release mapping in [PACKAGING.md](PACKAGING.md) in the same change,
including the upstream version, Go toolchain, and reason for the new build.
The pinned source descriptor remains the machine-readable source of truth.
Do not infer upstream security-fix coverage from the packaging patch number.

Development snapshot images use the upstream release recorded in
`.ocm/upstream-source.json`.
After publishing a release, update the ECR credential-provider image tag in
`gardener-extension-provider-aws/imagevector/images.yaml` to deploy it.

## Security Analysis

Before building images, CI runs gosec v2.30.0 to check for security problems in the
upstream production code used by the credential-provider binary. It identifies
the upstream packages needed for each supported architecture and scans them for
Linux amd64 and arm64. Findings fail the build.

The combined results are stored in SARIF, a standard format for static-analysis
reports. The OCM descriptor includes this report and identifies the upstream
source it covers.

## Local Verification

```sh
python3 -B -m unittest discover -s .ci/tests -v
docker build \
  --build-arg UPSTREAM_VERSION="$(python3 .ci/upstream.py version)" \
  --build-arg UPSTREAM_COMMIT="$(python3 .ci/upstream.py commit)" \
  -t ecr-credential-provider .
```
