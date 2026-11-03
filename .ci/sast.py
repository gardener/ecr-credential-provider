#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path


def first_party_directories(packages):
    decoder = json.JSONDecoder()
    directories = set()
    remaining = packages.strip()
    # `go list -json` emits consecutive JSON objects, not a JSON array.
    while remaining:
        package, end = decoder.raw_decode(remaining)
        remaining = remaining[end:].lstrip()
        if package.get('Module', {}).get('Path') == 'k8s.io/cloud-provider-aws':
            directories.add(package['Dir'])
    if not directories:
        raise ValueError('No first-party packages found for the credential provider')
    return sorted(directories)


def merge_reports(reports):
    combined = {'version': '2.1.0', 'runs': []}
    for architecture, report in reports:
        if report.get('version') != combined['version'] or not report.get('runs'):
            raise ValueError('Scanner did not produce a SARIF 2.1.0 run')
        for run in report['runs']:
            run.setdefault('properties', {})['architecture'] = architecture
            combined['runs'].append(run)
    return combined


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    reports = []
    with tempfile.TemporaryDirectory() as directory:
        for architecture in ('amd64', 'arm64'):
            env = {**os.environ, 'GOOS': 'linux', 'GOARCH': architecture, 'CGO_ENABLED': '0'}
            packages = subprocess.run(
                ['go', 'list', '-deps', '-json', './cmd/ecr-credential-provider'],
                cwd=args.source, check=True, capture_output=True, text=True, env=env,
            ).stdout
            report = Path(directory) / f'{architecture}.sarif'
            subprocess.run(
                ['gosec', '-fmt=sarif', '-out=' + str(report),
                 *first_party_directories(packages)],
                cwd=args.source, check=True, env=env,
            )
            reports.append((architecture, json.loads(report.read_text())))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(merge_reports(reports), indent=2) + '\n')


if __name__ == '__main__':
    main()
