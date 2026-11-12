"""Synthetic evidence tests are not an executed native rebuild or legal approval."""
import copy
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import verify_s05d_evidence as v


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        def file(name, data):
            p=self.root/name; p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            return {'file':name,'sha256':v.digest(data)}
        self.file=file
        self.sbom=file('sbom.json',json.dumps({'source':{'metadata':{'imageID':'sha256:'+'a'*64}}}).encode())
        with tarfile.open(self.root/'source.tar','w') as t:
            e=tarfile.TarInfo('source/code.c');data=b'int fixture;';e.size=len(data);t.addfile(e,io.BytesIO(data))
        source={'file':'source.tar','sha256':v.digest((self.root/'source.tar').read_bytes())}
        notice=file('LICENSE',b'MIT synthetic copyright fixture\nPermission is hereby granted '+b'x'*200)
        notice['license']='MIT'
        self.m={'schemaVersion':1,'imageConfigDigest':'sha256:'+'a'*64,'sbomFile':'sbom.json',
                'sbomSha256':self.sbom['sha256'],'sources':[source],'notices':[notice],
                'buildScripts':[file('build.txt',b'synthetic build command')],
                'staticInputs':[file('object.a',b'synthetic inventory fixture only')],
                'retentionMethod':'reviewed independent copies','durabilityClaim':'not guaranteed'}
        self.r={'schemaVersion':1,'recipeCommit':v.RECIPE,'target':v.TARGET,'inputLockSha256':v.LOCK_SHA,
                'status':'BLOCKED','generatedLockSha256':None,'generatedLockFile':None}
    def tearDown(self):self.tmp.cleanup()
    def test_valid_blocked_is_not_pass(self):
        self.assertEqual(v.verify_resolution(self.r,self.root)['generatedLock'],'BLOCKED')
    def test_wrong_lock(self):
        self.r['inputLockSha256']='0'*64
        with self.assertRaises(ValueError):v.verify_resolution(self.r,self.root)
    def test_wrong_target(self):
        self.r['target']='x86_64-unknown-linux-musl'
        with self.assertRaises(ValueError):v.verify_resolution(self.r,self.root)
    def test_fabricated_generated_lock(self):
        self.r['generatedLockSha256']='a'*64
        with self.assertRaises(ValueError):v.verify_resolution(self.r,self.root)
    def test_unverified_toolchain(self):
        self.r.update(status='PARTIAL',historicalUpstreamLock=False,toolchain={'verified':False})
        with self.assertRaises(ValueError):v.verify_resolution(self.r,self.root)
    def test_resolved_is_not_compiled_or_linked(self):
        scope={'schemaVersion':1,'target':v.TARGET,'records':[{'status':'UNKNOWN'}],
               'counts':{s:int(s=='UNKNOWN') for s in ['RESOLVED','COMPILED','LINKED — EVIDENCED','NOT SELECTED — EVIDENCED','UNKNOWN']}}
        self.assertEqual(v.verify_scope(scope)['scope'],'BLOCKED')
        for state in ['COMPILED','LINKED — EVIDENCED','NOT SELECTED — EVIDENCED']:
            bad=copy.deepcopy(scope);bad['records'][0]['status']=state;bad['counts']={s:int(s==state) for s in bad['counts']}
            with self.assertRaises(ValueError):v.verify_scope(bad)
    def test_source_package_inventory_is_not_legal_pass(self):
        r=v.verify_source_package(self.m,self.root)
        self.assertFalse(r['legalApproval']);self.assertEqual(r['binaryDistributionReadiness'],'BLOCKED')
    def test_foreign_image(self):
        self.m['imageConfigDigest']='sha256:'+'b'*64
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_missing_source(self):
        (self.root/'source.tar').unlink()
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_wrong_checksum(self):
        self.m['sources'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_missing_notice(self):
        self.m['notices']=[]
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_missing_command(self):
        self.m['buildScripts']=[]
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_missing_static_inputs(self):
        self.m['staticInputs']=[]
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_actions_retention_not_durable(self):
        self.m['retentionMethod']='github-actions-artifact'
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_no_host_guarantee(self):
        self.m['durabilityClaim']='guaranteed'
        with self.assertRaises(ValueError):v.verify_source_package(self.m,self.root)
    def test_traversal_and_links(self):
        for name,typ in [('../LICENSE',tarfile.REGTYPE),('link',tarfile.SYMTYPE)]:
            with tarfile.open(self.root/'bad.tar','w') as t:
                e=tarfile.TarInfo(name);e.type=typ;e.linkname='/etc/passwd';t.addfile(e)
            with self.assertRaises(ValueError):v.safe_members(self.root/'bad.tar')
    def test_empty_archive(self):
        with tarfile.open(self.root/'empty.tar','w'):pass
        with self.assertRaises(ValueError):v.safe_members(self.root/'empty.tar')
    def test_source_lock_diff(self):
        a='[[package]]\nname="fixture"\nversion="1"\nchecksum="a"\n'
        b='[[package]]\nname="fixture"\nversion="1"\nchecksum="b"\n'
        self.assertEqual(len(v.lock_changes(a,b)['checksumChanges']),1)
    def test_full_blocked_and_filled_text_not_success(self):
        r={'status':'BLOCKED','executed':False,'controlSha256':None,'modifiedSha256':None,'blockers':['missing native toolchain']}
        self.assertEqual(v.verify_full_bundle(r)['fullBundle'],'BLOCKED')
        for field,value in [('status','VERIFIED'),('controlSha256','a'*64),('modifiedSha256','b'*64),('executed',True)]:
            bad={**r,field:value}
            with self.assertRaises(ValueError):v.verify_full_bundle(bad)
    def test_reduced_profile_rejected(self):
        with self.assertRaises(ValueError):v.verify_full_bundle({'profile':'reduced-feature PNG/JPEG'})
    def test_same_byte_is_not_modified_full_build(self):
        with self.assertRaises(ValueError):v.verify_full_bundle({'status':'VERIFIED','controlSha256':'a'*64,'modifiedSha256':'a'*64})
    def test_empty_compiler_text_not_evidence(self):
        self.r.update(status='PARTIAL',historicalUpstreamLock=False,toolchain={'verified':True,'components':[]})
        with self.assertRaises(ValueError):v.verify_resolution(self.r,self.root)
    def test_wrapped_mpl_header_is_original_notice(self):
        header=b'/* This Source Code Form is subject to the terms of the Mozilla Public\n * License, v. 2.0. If a copy of the MPL was not distributed with this\n * file, You can obtain one at https://mozilla.org/MPL/2.0/. */\n'
        source=header+b'pub fn fixture() {}\n'
        with tarfile.open(self.root/'mpl.crate','w') as a:
            e=tarfile.TarInfo('fixture/src/lib.rs');e.size=len(source);a.addfile(e,io.BytesIO(source))
        h=self.file('header.txt',header);h.update(kind='source-header',archiveMember='fixture/src/lib.rs',completeSourceSha256=v.digest(source))
        sha=v.digest((self.root/'mpl.crate').read_bytes())
        r={'name':'fixture','version':'1','archiveFile':'mpl.crate','archiveSha256':sha,'cargoChecksum':sha,
           'decision':'PASS','licenseDeclaration':'MPL-2.0','evidence':[h]}
        with patch.dict(v.TRUSTED_CRATES,{('fixture','1'):sha}):
            self.assertEqual(v.verify_notice(r,self.root)['notice'],'PASS')
            (self.root/'header.txt').write_bytes(b'Mozilla Public License fake mozilla.org/MPL/2.0')
            with self.assertRaises(ValueError):v.verify_notice(r,self.root)
    def test_physical_metadata_feature_binding(self):
        metadata={'packages':[{'id':'fixture@1','name':'fixture','version':'1'}],
                  'resolve':{'nodes':[{'id':'fixture@1','features':['default']}]}}
        proof=self.file('metadata.json',json.dumps(metadata).encode())
        scope={'schemaVersion':1,'target':v.TARGET,'featureMode':'workspace-default','metadataFile':proof['file'],
               'metadataSha256':proof['sha256'],'records':[{'name':'fixture','version':'1','packageId':'fixture@1','features':['default'],'status':'RESOLVED'}],
               'counts':{s:int(s=='RESOLVED') for s in ['RESOLVED','COMPILED','LINKED — EVIDENCED','NOT SELECTED — EVIDENCED','UNKNOWN']}}
        self.assertEqual(v.verify_scope(scope,self.root)['scope'],'PARTIAL')
        scope['records'][0]['features']=['fake']
        with self.assertRaises(ValueError):v.verify_scope(scope,self.root)
    def test_invalid_compiled_archive(self):
        with self.assertRaises(ValueError):v.compiled_shape(b'!<arch>\n')
        self.assertFalse(v.compiled_shape(b'\x7fELF'))
    def test_archive_member_inventory(self):
        payload=b'fixture'
        header=b'fixture.o/'.ljust(16)+b'0'.ljust(12)+b'0'.ljust(6)+b'0'.ljust(6)+b'100644'.ljust(8)+str(len(payload)).encode().ljust(10)+bytes([96,10])
        raw=b'!<arch>\n'+header+payload+b'\n'
        self.assertTrue(v.compiled_shape(raw))
        self.assertEqual(v.archive_members(raw)[0]['sha256'],v.digest(payload))
    def test_fabricated_compiler_record_without_physical_metadata(self):
        s={'schemaVersion':1,'target':v.TARGET,'records':[{'status':'COMPILED','packageId':'made-up','features':[]}],
           'counts':{k:int(k=='COMPILED') for k in ['RESOLVED','COMPILED','LINKED — EVIDENCED','NOT SELECTED — EVIDENCED','UNKNOWN']}}
        with self.assertRaises(ValueError):v.verify_scope(s,self.root)
    def test_recorded_generated_lock_and_scope(self):
        import tomllib
        base=v.ROOT/'docs/evidence/s05d'
        r=json.loads((base/'cargo-resolution.json').read_text())
        data=(base/'generated-Cargo.lock').read_bytes()
        self.assertEqual(v.digest(data),r['generatedLockSha256'])
        before=(v.ROOT/'docs/evidence/s05b/upstream/librsvg-Cargo.lock').read_text()
        for attempt in r['attempts']:
            self.assertEqual(attempt['exitCode'],0)
            self.assertEqual(attempt['afterSha256'],v.digest(data))
            self.assertEqual(attempt['changes'],v.lock_changes(before,data.decode()))
        lock=tomllib.loads(data.decode())['package']
        scope=json.loads((base/'rust-compile-link-scope.json').read_text())
        self.assertEqual({(p['name'],p['version'],p.get('source','path')) for p in lock},
                         {(p['name'],p['version'],p['source']) for p in scope['records']})
        self.assertEqual(sum(scope['counts'].values()),len(lock))
    def test_recorded_notice_and_collector_hashes(self):
        base=v.ROOT/'docs/evidence/s05d'
        manifest=json.loads((base/'rust-license-resolution.json').read_text())
        self.assertEqual(len(manifest['records']),13)
        self.assertEqual(manifest['counts'],{s:sum(r['decision']==s for r in manifest['records']) for s in ['PASS','BLOCKED','UNKNOWN','NOT_APPLICABLE']})
        for r in manifest['records']:
            self.assertEqual(r['cargoChecksum'],v.TRUSTED_CRATES[(r['name'],r['version'])])
            if r['decision']=='PASS':
                self.assertTrue(r['evidence'])
                for e in r['evidence']:v.physical(base,e['file'],e['sha256'])
        receipt=json.loads((base/'experiment-receipt.json').read_text())
        for name,sha in receipt['codeSha256'].items():v.physical(v.ROOT,name,sha)
    def test_fake_notice(self):
        archive=self.m['sources'][0]
        r={'archiveFile':archive['file'],'archiveSha256':archive['sha256'],'cargoChecksum':archive['sha256'],
           'decision':'PASS','licenseDeclaration':'MIT','evidence':[]}
        with self.assertRaises(ValueError):v.verify_notice(r,self.root)
    def test_wrong_crate_checksum(self):
        a=self.m['sources'][0]
        with self.assertRaises(ValueError):v.verify_notice({'archiveFile':a['file'],'archiveSha256':a['sha256'],'cargoChecksum':'0'*64},self.root)
    def test_changed_features_without_metadata_not_resolved(self):
        s={'schemaVersion':1,'target':v.TARGET,'records':[{'status':'RESOLVED','features':['fake']}],
           'counts':{k:int(k=='RESOLVED') for k in ['RESOLVED','COMPILED','LINKED — EVIDENCED','NOT SELECTED — EVIDENCED','UNKNOWN']}}
        with self.assertRaises(ValueError):v.verify_scope(s)
    def test_symlink_physical_input(self):
        (self.root/'alias').symlink_to(self.root/'LICENSE')
        with self.assertRaises(ValueError):v.physical(self.root,'alias',self.m['notices'][0]['sha256'])


if __name__=='__main__':unittest.main()
