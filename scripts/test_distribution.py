#!/usr/bin/env python3
"""Source archive policy: tiny synthetic Git trees, no application build."""
import io
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
import verify_distribution as distribution


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='siteyonetim-s04d-archive-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'repo';self.root.mkdir()
        for name in distribution.REQUIRED|{str(p.relative_to(distribution.ROOT)) for p in (distribution.ROOT/'prisma/migrations').glob('*/migration.sql')}:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(distribution.ROOT/name,target)
        self.git('init','-q');self.commit()
    def git(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.DEVNULL).decode().strip()
    def commit(self):
        self.git('add','-A');self.git('-c','user.name=Synthetic','-c','user.email=archive@example.invalid','-c','commit.gpgsign=false','commit','-qm','Synthetic fixture');self.revision=self.git('rev-parse','HEAD')
    def archive(self):
        out=Path(self.temp.name)/'source.tar.gz';self.git('archive','--format=tar.gz','--prefix=source-fixture/','--output='+str(out),'HEAD');return out
    def test_complete_source_without_ignored_env(self):
        (self.root/'.env').write_text('synthetic untracked, never archived')
        self.assertTrue(distribution.verify(self.root,self.revision,self.archive())['source_archive_verified'])
    def test_tracked_real_env_filename_rejected(self):
        (self.root/'.env').write_text('synthetic forbidden filename');self.git('add','-f','.env');self.commit()
        with self.assertRaises(ValueError):distribution.verify(self.root,self.revision,self.archive())
    def test_key_pattern_across_stream_boundary_rejected(self):
        (self.root/'note.txt').write_text('x'*65530+'AGE-SECRET-KEY-'+'A'*60);self.commit()
        with self.assertRaises(ValueError):distribution.verify(self.root,self.revision,self.archive())
    def test_missing_required_file_and_changed_archive(self):
        archive=self.archive();changed=Path(self.temp.name)/'changed.tar.gz'
        with tarfile.open(archive,'r:gz') as before,tarfile.open(changed,'w:gz') as after:
            for member in before:
                if member.isfile():
                    data=before.extractfile(member).read()
                    if member.name.endswith('/README.md'):data+=b'changed'
                    member.size=len(data);after.addfile(member,io.BytesIO(data))
                else:after.addfile(member)
        with self.assertRaises(ValueError):distribution.verify(self.root,self.revision,changed)
        (self.root/'Dockerfile').unlink();self.commit()
        with self.assertRaises(ValueError):distribution.verify(self.root,self.revision,self.archive())


if __name__=='__main__':unittest.main()
