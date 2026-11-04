#!/bin/sh
set -eu

version=${1:?upstream version is required}
commit=${2:?upstream commit is required}
destination=${3:?checkout destination is required}

printf '%s\n' "$version" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$' || {
  echo 'Upstream version must be a stable release tag' >&2
  exit 1
}
printf '%s\n' "$commit" | grep -Eq '^[0-9a-f]{40}$' || {
  echo 'Upstream commit must be a full SHA-1 commit ID' >&2
  exit 1
}

if [ -d "$destination" ] && [ -n "$(ls -A "$destination")" ]; then
  echo 'Checkout destination must be empty' >&2
  exit 1
fi
git init --quiet "$destination"
# Fetch the tag namespace explicitly; never fall back to a same-named branch.
git -C "$destination" fetch --depth=1 --no-tags \
  https://github.com/kubernetes/cloud-provider-aws.git \
  "refs/tags/$version:refs/tags/$version"
resolved=$(git -C "$destination" rev-parse "refs/tags/$version^{commit}")
if [ "$resolved" != "$commit" ]; then
  echo "Upstream tag $version resolves to $resolved, expected $commit" >&2
  exit 1
fi
git -C "$destination" checkout --quiet --detach "$commit"
