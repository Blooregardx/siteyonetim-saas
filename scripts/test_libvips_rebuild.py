import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
import struct
import zlib
from unittest.mock import patch
import verify_libvips_rebuild as v

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/evidence/s05c'
SCOPE=json.loads((DATA/'rust-build-scope.json').read_text())
SOURCES=json.loads((DATA/'rust-source-manifest.json').read_text())
OBS=json.loads((DATA/'upstream-build-observations.json').read_text())
LOCK=ROOT/'docs/evidence/s05b/upstream/librsvg-Cargo.lock'
SPEC=json.loads((DATA/'toolchain-spec.json').read_text())


class EvidenceTests(unittest.TestCase):
    def test_scope_and_sources(self):
        self.assertEqual(v.verify_scope(SCOPE,LOCK,OBS)['decision'],'PARTIAL')
        self.assertEqual(v.verify_sources(SOURCES,DATA)['decision'],'PARTIAL')

    def test_not_seen_is_not_not_selected(self):
        s=copy.deepcopy(SCOPE);r=next(r for r in s['records'] if r['scopeDecision']=='UNKNOWN');r['scopeDecision']='NOT SELECTED — EVIDENCED';s['counts']={k:sum(r['scopeDecision']==k for r in s['records']) for k in s['counts']}
        with self.assertRaises(ValueError):v.verify_scope(s,LOCK,OBS)

    def test_wrong_lock(self):
        s=copy.deepcopy(SCOPE);s['lockSha256']='0'*64
        with self.assertRaises(ValueError):v.verify_scope(s,LOCK,OBS)

    def test_unknown_crate(self):
        s=copy.deepcopy(SCOPE);s['records'][0]['name']='unlisted'
        with self.assertRaises(ValueError):v.verify_scope(s,LOCK,OBS)

    def test_toolchain_compile_lines_excluded(self):
        s=copy.deepcopy(SCOPE);r=next(r for r in s['records'] if r['scopeDecision']=='COMPILED — EVIDENCED');r['evidenceLines']=['#7 92.1 Compiling '+r['name']+' v'+r['version']]
        with self.assertRaises(ValueError):v.verify_scope(s,LOCK,OBS)

    def test_registry_checksum(self):
        s=copy.deepcopy(SOURCES);r=next(r for r in s['records'] if r['decision']=='PASS');r['archiveSha256']='0'*64
        with self.assertRaises(ValueError):v.verify_sources(s,DATA)

    def test_missing_license(self):
        s=copy.deepcopy(SOURCES);r=next(r for r in s['records'] if r['decision']=='PASS');r['notices']=[]
        with self.assertRaises(ValueError):v.verify_sources(s,DATA)

    def test_git_and_path_need_identity(self):
        for kind in ['git','path']:
            s=copy.deepcopy(SOURCES);r=next(r for r in s['records'] if r['decision']=='PASS');r['sourceKind']=kind
            with self.assertRaises(ValueError):v.verify_sources(s,DATA)

    def test_actual_crate_bytes_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):v.verify_sources(SOURCES,DATA,Path(tmp))
    def test_source_record_omission(self):
        s=copy.deepcopy(SOURCES);s['records'].pop()
        with self.assertRaises(ValueError):v.verify_sources(s,DATA)
    def test_notice_checksum_tamper(self):
        s=copy.deepcopy(SOURCES);r=next(r for r in s['records'] if r['decision']=='PASS');r['notices'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):v.verify_sources(s,DATA)
    def test_empty_and_traversal_source_archive(self):
        from research_rust_sources import inspect_rust_archive
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.tar'
            with tarfile.open(p,'w'):pass
            with self.assertRaises(ValueError):inspect_rust_archive(p)
            with tarfile.open(p,'w') as t:
                item=tarfile.TarInfo('../LICENSE');item.size=1;t.addfile(item,io.BytesIO(b'x'))
            with self.assertRaises(ValueError):inspect_rust_archive(p)
    def test_source_counts_and_origin_cannot_be_filled_in(self):
        s=copy.deepcopy(SOURCES);s['counts']['PASS']=357
        with self.assertRaises(ValueError):v.verify_sources(s,DATA)
        o=copy.deepcopy(OBS);o['commit']='0'*40
        with self.assertRaises(ValueError):v.verify_scope(SCOPE,LOCK,o)
    def test_text_only_rebuild_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ValueError,KeyError,OSError)):v.verify_rebuild({'status':'PARTIAL','sourceCommit':v.COMMIT,'baseImage':SPEC['baseImage'],'target':SPEC['target']},Path(tmp),SPEC)

    def test_wrong_commit_base_target_tools(self):
        r={'sourceCommit':v.COMMIT,'baseImage':SPEC['baseImage'],'target':SPEC['target'],'status':'BLOCKED'}
        for name in ['sourceCommit','baseImage','target']:
            bad=copy.deepcopy(r);bad[name]='wrong'
            with self.assertRaises(ValueError):v.verify_rebuild(bad,ROOT,SPEC)
        bad=copy.deepcopy(SPEC);bad['expectedTools']['gcc']='0'
        with self.assertRaises(ValueError):v.verify_rebuild(r,ROOT,bad)


@unittest.skipUnless(shutil.which('cc') and shutil.which('readelf') and shutil.which('nm'),'ELF fixture tools unavailable')
class BinaryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        for p in ['input','out/control','out/modified','work/control/libvips/iofuncs','work/modified/libvips/iofuncs']:(self.root/p).mkdir(parents=True)
        before=b'int fixture(void){return 7;}\n';after=before+b'__attribute__((used)) static const char marker[]="S05C_TEST_MARKER";\n'
        for kind,data in [('control',before),('modified',after)]:
            path=self.root/('work/'+kind+'/libvips/iofuncs/init.c');path.write_bytes(data)
            subprocess.run(['cc','-shared','-fPIC','-Wl,-soname,libvips-cpp.so.8.18.7',str(path),'-o',str(self.root/('out/'+kind+'/libvips.so'))],check=True,capture_output=True)
        (self.root/'out/source-change.patch').write_text('synthetic source diff')
        with tarfile.open(self.root/'input/vips.tar','w') as t:
            item=tarfile.TarInfo('fixture/libvips/iofuncs/init.c');item.size=len(before);t.addfile(item,io.BytesIO(before))
        shutil.copyfile(self.root/'out/control/libvips.so',self.root/'out/distributed-libvips.so')
        # Real PNG signature/IHDR dimensions are checked; this unit fixture is not a Sharp execution claim.
        def chunk(kind,data):return len(data).to_bytes(4,'big')+kind+data+(zlib.crc32(kind+data)&0xffffffff).to_bytes(4,'big')
        (self.root/'out/result.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\x12\x34\x56'))+chunk(b'IEND',b''))
        (self.root/'out/sharp-maps.txt').write_text('7000-8000 r-xp 00000000 00:00 42 out/modified/libvips.so\n8000-9000 r-xp 00000000 00:00 43 /app/node_modules/@img/sharp-linux-x64/lib/fixture.node\n')
        self.image='sha256:'+'a'*64;sbom={'source':{'metadata':{'imageID':self.image}}};(self.root/'out/environment-sbom.syft.json').write_text(json.dumps(sbom));(self.root/'environment-config-id.txt').write_text(self.image)
        self.spec=copy.deepcopy(SPEC);self.spec['source']['sha256']=v.sha(self.root/'input/vips.tar');self.spec['distributedBinarySha256']=v.sha(self.root/'out/distributed-libvips.so')
        self.anchor=patch.object(v,'SOURCE_SHA',self.spec['source']['sha256']);self.anchor.start()
        (self.root/'out/sharp-addon.node').write_bytes(b'synthetic-addon-fixture-only')
        self.r={'packages':{'sharp':'0.35.5','@img/sharp-libvips-linux-x64':'1.3.4','@img/sharp-linux-x64':'0.35.5'},'nativeAddon':{'path':'/app/node_modules/@img/sharp-linux-x64/lib/fixture.node','sha256':v.sha(self.root/'out/sharp-addon.node')},'sourceCommit':v.COMMIT,'baseImage':self.spec['baseImage'],'target':self.spec['target'],'status':'PARTIAL','profile':self.spec['profile'],'fullUpstreamRecipe':False,'buildFlags':{k:{'meson':v.FLAGS.copy()} for k in ['control','modified']},'toolchain':self.spec['expectedTools'],'imageID':self.image,'sbomSha256':v.sha(self.root/'out/environment-sbom.syft.json'),'sourceModification':{'file':'libvips/iofuncs/init.c','beforeSha256':hashlib.sha256(before).hexdigest(),'afterSha256':hashlib.sha256(after).hexdigest(),'patchSha256':v.sha(self.root/'out/source-change.patch'),'marker':'S05C_TEST_MARKER'},'binaries':{k:{'path':'out/'+k+'/libvips.so','sha256':v.sha(self.root/('out/'+k+'/libvips.so')),'soname':'libvips-cpp.so.8.18.7'} for k in ['control','modified']},'abi':{'controlVsModifiedEqual':True,'missingFromModified':[],'missingComparedWithDistributed':[]},'distributedBinarySha256':self.spec['distributedBinarySha256'],'sharp':{'exitCode':0,'newLoaded':True,'oldLoaded':False,'png':True,'width':1,'height':1,'loadedSha256':v.sha(self.root/'out/modified/libvips.so')}}

    def tearDown(self):self.anchor.stop();self.tmp.cleanup()
    def test_physical_files_allow_partial_only(self):
        r=v.verify_rebuild(self.r,self.root,self.spec);self.assertEqual(r['modifiedRebuild'],'PARTIAL');self.assertEqual(r['staticInputs'],'BLOCKED');self.assertEqual(r['binaryDistributionReadiness'],'BLOCKED')
    def test_old_library_false_success(self):
        self.r['sharp']['oldLoaded']=True
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_same_byte_is_not_rebuild(self):
        self.r['binaries']['modified']=self.r['binaries']['control']
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_wrong_features(self):
        self.r['buildFlags']['modified']['meson']=[]
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_invalid_png_file(self):
        (self.root/'out/result.png').write_bytes(b'fake')
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_missing_source_archive(self):
        (self.root/'input/vips.tar').unlink()
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_wrong_binary_sha(self):
        self.r['binaries']['modified']['sha256']='0'*64
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_abi_mismatch(self):
        self.r['abi']['controlVsModifiedEqual']=False
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_source_change_hash(self):
        self.r['sourceModification']['afterSha256']='0'*64
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_foreign_sbom(self):
        self.r['imageID']='sha256:'+'b'*64
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_actual_elf_abi_mismatch(self):
        src=self.root/'work/extra.c';src.write_bytes((self.root/'work/modified/libvips/iofuncs/init.c').read_bytes()+b'int additional_export(void){return 1;}\n')
        binary=self.root/'out/modified/libvips.so'
        subprocess.run(['cc','-shared','-fPIC','-Wl,-soname,libvips-cpp.so.8.18.7',str(src),'-o',str(binary)],check=True,capture_output=True)
        self.r['binaries']['modified']['sha256']=v.sha(binary)
        self.r['sharp']['loadedSha256']=v.sha(binary)
        with self.assertRaisesRegex(ValueError,'ACTUAL_ABI'):v.verify_rebuild(self.r,self.root,self.spec)
    def test_actual_wrong_elf_platform(self):
        binary=self.root/'out/modified/libvips.so';data=bytearray(binary.read_bytes());data[18:20]=(183).to_bytes(2,'little');binary.write_bytes(data)
        self.r['binaries']['modified']['sha256']=v.sha(binary)
        with self.assertRaisesRegex(ValueError,'ELF_PLATFORM'):v.verify_rebuild(self.r,self.root,self.spec)
    def test_reported_runtime_toolchain_mismatch(self):
        self.r['toolchain']={**self.r['toolchain'],'gcc':'99'}
        with self.assertRaisesRegex(ValueError,'TOOLCHAIN'):v.verify_rebuild(self.r,self.root,self.spec)
    def test_raw_maps_required(self):
        (self.root/'out/sharp-maps.txt').write_text('old binary only')
        with self.assertRaises(ValueError):v.verify_rebuild(self.r,self.root,self.spec)
    def test_static_text_does_not_clear(self):
        self.r['staticInputs']={'originalFullBundleAvailable':True,'review':'all fields filled'}
        self.assertEqual(v.verify_rebuild(self.r,self.root,self.spec)['staticInputs'],'BLOCKED')


if __name__=='__main__':unittest.main()
