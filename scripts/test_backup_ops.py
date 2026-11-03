#!/usr/bin/env python3
"""Failure matrix: real age and bounded streams, no database or real credentials."""
import contextlib
import datetime as dt
import json
import multiprocessing
import time
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import backup_ops as ops
import safe_upgrade


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='siteyonetim-s04c-unit-')
        self.base = Path(self.temp.name)
        self.root = self.base / 'backups'
        ops.initialize(self.root)
        self.key = self.base / 'identity.agekey'
        ops.run(['age-keygen','-o',str(self.key)])
        self.key.chmod(0o600)
        self.recipients = self.base / 'recipients'
        self.recipients.write_text(ops.run(['age-keygen','-y',str(self.key)])+'\n')
        self.recipients.chmod(0o600)
        self.c = {'source':{'container_id':'a'*64,'database':'siteyonetim_test','system_identifier':'1'}, 'backup_directory':str(self.root),'recipients_file':str(self.recipients),'retention_days':7,'revision':'b'*40}
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(patch.object(ops,'bound',side_effect=lambda b:b))
        self.stack.enter_context(patch.object(ops,'metadata',return_value={'migrations':[], 'catalog_sha256':'f'*64}))
        self.stack.enter_context(patch.object(ops,'backup_role_safe',return_value=True))
        self.stack.enter_context(patch.object(ops,'sql',return_value='1'))
        self.actual_pipeline = ops.pipeline

    def produce(self, code):
        def stream(_producer, consumer, output=None, drain=False):
            return self.actual_pipeline([sys.executable,'-c',code],consumer,output,drain)
        return patch.object(ops,'pipeline',side_effect=stream)

    def complete(self):
        with self.produce("import sys;sys.stdout.buffer.write(b'synthetic-only')"):
            with ops.locked(self.root):
                return ops.backup(self.c)

    def test_encrypted_publication_large_stream(self):
        with self.produce("import sys;chunk=bytes(range(256))*256\nfor _ in range(512):sys.stdout.buffer.write(chunk)"):
            name = ops.backup(self.c)
        directory,m = ops.entry(self.root,name)
        self.assertEqual(len(m['sha256']),64)
        self.assertEqual((directory/'database.age').stat().st_mode & 0o077,0)
        self.assertFalse(list(self.root.glob('.partial-*')))
        output = subprocess.Popen(['age','-d','-i',str(self.key),str(directory/'database.age')],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        size = 0
        while block := output.stdout.read(65536):
            size += len(block)
        output.stdout.close()
        self.assertEqual(output.wait(),0)
        self.assertEqual(size,32*1024*1024)

    def test_overlapping_operation_is_refused(self):
        with ops.locked(self.root):
            with self.assertRaises(ops.Refused):
                with ops.locked(self.root):
                    self.fail('second lock succeeded')

    def test_producer_failure_does_not_publish(self):
        with self.produce("import sys;sys.stdout.buffer.write(b'partial');sys.exit(9)"):
            with self.assertRaises(ops.Refused):
                ops.backup(self.c)
        self.assertEqual(ops.status(self.root)['valid_copies'],0)
        self.assertFalse(list(self.root.glob('.partial-*')))

    def test_encryption_failure_does_not_publish(self):
        self.recipients.write_text('invalid-recipient\n')
        with self.produce("import sys;sys.stdout.buffer.write(b'partial')"):
            with self.assertRaises(ops.Refused):
                ops.backup(self.c)
        self.assertEqual(ops.status(self.root)['valid_copies'],0)

    def test_low_disk_and_real_write_limit_failure(self):
        with patch.object(ops.shutil,'disk_usage',return_value=type('Disk',(),{'free':0})()):
            with self.assertRaises(ops.Refused):
                ops.backup(self.c)
        popen = subprocess.Popen
        def limited(args,**kwargs):
            if args[0]=='age':
                kwargs['preexec_fn']=lambda:resource.setrlimit(resource.RLIMIT_FSIZE,(1024,1024))
            return popen(args,**kwargs)
        with self.produce("import sys;sys.stdout.buffer.write(b'x'*1048576)"),patch.object(subprocess,'Popen',side_effect=limited):
            with self.assertRaises(ops.Refused):
                ops.backup(self.c)
        self.assertEqual(ops.status(self.root)['valid_copies'],0)

    def test_filesystem_write_error(self):
        with self.produce("import sys;sys.stdout.buffer.write(b'test')"),patch.object(ops.os,'fsync',side_effect=OSError(28,'simulated disk full')):
            with self.assertRaises(OSError):
                ops.backup(self.c)
        self.assertEqual(ops.status(self.root)['valid_copies'],0)

    def test_interruption_terminates_pipeline(self):
        def worker():
            signal.signal(signal.SIGTERM,ops.interrupted)
            try:
                with self.produce("import time;time.sleep(30)"):
                    ops.backup(self.c)
            except KeyboardInterrupt:
                sys.exit(130)
        process=multiprocessing.get_context('fork').Process(target=worker)
        process.start()
        for _ in range(50):
            if list(self.root.glob('.partial-*')):
                break
            time.sleep(.02)
        time.sleep(.2)
        process.terminate()
        process.join(10)
        self.assertFalse(process.is_alive())
        self.assertEqual(process.exitcode,130)
        self.assertEqual(ops.status(self.root)['valid_copies'],0)
        self.assertFalse(list(self.root.glob('.partial-*')))

    def dated(self, name, days):
        old = self.root/name
        date = (dt.datetime.now(ops.UTC)-dt.timedelta(days=days)).strftime(ops.STAMP)
        new = self.root/f'backup-{date}-{name[-32:]}'
        old.rename(new)
        m = ops.read_json(new/'manifest.json')
        (new/'manifest.json').unlink()
        m['created']=date
        ops.write_json(new/'manifest.json',m)
        return new

    def test_retention_dry_run_and_last_verified_copy(self):
        old = self.dated(self.complete(),20)
        _,m = ops.entry(self.root,old.name)
        ops.write_json(old/'verified.json',{'sha256':m['sha256']})
        middle = self.dated(self.complete(),10)
        latest = self.dated(self.complete(),1)
        result = ops.prune(self.c,self.root)
        self.assertEqual(result['eligible_count'],1)
        self.assertTrue(middle.exists())
        ops.prune(self.c,self.root,False)
        self.assertTrue(old.exists())
        self.assertTrue(latest.exists())
        self.assertFalse(middle.exists())

    def test_last_completed_copy_is_never_deleted(self):
        only = self.dated(self.complete(),30)
        self.assertEqual(ops.prune(self.c,self.root,False)['eligible_count'],0)
        self.assertTrue(only.exists())

    def test_corrupt_backup_not_counted_or_pruned(self):
        directory = self.dated(self.complete(),30)
        (directory/'database.age').write_bytes(b'corrupt')
        self.assertEqual(ops.status(self.root)['valid_copies'],0)
        self.assertEqual(ops.prune(self.c,self.root,False)['eligible_count'],0)
        self.assertTrue(directory.exists())

    def test_symlink_hardlink_wrong_directory_and_traversal_refused(self):
        name = self.complete()
        outside = self.base/'outside'
        outside.mkdir(mode=0o700)
        (outside/'keep').write_text('untouched')
        with self.assertRaises((ops.Refused,OSError)):
            with ops.locked(outside):
                pass
        (self.base/'alias').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ops.Refused):
            with ops.locked(self.base/'alias'):
                pass
        with self.assertRaises(ops.Refused):
            ops.entry(self.root,'../outside')
        directory = self.root/name
        (directory/'database.age').unlink()
        (directory/'database.age').symlink_to(outside/'keep')
        ops.prune(self.c,self.root,False)
        self.assertEqual((outside/'keep').read_text(),'untouched')
        with self.assertRaises(ops.Refused):
            ops.entry(self.root,name)
        (directory/'database.age').unlink()
        os.link(outside/'keep',directory/'database.age')
        with self.assertRaises(ops.Refused):
            ops.entry(self.root,name)

    def test_safe_upgrade_stage_order_and_failure_stops_writers(self):
        class Driver:
            def __init__(self): self.events=[]
            def stop(self): self.events.append('stop')
            def build(self): self.events.append('build')
            def migrate(self): self.events.append('migrate');raise ops.Refused('injected migration failure')
            def schema(self): self.events.append('schema')
            def start(self): self.events.append('start')
        d=Driver()
        with self.assertRaisesRegex(ops.Refused,'FAILED_WRITERS_STOPPED; stage=migrate'):
            safe_upgrade.sequence(d,lambda:d.events.append('backup') or 'copy',lambda n:d.events.append('verify'),lambda n:d.events.append('restore'))
        self.assertEqual(d.events,['stop','backup','verify','restore','build','migrate','stop'])
        d=Driver()
        with self.assertRaisesRegex(ops.Refused,'stage=verify-backup'):
            safe_upgrade.sequence(d,lambda:'copy',lambda n:ops.require(False),lambda n:None)
        self.assertEqual(d.events,['stop','stop'])


if __name__ == '__main__':
    unittest.main()
