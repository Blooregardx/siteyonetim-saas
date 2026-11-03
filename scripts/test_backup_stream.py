# SPDX-License-Identifier: AGPL-3.0-only
"""Small deterministic stream regressions; no database or Docker mutation."""
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import unittest

os.environ.setdefault("OSS_TEST_SOURCE_CONTAINER", "unused-source")
os.environ.setdefault("OSS_TEST_RESTORE_CONTAINER", "unused-target")
spec = importlib.util.spec_from_file_location("drill", Path(__file__).with_name("verify-backup-restore.py"))
drill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drill)


class BoundedReader(io.BytesIO):
    def read(self, size=-1):
        if size != 64 * 1024:
            raise AssertionError("Unbounded read")
        return super().read(size)


class StreamTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(drill.digest_stream(BoundedReader()), (hashlib.sha256(b"").hexdigest(), 0))

    def test_chunk_boundaries_unicode_and_copy_escapes(self):
        payload = (b"x" * 65535 + b"\n" + '{"name":"Türkçe €","text":"a\\nb"}\n'.encode()) * 5
        digest, count = drill.digest_stream(BoundedReader(payload))
        self.assertEqual(digest, hashlib.sha256(payload).hexdigest())
        self.assertEqual(count, 10)

    def test_binary_dump_hash(self):
        payload = bytes(range(256)) * 1000
        self.assertEqual(drill.digest_stream(BoundedReader(payload))[0], hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    unittest.main()
