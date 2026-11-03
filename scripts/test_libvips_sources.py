import copy
import json
from pathlib import Path
import unittest
from verify_libvips_sources import verify
from distribution_gate import evaluate
from research_libvips_sources import inspect_archive
import tarfile
import tempfile
import io

ROOT=Path(__file__).resolve().parents[1]/'docs/evidence/s05b'
M=json.loads((ROOT/'libvips-source-manifest.json').read_text())


class SourceTests(unittest.TestCase):
    def test_valid_structural_evidence_is_partial(self):
        self.assertEqual(verify(M,ROOT)['sourceEvidence'],'PARTIAL')

    def test_wrong_commit(self):
        for name in ['package','libvips','sharp']:
            m=copy.deepcopy(M);m[name]['commit']='0'*40
            with self.assertRaises(ValueError):verify(m,ROOT)

    def test_bad_checksum(self):
        m=copy.deepcopy(M);m['buildFiles']['upstream/versions.properties']='x'
        with self.assertRaises(ValueError):verify(m,ROOT)

    def test_wrong_build_manifest(self):
        m=copy.deepcopy(M);m['dependencies'][0]['version']='0'
        with self.assertRaises(ValueError):verify(m,ROOT)

    def test_cached_archive_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'sharp.tar').write_bytes(b'wrong source')
            with self.assertRaises(ValueError):verify(M,ROOT,cache=root)

    def test_missing_source(self):
        m=copy.deepcopy(M);m['dependencies'].pop()
        with self.assertRaises(ValueError):verify(m,ROOT)

    def test_missing_license(self):
        m=copy.deepcopy(M);m['dependencies'][0]['notices']=[]
        self.assertTrue(any('NOTICE_MISSING' in e for e in verify(m,ROOT)['errors']))

    def test_missing_relinking(self):
        self.assertEqual(verify(M,ROOT)['relinkingEvidence'],'BLOCKED')

    def test_image_identity(self):
        with self.assertRaises(ValueError):verify(M,ROOT,{'imageID':'bad'},'sha256:'+'a'*64)

    def test_empty_or_bad_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.tar'
            p.write_bytes(b'')
            with self.assertRaises(tarfile.TarError):inspect_archive(p)
            with tarfile.open(p,'w'):pass
            with self.assertRaises(ValueError):inspect_archive(p)

    def test_unsafe_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.tar'
            with tarfile.open(p,'w') as t:
                item=tarfile.TarInfo('../escape');item.size=1;t.addfile(item,io.BytesIO(b'x'))
            with self.assertRaises(ValueError):inspect_archive(p)

    def test_text_proof_cannot_clear_native(self):
        image='sha256:'+'a'*64
        sbom={'source':{'type':'image','metadata':{'imageID':image}},'artifacts':[{'id':'x','name':'sharp','version':'0.35.5','licenses':[{'spdxExpression':'Apache-2.0'}]}]}
        proof={'x':dict.fromkeys(['upstream','binarySourceMatch','noticeEvidence','sourceProvision','relinking','reviewer'],'filled but unverified')}
        proof['x'].update(name='sharp',version='0.35.5',imageID=image,decision='PASS')
        self.assertEqual(evaluate(sbom,image,proof)['readiness'],'BLOCKED')

    def test_wrong_platform_and_binary_hash(self):
        image_id='sha256:'+'a'*64
        image={'imageID':image_id,'sharpVersion':'0.35.5','binaries':[{'platform':'darwin-arm64'}]}
        with self.assertRaises(ValueError):verify(M,ROOT,image,image_id)
        image['binaries']=[{'platform':p,'package':'@img/sharp-libvips-'+p,'packageVersion':'1.3.4','elf':{'magic':'7f454c46','class':2,'machine':62},'sha256':'invalid','versions':{'vips':'8.18.7'}} for p in ['linux-x64','linuxmusl-x64']]
        with self.assertRaises(ValueError):verify(M,ROOT,image,image_id)
        for b in image['binaries']:b['sha256']='a'*64
        m=copy.deepcopy(M);m['images']=[{'platform':b['platform'],'imageID':image_id,'sha256':'b'*64} for b in image['binaries']]
        result=verify(m,ROOT,image,image_id)
        self.assertTrue(any('UNREVIEWED_BINARY_BINDING' in e for e in result['errors']))

    def test_no_global_clearance(self):
        m=copy.deepcopy(M);m['maintainerReview']['approved']=True;m['gaps']=[]
        self.assertEqual(verify(m,ROOT)['binaryDistributionReadiness'],'BLOCKED')


if __name__=='__main__':unittest.main()
