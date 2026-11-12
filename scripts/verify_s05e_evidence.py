"""Validate honest S05-E experiment outcomes; no automatic legal clearance."""
import argparse
import json
from pathlib import Path

from s05e_source_protocol import physical
from s05e_native_recipe import LOCK_SHA


def verify_outcome(record,root):
    if record.get('schemaVersion')!=1 or record.get('status') not in {'BLOCKED','PARTIAL'}:
        raise ValueError('UNREVIEWED_FULL_COMPLIANCE_CLAIM')
    if record.get('binaryDistributionReadiness')!='BLOCKED':
        raise ValueError('GENERAL_DISTRIBUTION_MUST_REMAIN_BLOCKED')
    if record.get('executed'):
        if record.get('recipeCommit')!='ebb95f8add54eee8bed840e3fb587e4cbec857d7' or record.get('sourceLockSha256')!=LOCK_SHA:
            raise ValueError('RECIPE_OR_LOCK')
        if record.get('target')!='x86_64-unknown-linux-gnu' or record.get('profile')!='CONTROLLED_FULL_NATIVE_WITH_S05D_LOCK':
            raise ValueError('WRONG_TARGET_OR_REDUCED_PROFILE')
    if type(record.get('executed')) is not bool:
        raise ValueError('EXECUTION_STATE')
    if not record['executed']:
        if any(record.get(k) is not None for k in ['controlSha256','modifiedSha256','abiComparison']) or record.get('sharpTests')!='NOT_RUN':
            raise ValueError('FABRICATED_UNEXECUTED_RESULTS')
        if not record.get('blockerEvidence'):
            raise ValueError('PHYSICAL_BLOCKER_REQUIRED')
        for f in record['blockerEvidence']:
            if not physical(root,f['file'],f['sha256']).stat().st_size:raise ValueError('EMPTY_BLOCKER')
    else:
        for phase in ['control','modified']:
            h=record.get(phase+'Sha256')
            if h:
                # A textual SHA cannot replace the actual generated file.
                f=physical(root,record['binaryFiles'][phase],h)
                if f.read_bytes()[:6]!=b'\x7fELF\x02\x01':raise ValueError('ELF_REQUIRED')
        if record.get('status')=='PARTIAL':
            if record.get('exitCode')!=0 or not record.get('controlSha256') or not record.get('modifiedSha256'):
                raise ValueError('BUILD_SUCCESS_WITHOUT_BINARY')
            if record['controlSha256']==record['modifiedSha256']:
                raise ValueError('SAME_BYTE_IS_NOT_MODIFIED_REBUILD')
            change=record.get('sourceChange') or {}
            before=physical(root,change['beforeFile'],change['beforeSha256'])
            after=physical(root,change['afterFile'],change['afterSha256'])
            if before.read_bytes()==after.read_bytes():raise ValueError('UNCHANGED_SOURCE')
            for f in record.get('staticInputs',[]):physical(root,f['file'],f['sha256'])
            if not record.get('staticInputs'):raise ValueError('STATIC_INPUTS_MISSING')
    return {'recordIntegrity':'PASS','fullRebuild':record['status'],
            'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--record',type=Path,required=True)
    a=p.parse_args()
    try:
        print(json.dumps(verify_outcome(json.loads(a.record.read_text()),a.root)))
        raise SystemExit(1)  # Valid BLOCKED/PARTIAL evidence is not distribution approval.
    except (OSError,ValueError,KeyError,TypeError):
        print('{"recordIntegrity":"BLOCKED","binaryDistributionReadiness":"BLOCKED"}')
        raise SystemExit(2)
