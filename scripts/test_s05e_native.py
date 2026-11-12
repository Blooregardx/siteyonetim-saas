"""Native prerequisite, source safety, original notice and honest outcome tests."""
import copy
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from s05e_extract import extract
from s05e_native_recipe import render
from s05e_source_protocol import sha, file_sha
from s05e_rust_notices import verify_authors
from verify_s05e_evidence import verify_outcome
from s05e_native_recipe import LOCK_SHA

ROOT=Path(__file__).resolve().parents[1]


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'failure.txt').write_text('Observed prerequisite failure; not executed')
        self.blocked={'schemaVersion':1,'status':'BLOCKED','executed':False,'controlSha256':None,'modifiedSha256':None,
                      'abiComparison':None,'sharpTests':'NOT_RUN','binaryDistributionReadiness':'BLOCKED',
                      'blockerEvidence':[{'file':'failure.txt','sha256':file_sha(self.root/'failure.txt')}]}
        self.blocked.update(recipeCommit='ebb95f8add54eee8bed840e3fb587e4cbec857d7',sourceLockSha256=LOCK_SHA,
                            target='x86_64-unknown-linux-gnu',profile='CONTROLLED_FULL_NATIVE_WITH_S05D_LOCK')

    def test_valid_blocked_record_is_not_clearance(self):
        self.assertEqual(verify_outcome(self.blocked,self.root)['binaryDistributionReadiness'],'BLOCKED')

    def test_invented_unexecuted_binary(self):
        self.blocked['controlSha256']='0'*64
        with self.assertRaises(ValueError):verify_outcome(self.blocked,self.root)

    def test_invented_unexecuted_abi(self):
        self.blocked['abiComparison']='PASS'
        with self.assertRaises(ValueError):verify_outcome(self.blocked,self.root)

    def test_missing_physical_failure(self):
        (self.root/'failure.txt').unlink()
        with self.assertRaises(ValueError):verify_outcome(self.blocked,self.root)

    def test_filled_strings_cannot_grant_clearance(self):
        self.blocked.update(status='PASS',binaryDistributionReadiness='PASS')
        with self.assertRaises(ValueError):verify_outcome(self.blocked,self.root)

    def test_build_claim_without_files(self):
        self.blocked.update(executed=True,status='PARTIAL',exitCode=0)
        with self.assertRaises(ValueError):verify_outcome(self.blocked,self.root)

    def test_wrong_lock_rejected(self):
        self.blocked.update(executed=True,sourceLockSha256='0'*64)
        with self.assertRaisesRegex(ValueError,'RECIPE_OR_LOCK'):verify_outcome(self.blocked,self.root)

    def test_wrong_commit_rejected(self):
        self.blocked.update(executed=True,recipeCommit='0'*40)
        with self.assertRaisesRegex(ValueError,'RECIPE_OR_LOCK'):verify_outcome(self.blocked,self.root)

    def test_wrong_target_rejected(self):
        self.blocked.update(executed=True,target='x86_64-unknown-linux-musl')
        with self.assertRaisesRegex(ValueError,'WRONG_TARGET'):verify_outcome(self.blocked,self.root)

    def test_reduced_build_cannot_become_full(self):
        self.blocked.update(executed=True,profile='S05C_REDUCED_PNG_JPEG')
        with self.assertRaisesRegex(ValueError,'REDUCED_PROFILE'):verify_outcome(self.blocked,self.root)

    def test_s05e_text_cannot_open_distribution_gate(self):
        from distribution_gate import evaluate
        image='sha256:'+'1'*64
        artifact={'id':'s','name':'sharp','version':'0.35.5','licenses':[{'spdxExpression':'Apache-2.0'}]}
        proof={k:'filled' for k in ['upstream','binarySourceMatch','noticeEvidence','sourceProvision','relinking','reviewer']}
        proof.update(name='sharp',version='0.35.5',imageID=image,decision='PASS',s05eEvidence='PASS')
        r=evaluate({'source':{'type':'image','metadata':{'imageID':image}},'artifacts':[artifact]},image,{'s':proof})
        self.assertEqual(r['readiness'],'BLOCKED')

    def test_same_bytes_not_modified(self):
        raw=b'\x7fELF\x02\x01'+b'\0'*64
        (self.root/'library').write_bytes(raw)
        self.blocked.update(executed=True,status='PARTIAL',exitCode=0,controlSha256=sha(raw),modifiedSha256=sha(raw),binaryFiles={'control':'library','modified':'library'})
        with self.assertRaises(ValueError):verify_outcome(self.blocked,self.root)

    def test_recipe_offline_preserves_full_native_sources(self):
        text=render()
        self.assertNotIn('$CURL',text)
        self.assertNotIn('sh.rustup.rs',text)
        self.assertNotIn('rm -rf lib\n',text)
        self.assertIn('sources/rsvg.tar',text)
        self.assertIn('sources/pango.tar',text)
        self.assertIn('sources/glib.tar',text)
        self.assertIn('generated-Cargo.lock',text)
        self.assertIn('Copyright 2017 Lovell Fuller',text)
        self.assertEqual(text.count('python3.12 /config/s05e_extract.py'),28)

    def archive(self,entries):
        p=self.root/'source.tar'
        with tarfile.open(p,'w') as t:
            for name,kind,payload in entries:
                e=tarfile.TarInfo(name)
                if kind=='file':e.size=len(payload);t.addfile(e,io.BytesIO(payload))
                elif kind=='link':e.type=tarfile.SYMTYPE;e.linkname=payload;t.addfile(e)
                elif kind=='hardlink':e.type=tarfile.LNKTYPE;e.linkname=payload;t.addfile(e)
                else:e.type=tarfile.FIFOTYPE;t.addfile(e)
        return p

    def test_source_hash_before_extraction(self):
        p=self.archive([('pkg/file','file',b'good')])
        with self.assertRaises(ValueError):extract(p,'0'*64,self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_safe_internal_source_link(self):
        p=self.archive([('pkg/file','file',b'good'),('pkg/link','link','file')])
        extract(p,file_sha(p),self.root/'out')
        self.assertEqual((self.root/'out/link').read_bytes(),b'good')
        self.assertEqual((self.root/'out/file').stat().st_mtime,0)

    def test_source_link_escape(self):
        p=self.archive([('pkg/file','file',b'good'),('pkg/link','link','../../outside')])
        with self.assertRaises(ValueError):extract(p,file_sha(p),self.root/'out')

    def test_link_ancestor_attack(self):
        p=self.archive([('pkg/d/file','file',b'good'),('pkg/d','link','other')])
        with self.assertRaises(ValueError):extract(p,file_sha(p),self.root/'out')

    def test_archive_source_traversal(self):
        p=self.archive([('pkg/../outside','file',b'bad')])
        with self.assertRaises(ValueError):extract(p,file_sha(p),self.root/'out')

    def test_archive_duplicate_source(self):
        p=self.archive([('pkg/file','file',b'a'),('pkg/file','file',b'b')])
        with self.assertRaises(ValueError):extract(p,file_sha(p),self.root/'out')

    def test_archive_source_device(self):
        p=self.archive([('pkg/device','device',b'')])
        with self.assertRaises(ValueError):extract(p,file_sha(p),self.root/'out')

    def test_nonempty_source_destination(self):
        p=self.archive([('pkg/file','file',b'good')])
        with self.assertRaises(ValueError):extract(p,file_sha(p),self.root)

    def test_authors_rule_is_exact_not_generic_exception(self):
        with self.assertRaises(ValueError):verify_authors({'name':'block','version':'0.1.6'},self.root,self.root)

    def test_wrong_crate_checksum_rejected(self):
        r=json.loads((ROOT/'docs/evidence/s05e/rust-notice-resolution.json').read_text())['records']
        r=copy.deepcopy(next(x for x in r if x['name']=='r-efi'))
        r['cargoChecksum']='0'*64
        with self.assertRaises(ValueError):verify_authors(r,self.root,self.root)

    def test_wrong_original_notice_rejected(self):
        r=json.loads((ROOT/'docs/evidence/s05e/rust-notice-resolution.json').read_text())['records']
        r=copy.deepcopy(next(x for x in r if x['name']=='r-efi'))
        r['notice']['sha256']='0'*64
        with self.assertRaises(ValueError):verify_authors(r,self.root,self.root)

    def test_notice_counts_remain_scoped(self):
        r=json.loads((ROOT/'docs/evidence/s05e/rust-notice-resolution.json').read_text())
        self.assertEqual(len(r['records']),9)
        self.assertEqual(r['counts'],{'PASS':2,'BLOCKED':7,'UNKNOWN':0,'NOT_APPLICABLE':0})
        self.assertFalse(r['legalApproval'])


if __name__=='__main__':unittest.main()
