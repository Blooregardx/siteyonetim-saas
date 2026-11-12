"""Sequester only recorded libvips install outputs before the second build.

The upstream recipe builds libvips once. Leaving its installed libvips.a in
TARGET makes a second find/--exclude-libs hide the core C API. Preserve those
outputs outside TARGET; never delete or optimize dependency packages.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import os


def sequester(prefix,log,backup):
    if prefix.is_symlink() or not prefix.is_dir() or prefix.resolve()==Path('/') or backup.exists():
        raise ValueError('PREFIX_OR_BACKUP')
    if backup.resolve().is_relative_to(prefix.resolve()):raise ValueError('BACKUP_MUST_LEAVE_PREFIX')
    names=[]
    allowed={'lib/libvips.a','lib/libvips-cpp.so.8.18.7','lib/libvips-cpp.so',
             'lib/pkgconfig/vips.pc','lib/pkgconfig/vips-cpp.pc','include/vips'}
    for line in log.read_text().splitlines():
        if line.startswith('#') or not line:continue
        p=PurePosixPath(line)
        if not line.startswith('/target/') or '..' in p.parts:
            raise ValueError('INSTALL_PATH_OUTSIDE_TARGET')
        name='/'.join(p.parts[2:])
        if name not in allowed and not name.startswith('include/vips/'):
            raise ValueError('NOT_A_LIBVIPS_INSTALL_OUTPUT')
        if name in names:raise ValueError('DUPLICATE_INSTALL_PATH')
        names.append(name)
    if not {'lib/libvips.a','lib/libvips-cpp.so.8.18.7'}<=set(names):
        raise ValueError('INCOMPLETE_VIPS_INSTALL_LOG')
    records=[]
    for name in names:
        p=prefix/name
        if any(a.is_symlink() for a in p.parents if a!=prefix and a.is_relative_to(prefix)):
            raise ValueError('INSTALL_SYMLINK_ANCESTOR')
        if p.is_symlink():
            if name!='lib/libvips-cpp.so' or os.readlink(p)!='libvips-cpp.so.8.18.7':raise ValueError('INSTALL_ALIAS')
            records.append({'file':name,'kind':'symlink','target':os.readlink(p)})
        elif p.is_file():
            with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
            records.append({'file':name,'kind':'regular','sha256':h})
        elif p.is_dir() and name=='include/vips':
            if any(str(f.relative_to(prefix)) not in names for f in p.rglob('*') if f.is_file() or f.is_symlink()):
                raise ValueError('UNRECORDED_VIPS_HEADER')
        else:raise ValueError('MISSING_INSTALL_OUTPUT')
    backup.mkdir(parents=True)
    for r in records:
        out=backup/r['file'];out.parent.mkdir(parents=True,exist_ok=True)
        (prefix/r['file']).rename(out)
    header_dir=prefix/'include/vips'
    if header_dir.is_dir():header_dir.rmdir()
    result={'scope':'Only libvips outputs sequestered; unchanged native dependencies retained',
            'files':records,'legalApproval':False}
    (backup/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path);p.add_argument('install_log',type=Path);p.add_argument('backup',type=Path)
    a=p.parse_args();print(json.dumps(sequester(a.prefix,a.install_log,a.backup)))
