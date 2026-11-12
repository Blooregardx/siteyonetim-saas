"""Synthetic integrity and recovery adversarial tests, never compliance approval."""
import copy
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import s05e_source_protocol as p


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name)
        self.root = self.parent/'source'
        self.index = p.fixture(self.root)

    def mutate(self, edit):
        m = json.loads((self.root/'source-index.json').read_text())
        edit(m)
        raw = json.dumps(m).encode()
        (self.root/'source-index.json').write_bytes(raw)
        return p.sha(raw)

    def rejected(self, edit):
        h = self.mutate(edit)
        with self.assertRaises((ValueError, KeyError, OSError)):
            p.verify(self.root, h)

    def bundle(self):
        dest = self.parent/'bundle.tar'
        with tarfile.open(dest, 'w') as t:
            for f in sorted(self.root.rglob('*')):
                if f.is_file():
                    t.add(f, arcname=str(f.relative_to(self.root)), recursive=False)
        return dest

    def test_valid_integrity_still_blocked(self):
        r = p.verify(self.root, self.index)
        self.assertEqual(r['protocolIntegrity'], 'PASS')
        self.assertEqual(r['binaryDistributionReadiness'], 'BLOCKED')
        self.assertFalse(r['legalApproval'])
        self.assertEqual(r['durableSourceProvision'], 'PARTIAL')

    def test_source_index_needs_external_trust_anchor(self):
        with self.assertRaises(ValueError):
            p.verify(self.root, '0'*64)

    def test_manifest_mismatch(self):
        self.rejected(lambda m: m.update(imageManifestDigest='sha256:'+'0'*64))

    def test_config_mismatch(self):
        self.rejected(lambda m: m.update(imageConfigDigest='sha256:'+'0'*64))

    def test_wrong_binary(self):
        self.rejected(lambda m: m.update(binarySha256='0'*64))

    def test_missing_binary(self):
        self.rejected(lambda m: m.update(binaryPath='usr/lib/missing.so'))

    def test_missing_role(self):
        self.rejected(lambda m: m['inventory'].pop())

    def test_duplicate_input(self):
        self.rejected(lambda m: m['inventory'].append(m['inventory'][0]))

    def test_empty_notice(self):
        def edit(m):
            r = next(r for r in m['inventory'] if r['role']=='notice')
            (self.root/r['file']).write_bytes(b'')
            r['sha256'] = p.sha(b'')
        self.rejected(edit)

    def test_metadata_is_not_legal_approval(self):
        self.rejected(lambda m: m.update(legalApproval=True))

    def test_guaranteed_storage_claim_rejected(self):
        self.rejected(lambda m: m.update(durabilityGuarantee=True))

    def test_fake_archive(self):
        def edit(m):
            r = next(r for r in m['inventory'] if r['role']=='static-archive')
            (self.root/r['file']).write_bytes(b'PASS archive')
            r['sha256'] = p.sha(b'PASS archive')
        self.rejected(edit)

    def test_fake_object(self):
        def edit(m):
            r = next(r for r in m['inventory'] if r['role']=='object')
            (self.root/r['file']).write_bytes(b'PASS object')
            r['sha256'] = p.sha(b'PASS object')
        self.rejected(edit)

    def test_foreign_sbom(self):
        def edit(m):
            raw = json.dumps({'source':{'type':'image','metadata':{'imageID':'sha256:'+'0'*64}}}).encode()
            (self.root/'sbom.json').write_bytes(raw)
            m['sbom']['sha256'] = p.sha(raw)
        self.rejected(edit)

    def test_lockfile_inventory_is_not_image_sbom(self):
        def edit(m):
            raw = json.dumps({'source':{'type':'directory','metadata':{'imageID':m['imageConfigDigest']}}}).encode()
            (self.root/'sbom.json').write_bytes(raw)
            m['sbom']['sha256'] = p.sha(raw)
        self.rejected(edit)

    def test_synthetic_empty_sbom_cannot_be_promoted_to_real_candidate(self):
        h=self.mutate(lambda m:m.update(purpose='PREPUBLICATION_CANDIDATE'))
        with self.assertRaisesRegex(ValueError,'EMPTY_IMAGE_SBOM'):
            p.verify(self.root,h)

    def test_tampered_physical_blob(self):
        f = next((self.root/'oci/blobs/sha256').iterdir())
        f.write_bytes(b'tampered')
        with self.assertRaises(ValueError):
            p.verify(self.root,self.index)

    def test_restore_each_of_two_copies(self):
        source = self.bundle()
        for n in range(2):
            copy_path = self.parent/('copy-'+str(n)+'.tar')
            copy_path.write_bytes(source.read_bytes())
            r = p.restore(copy_path,p.file_sha(source),self.index,self.parent/('restored-'+str(n)))
            self.assertEqual(r['protocolIntegrity'],'PASS')
        # These are two unit-test copies on one host, not independent storage.

    def test_restore_corruption(self):
        bundle = self.bundle();h = p.file_sha(bundle)
        bundle.write_bytes(bundle.read_bytes()+b'corruption')
        with self.assertRaises(ValueError):
            p.restore(bundle,h,self.index,self.parent/'restore')

    def test_restore_missing_copy(self):
        with self.assertRaises(ValueError):
            p.restore(self.parent/'missing', '0'*64, self.index,self.parent/'restore')

    def test_restore_wrong_index(self):
        bundle=self.bundle()
        with self.assertRaises(ValueError):
            p.restore(bundle,p.file_sha(bundle),'0'*64,self.parent/'restore')

    def test_restore_existing_destination(self):
        bundle=self.bundle()
        with self.assertRaises(ValueError):
            p.restore(bundle,p.file_sha(bundle),self.index,self.root)

    def bad_tar(self, entries):
        f = self.parent/'bad.tar'
        with tarfile.open(f,'w') as t:
            for e,raw in entries:
                t.addfile(e,io.BytesIO(raw) if e.isfile() else None)
        with self.assertRaises(ValueError):
            p.regular_tar(f)

    def test_traversal(self):
        e=tarfile.TarInfo('../escape');e.size=1
        self.bad_tar([(e,b'x')])

    def test_symlink(self):
        e=tarfile.TarInfo('alias');e.type=tarfile.SYMTYPE;e.linkname='/etc/passwd'
        self.bad_tar([(e,b'')])

    def test_hardlink(self):
        e=tarfile.TarInfo('alias');e.type=tarfile.LNKTYPE;e.linkname='file'
        self.bad_tar([(e,b'')])

    def test_duplicate_tar_member(self):
        e=tarfile.TarInfo('file');e.size=1
        self.bad_tar([(e,b'x'),(e,b'y')])

    def test_special_file(self):
        e=tarfile.TarInfo('dev');e.type=tarfile.CHRTYPE
        self.bad_tar([(e,b'')])

    def test_size_limit(self):
        f=self.bundle()
        with self.assertRaises(ValueError):
            p.regular_tar(f, maximum=1)

    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            p.strict_json(b'{"legalApproval":false,"legalApproval":true}')

    def test_symlink_parent_input(self):
        (self.root/'alias').symlink_to('inputs',target_is_directory=True)
        self.rejected(lambda m: m['inventory'][0].update(file='alias/'+Path(m['inventory'][0]['file']).name))


if __name__ == '__main__':
    unittest.main()
