# SPDX-License-Identifier: AGPL-3.0-only
"""Offline source-distribution checks. Does not test remote URLs or deploy."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

root = Path(__file__).resolve().parent.parent
package = json.loads((root / 'package.json').read_text())
lock = json.loads((root / 'package-lock.json').read_text())
assert package['license'] == lock['packages']['']['license'] == 'AGPL-3.0-only'
assert package['version'] == lock['version'] == lock['packages']['']['version']
assert hashlib.sha256((root / 'LICENSE').read_bytes()).hexdigest() == '0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0', 'Official complete AGPL text changed'
for name in ['COPYRIGHT', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'SECURITY.md', 'docs/THIRD-PARTY-LICENSES.md', 'docs/DEPENDENCY-LICENSES.csv']:
    assert (root / name).is_file(), name
packages = [value for path, value in lock['packages'].items() if path]
assert all(value.get('license') for value in packages), 'Missing dependency license metadata'
files = subprocess.check_output(['git', 'ls-files', '-z', '--', '*.md'], cwd=root).decode().split('\0')
links = 0
for name in filter(None, files):
    path = root / name
    for destination in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', path.read_text()):
        if re.match(r'^[a-zA-Z][\w+.-]*:|^#', destination):
            continue
        target = unquote(destination.split('#')[0])
        assert (path.parent / target).exists(), f'{name}: missing local target {target}'
        links += 1
for name in ['scripts/test_backup_stream.py', 'scripts/verify-backup-restore.py', 'tests/security-matrix.integration.ts', 'tests/e2e/security-session.spec.ts', 'prisma/migrations/202611040001_financial_immutability/migration.sql']:
    assert 'SPDX-License-Identifier: AGPL-3.0-only' in (root / name).read_text(), name
print(json.dumps({'verified': True, 'markdownFiles': len(list(filter(None, files))), 'localFileLinks': links, 'dependencyLicenseRecords': len(packages), 'license': package['license']}))
