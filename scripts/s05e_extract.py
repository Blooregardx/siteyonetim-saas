"""Bounded source extraction; links are created last and stay inside the source.

Input integrity is checked before the archive is opened. Never extracts devices
or trusts archive permissions/owners. Destination must be empty.
"""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import posixpath
import shutil
import tarfile

def extract(archive, expected, dest):
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size>512*1024**2:
        raise ValueError('SOURCE_ARCHIVE_SIZE_OR_PATH')
    h=hashlib.sha256()
    with archive.open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    if h.hexdigest() != expected:
        raise ValueError('SOURCE_HASH')
    if dest.is_symlink() or dest.exists() and any(dest.iterdir()):
        raise ValueError('SOURCE_DESTINATION_NOT_EMPTY')
    dest.mkdir(parents=True,exist_ok=True)
    links=[];names=set();total=0;top=None
    with tarfile.open(archive) as t:
        for i,e in enumerate(t):
            if i>=100000:raise ValueError('SOURCE_ENTRY_LIMIT')
            p=PurePosixPath(e.name)
            if p.is_absolute() or '..' in p.parts or not p.parts:
                raise ValueError('SOURCE_PATH')
            if top is None:top=p.parts[0]
            if p.parts[0]!=top:
                raise ValueError('MULTIPLE_SOURCE_ROOTS')
            relative='/'.join(p.parts[1:])
            if not relative:
                if not e.isdir():raise ValueError('SOURCE_ROOT_NOT_DIRECTORY')
                continue
            if relative in names:raise ValueError('SOURCE_DUPLICATE')
            names.add(relative)
            out=dest/relative
            total+=e.size
            if e.size<0 or e.size>128*1024**2 or total>512*1024**2:
                raise ValueError('SOURCE_SIZE')
            if e.issym() or e.islnk():
                target=posixpath.normpath(posixpath.join(str(p.parent),e.linkname) if e.issym() else e.linkname)
                if PurePosixPath(e.linkname).is_absolute() or target.split('/')[0]!=top or '..' in PurePosixPath(target).parts:
                    raise ValueError('SOURCE_LINK_ESCAPE')
                links.append((out,e,target))
            elif e.isdir():out.mkdir(parents=True,exist_ok=True)
            elif e.isfile():
                out.parent.mkdir(parents=True,exist_ok=True)
                with t.extractfile(e) as source,out.open('xb') as output:shutil.copyfileobj(source,output)
                out.chmod(0o755 if e.mode&0o111 else 0o644)
                if not 0<=e.mtime<=2147483647:raise ValueError('SOURCE_MTIME_RANGE')
                os.utime(out,(e.mtime,e.mtime),follow_symlinks=False)
            else:raise ValueError('SOURCE_SPECIAL_FILE')
        # Prevent links becoming ancestors of regular files or other links.
        for out,e,target in links:
            if out.exists() or any(out in f.parents for f in dest.rglob('*')):
                raise ValueError('SOURCE_LINK_ANCESTOR')
            out.parent.mkdir(parents=True,exist_ok=True)
            if e.issym():out.symlink_to(e.linkname)
            else:
                src=dest/'/'.join(PurePosixPath(target).parts[1:])
                if src.is_symlink() or not src.is_file():raise ValueError('SOURCE_HARDLINK_TARGET')
                shutil.copyfile(src,out)
        for out,_,_ in links:
            if not out.resolve().is_relative_to(dest.resolve()):raise ValueError('SOURCE_LINK_CHAIN_ESCAPE')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path);p.add_argument('sha256');p.add_argument('destination',type=Path)
    a=p.parse_args();extract(a.archive,a.sha256,a.destination)
