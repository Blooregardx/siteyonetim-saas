#!/usr/bin/env python3
"""No daemon mutations: filesystem/port negatives plus explicit daemon metadata stubs."""
import copy
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import selfhost_preflight as pf


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='siteyonetim-s04d-preflight-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ['Dockerfile','compose.selfhost.yaml','prisma/schema.prisma','.env.selfhost.example']:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(pf.ROOT/name,path)
        (self.root/'docker').mkdir()
        for name in ['init.sh','grants.sql']:shutil.copyfile(pf.ROOT/'docker'/name,self.root/'docker'/name)
        for name in range(11):
            path=self.root/f'prisma/migrations/{name:04}/migration.sql';path.parent.mkdir(parents=True);path.write_text('synthetic')
        self.env=self.root/'.env.selfhost';self.env.write_text('POSTGRES_DB=siteyonetim_test\n');self.env.chmod(0o600)
        (self.root/'secrets').mkdir(mode=0o700)
        secrets={}
        for name in ['db_password','migrator_password','runtime_password','smtp_url']:
            path=self.root/'secrets'/name;path.write_text('' if name=='smtp_url' else 'f'*64+'\n');path.chmod(0o640)
            secrets[name]={'file':str(path)}
        with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        self.config={'services':{'db':{'image':'postgres:17-bookworm','environment':{'POSTGRES_DB':'siteyonetim_test'}},'migrate':{'environment':{'POSTGRES_DB':'siteyonetim_test'}},'app':{'environment':{'POSTGRES_DB':'siteyonetim_test','APP_URL':'https://example.invalid','MAIL_FROM':''},'read_only':True,'cap_drop':['ALL'],'security_opt':['no-new-privileges:true'],'ports':[{'host_ip':'127.0.0.1','target':3000,'published':str(port),'protocol':'tcp'}]}},'secrets':secrets}
        self.permissions={}
        actual=pf.file_info
        def metadata(path):
            info=actual(path)
            if path.parent.name=='secrets':
                uid,gid=self.permissions.get(path.name,(1000,999))
                return SimpleNamespace(st_mode=info.st_mode,st_nlink=info.st_nlink,st_uid=uid,st_gid=gid,st_size=info.st_size)
            return info
        self.patches=[patch.object(pf,'file_info',side_effect=metadata),patch.object(pf.shutil,'disk_usage',return_value=SimpleNamespace(free=20*1024**3)),patch.object(pf,'command',side_effect=self.command)]
        for item in self.patches:item.start();self.addCleanup(item.stop)

    def command(self,args):
        if args[-1]=='--format={{.Driver}}':return 0,'overlay2\n'
        if args[-2:]==['version','--short']:return 0,'v2.40.3\n'
        return 0,json.dumps(self.config)

    def inspect(self,**kw):return pf.inspect(self.root,self.env,**kw)
    def fails(self,code):self.assertIn(code,self.inspect()['errors'])

    def test_valid_demo_and_explicit_mail_requirement(self):
        result=self.inspect();self.assertTrue(result['ok']);self.assertIn('SMTP_MISSING_REGISTRATION_UNAVAILABLE',result['warnings'])
        self.assertFalse(self.inspect(require_mail=True)['ok'])

    def test_missing_env(self):self.env.unlink();self.fails('ENV_FILE_MISSING')
    def test_missing_secret(self):(self.root/'secrets/runtime_password').unlink();self.fails('SECRET_FILE_MISSING')
    def test_bad_permissions(self):(self.root/'secrets/runtime_password').chmod(0o644);self.fails('SECRET_PERMISSIONS_INVALID')
    def test_bad_uid_gid(self):self.permissions['runtime_password']=(0,0);self.fails('SECRET_UID_GID_INVALID')
    def test_secret_symlink(self):
        path=self.root/'secrets/runtime_password';path.unlink();path.symlink_to(self.env);self.fails('SECRET_TYPE_INVALID')
    def test_wrong_database(self):self.config['services']['app']['environment']['POSTGRES_DB']='wrong';self.fails('DATABASE_BINDING_INVALID')
    def test_public_db_and_app_ports(self):
        self.config['services']['db']['ports']=[{'published':'5432'}];self.fails('DATABASE_PORT_PUBLISHED')
        self.config['services']['app']['ports'][0]['host_ip']='0.0.0.0';self.fails('APP_PORT_BINDING_INVALID')
    def test_postgres_major(self):self.config['services']['db']['image']='postgres:18';self.fails('POSTGRES_17_REQUIRED')
    def test_invalid_https_origin(self):
        for value in ['http://localhost:3000','https://user:password@example.invalid','https://example.invalid/path','https://example.invalid/#x']:
            self.config['services']['app']['environment']['APP_URL']=value;self.fails('HTTPS_ORIGIN_INVALID')
    def test_busy_port(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0));listener.listen()
            self.config['services']['app']['ports'][0]['published']=str(listener.getsockname()[1]);self.fails('APP_PORT_UNAVAILABLE')
    def test_low_disk_daemon_and_configuration_failure(self):
        with patch.object(pf.shutil,'disk_usage',return_value=SimpleNamespace(free=0)):self.fails('DISK_RESERVE_INSUFFICIENT')
        with patch.object(pf,'command',return_value=(1,'')):self.fails('DOCKER_UNAVAILABLE')
        original=self.command
        with patch.object(pf,'command',side_effect=lambda args:(1,'') if args[-1]=='json' else original(args)):self.fails('COMPOSE_CONFIGURATION_INVALID')


if __name__=='__main__':unittest.main()
