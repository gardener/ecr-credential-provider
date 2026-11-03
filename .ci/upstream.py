#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / '.ocm/upstream-source.json'
RELEASE = re.compile(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')
COMMIT_SHA1 = re.compile(r'[0-9a-f]{40}')


def load_source(path=LOCK):
    with open(path) as stream:
        source = json.load(stream)
    version = source['version']
    access = source['access']
    if not RELEASE.fullmatch(version):
        raise ValueError('Upstream version must be a stable release tag')
    if not COMMIT_SHA1.fullmatch(access['commit']):
        raise ValueError('Upstream commit must be a full SHA-1 commit ID')
    if (source['name'], source['type'], access['type'], access['repoUrl'], access['ref']) != (
        'cloud-provider-aws', 'git', 'github',
        'github.com/kubernetes/cloud-provider-aws', f'refs/tags/{version}',
    ):
        raise ValueError('Unexpected upstream source identity or tag reference')
    return source


def validate_release(source, mode, packaging_version):
    if mode not in ('snapshot', 'release'):
        raise ValueError('Mode must be snapshot or release')
    if mode == 'release':
        packaging = re.fullmatch(
            RELEASE.pattern + r'(?:-dev)?', packaging_version,
        )
        if not packaging:
            raise ValueError('Packaging version must be a stable release with an optional -dev suffix')
        upstream = RELEASE.fullmatch(source['version'])
        if packaging.group(1, 2) != upstream.group(1, 2):
            raise ValueError('Packaging and upstream release must have the same major/minor version')
        if int(packaging.group(3)) < int(upstream.group(3)):
            raise ValueError('Packaging patch version must be greater than or equal to upstream patch version')


def checkout(source, destination):
    subprocess.run([
        'sh', str(ROOT / '.ci/checkout-upstream.sh'),
        source['version'], source['access']['commit'], str(destination),
    ], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('version', 'commit', 'prepare'))
    parser.add_argument('--mode', choices=('snapshot', 'release'))
    parser.add_argument('--checkout', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = load_source()
    if args.command == 'version':
        print(source['version'])
    elif args.command == 'commit':
        print(source['access']['commit'])
    else:
        validate_release(source, args.mode, (ROOT / 'VERSION').read_text().strip())
        if args.checkout is None or args.output is None:
            parser.error('prepare requires --checkout and --output')
        checkout(source, args.checkout)
        with args.output.open('a') as stream:
            stream.write(f"version={source['version']}\ncommit={source['access']['commit']}\n")


if __name__ == '__main__':
    main()
