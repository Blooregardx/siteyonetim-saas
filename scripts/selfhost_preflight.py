#!/usr/bin/env python3
"""Read-only Linux/Compose installation checks. Never print configuration values."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCKER = ['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock']


def command(args):
    try:
        result=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
        return result.returncode,result.stdout.decode()
    except (OSError,subprocess.TimeoutExpired,UnicodeError):
        return 1,''


def file_info(path):
    return path.lstat()


def inspect(root,env_file,min_free_gib=10,require_mail=False):
    errors=[]
    warnings=[]
    def check(ok,code):
        if not ok:errors.append(code)
        return ok
    check(os.name=='posix' and os.uname().sysname=='Linux','LINUX_REQUIRED')
    required=['Dockerfile','compose.selfhost.yaml','prisma/schema.prisma','.env.selfhost.example','docker/init.sh','docker/grants.sql']
    check(all((root/p).is_file() for p in required),'SOURCE_FILES_MISSING')
    migrations=list((root/'prisma/migrations').glob('*/migration.sql'))
    check(len(migrations)==11,'MIGRATION_SOURCE_COUNT')
    try:
        info=file_info(env_file)
        check(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and not info.st_mode & 0o077,'ENV_FILE_PERMISSIONS')
    except OSError:
        errors.append('ENV_FILE_MISSING')
    code,driver=command(DOCKER+['info','--format={{.Driver}}'])
    check(code==0,'DOCKER_UNAVAILABLE')
    if driver.strip()=='vfs':warnings.append('VFS_DISK_MULTIPLICATION')
    code,version=command(DOCKER+['compose','version','--short'])
    check(code==0 and re.match(r'^v?[2-9][0-9]*\.',version.strip()),'COMPOSE_V2_REQUIRED')
    try:check(shutil.disk_usage(root).free>=min_free_gib*1024**3,'DISK_RESERVE_INSUFFICIENT')
    except OSError:errors.append('DISK_CHECK_FAILED')
    code,data_root=command(DOCKER+['info','--format={{.DockerRootDir}}'])
    try:
        if code!=0 or not Path(data_root.strip()).is_absolute():raise OSError
        check(shutil.disk_usage(data_root.strip()).free>=min_free_gib*1024**3,'DOCKER_DISK_RESERVE_INSUFFICIENT')
    except OSError:warnings.append('DOCKER_DATA_DISK_NOT_CHECKED')
    if errors:return {'ok':False,'errors':errors,'warnings':warnings}
    code,raw=command(DOCKER+['compose','--env-file',str(env_file),'-f',str(root/'compose.selfhost.yaml'),'--profile','tools','config','--format','json'])
    if not check(code==0,'COMPOSE_CONFIGURATION_INVALID'):
        return {'ok':False,'errors':errors,'warnings':warnings}
    try:
        config=json.loads(raw)
        db=config['services']['db'];app=config['services']['app'];migrate=config['services']['migrate']
        check(re.fullmatch(r'(?:docker.io/library/)?postgres:17(?:-[a-z0-9.-]+)?(?:@sha256:[a-f0-9]{64})?',db.get('image','')),'POSTGRES_17_REQUIRED')
        names=[service.get('environment',{}).get('POSTGRES_DB','') for service in [db,app,migrate]]
        check(len(set(names))==1 and re.fullmatch(r'[a-z][a-z0-9_]{0,62}',names[0]),'DATABASE_BINDING_INVALID')
        check(not db.get('ports'),'DATABASE_PORT_PUBLISHED')
        check(app.get('read_only') is True and 'ALL' in app.get('cap_drop',[]) and any('no-new-privileges' in v for v in app.get('security_opt',[])),'APP_SECURITY_OPTIONS_INVALID')
        check(app.get('user','node') in ['node','1000','1000:1000'],'APP_USER_INVALID')
        origin=app.get('environment',{}).get('APP_URL','')
        try:
            parsed=urlsplit(origin)
            check(parsed.scheme=='https' and bool(parsed.hostname) and not parsed.username and not parsed.password and parsed.path in ['', '/'] and not parsed.query and not parsed.fragment and not any(c.isspace() for c in origin) and (parsed.port is None or 1<=parsed.port<=65535),'HTTPS_ORIGIN_INVALID')
        except ValueError:errors.append('HTTPS_ORIGIN_INVALID')
        sender=app.get('environment',{}).get('MAIL_FROM','')
        if not sender.strip():(errors if require_mail else warnings).append('MAIL_FROM_MISSING')
        check(not any(c in sender for c in '\r\n'),'MAIL_FROM_INVALID')
        # No network request or SMTP credential parsing: metadata only, never echo secrets.
        secret_root=root/'secrets'
        for name in ['db_password','migrator_password','runtime_password','smtp_url']:
            declared=Path(config['secrets'][name]['file'])
            path=secret_root/name
            check(declared==path,'SECRET_PATH_INVALID')
            try:
                info=file_info(path)
                check(not secret_root.is_symlink() and stat.S_ISREG(info.st_mode) and info.st_nlink==1,'SECRET_TYPE_INVALID')
                check(info.st_uid==1000 and info.st_gid==999,'SECRET_UID_GID_INVALID')
                check(stat.S_IMODE(info.st_mode) in ([0o600,0o640] if name=='smtp_url' else [0o640]),'SECRET_PERMISSIONS_INVALID')
                if name=='smtp_url':
                    if info.st_size==0:
                        (errors if require_mail else warnings).append('SMTP_MISSING_REGISTRATION_UNAVAILABLE')
                    else:warnings.append('SMTP_DELIVERY_NOT_VERIFIED')
                else:check(info.st_size in [64,65],'SECRET_SIZE_INVALID')
            except OSError:errors.append('SECRET_FILE_MISSING')
        ports=app.get('ports',[])
        if check(len(ports)==1,'APP_PORT_INVALID'):
            port=ports[0]
            if check(port.get('host_ip')=='127.0.0.1' and int(port.get('target',0))==3000 and port.get('protocol')=='tcp','APP_PORT_BINDING_INVALID'):
                try:
                    number=int(port['published'])
                    check(1<=number<=65535,'APP_PORT_INVALID')
                    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:probe.bind(('127.0.0.1',number))
                except (OSError,ValueError):errors.append('APP_PORT_UNAVAILABLE')
    except (KeyError,TypeError,ValueError,json.JSONDecodeError):errors.append('COMPOSE_STRUCTURE_INVALID')
    warnings.append('TLS_CERTIFICATE_AND_REAL_SMTP_NOT_TESTED')
    return {'ok':not errors,'errors':sorted(set(errors)),'warnings':sorted(set(warnings))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--env-file',type=Path,default=Path('.env.selfhost'))
    parser.add_argument('--min-free-gib',type=int,default=10)
    parser.add_argument('--require-mail',action='store_true')
    args=parser.parse_args()
    if args.min_free_gib<1:parser.error('min-free-gib must be positive')
    root=args.root.resolve()
    result=inspect(root,args.env_file if args.env_file.is_absolute() else root/args.env_file,args.min_free_gib,args.require_mail)
    print(json.dumps(result))
    return 0 if result['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
