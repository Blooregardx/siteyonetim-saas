import copy
import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from distribution_gate import evaluate

ID = 'sha256:' + 'a' * 64
SBOM = {'source': {'type': 'image', 'metadata': {'imageID': ID}}, 'artifacts': [{'id': '1', 'name': 'fixture', 'version': '1', 'licenses': [{'spdxExpression': 'MIT'}]}]}
PROOF = {'1': dict(name='fixture', version='1', imageID=ID, decision='PASS', upstream='https://example.invalid/fixture/1', binarySourceMatch='synthetic verified match', noticeEvidence='synthetic LICENSE hash', sourceProvision='not applicable: permissive fixture', relinking='not applicable: permissive fixture', reviewer='synthetic test')}


class GateTests(unittest.TestCase):
    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sbom = root / 'sbom.json'
            proof = root / 'proof.json'
            sbom.write_text(json.dumps(SBOM))
            command = [sys.executable, str(Path(__file__).with_name('distribution_gate.py')), '--sbom', str(sbom), '--image-id', ID, '--evidence', str(proof)]
            for value, expected in [(PROOF, 0), ({}, 1), ('malformed', 2)]:
                proof.write_text(json.dumps(value) if isinstance(value, dict) else value)
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected)
                self.assertNotIn('Traceback', result.stderr)

    def test_complete(self):
        self.assertEqual(evaluate(SBOM, ID, PROOF)['readiness'], 'PASS')

    def test_missing_fields(self):
        for key in PROOF['1']:
            p = copy.deepcopy(PROOF)
            del p['1'][key]
            self.assertEqual(evaluate(SBOM, ID, p)['readiness'], 'BLOCKED', key)

    def test_missing_component_version(self):
        s = copy.deepcopy(SBOM)
        p = copy.deepcopy(PROOF)
        del s['artifacts'][0]['version']
        del p['1']['version']
        self.assertEqual(evaluate(s, ID, p)['readiness'], 'BLOCKED')

    def test_wrong_version(self):
        p = copy.deepcopy(PROOF)
        p['1']['version'] = '2'
        self.assertEqual(evaluate(SBOM, ID, p)['readiness'], 'BLOCKED')

    def test_unknown(self):
        for license_value in [[], [{'spdxExpression': 'NOASSERTION'}], [{'spdxExpression': 'LicenseRef-custom'}]]:
            s = copy.deepcopy(SBOM)
            s['artifacts'][0]['licenses'] = license_value
            self.assertEqual(evaluate(s, ID, PROOF)['counts']['UNKNOWN'], 1)

    def test_identity_and_empty(self):
        for s in [{}, {'source': {'type': 'directory'}}, {**SBOM, 'artifacts': []}]:
            with self.assertRaises(ValueError):
                evaluate(s, ID, PROOF)
        with self.assertRaises(ValueError):
            evaluate(SBOM, 'sha256:' + 'b' * 64, PROOF)


if __name__ == '__main__':
    unittest.main()
