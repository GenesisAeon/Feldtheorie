# ADAPTED copy of Astra's reproduce_lr6_review.py: only (1) the code-identity pin, (2) null_meta in _persist_cell, (3) sys.path to the worktree changed.
"""LR6 review probes: synthetic/development data only; never execute research.

--repo is the private review-package checkout. --out must not yet exist.
No production files are changed. Only the original Git-history check of the
registry loader is omitted, via its documented repo=None parameter.
Freeze records are synthetic fixtures outside the project, not approvals.
"""
import argparse
from pathlib import Path
import json
import shutil
import sys
from unittest.mock import patch

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(repo))  # ADAPTED (3): --repo is the Lantern worktree itself
    from experiments.lantern_reconstruction import runs, runner, contexts, observation, training, metrics, decoders, artifacts, streams
    from experiments.lantern_reconstruction import registry_adapter as ra
    assert runs.code_identity()['identity'] == '670d9352e7fb6f7291318cbd36f0b2df2a17cdbd1cd84acf1e404cf16681ea2c', 'ADAPTED: repaired code b0da0c7'
    original_loader = ra.load_verified_snapshot
    snap = original_loader(repo=None)
    original_freeze = runs.FREEZE_FILE
    assert not original_freeze.exists(), 'This probe must not run in a frozen checkout'
    cand = json.loads(runs.CANDIDATE_FILE.read_text())
    result = {'package_commit': '0091f9650b581ae948f24112a81ed28308c24348',
              'lantern_commit': '29af52f03b1f8ffd68c168e58578034abc5ea529',
              'runtime': runs.software(), 'candidate_software': cand['software'],
              'registry_canonical_sha256': snap.canonical_sha256,
              'adaptation': 'registry repo=None omits original Git-history checks only; synthetic freeze paths redirected to output',
              'cases': {}}
    case = result['cases']

    # R1: authoritative candidate bytes, simulated approval record in scratch;
    # only manifest creation/check_resumable. No execute, no research contexts.
    candpath = out / 'fixture_candidate.json'
    candpath.write_bytes(runs.CANDIDATE_FILE.read_bytes())
    freezepath = out / 'fixture_freeze.json'
    fr = {'schema': runs.FREEZE_SCHEMA, 'status': 'frozen',
          'approved_by': ['SYNTHETIC UNIT TEST FIXTURE -- NO APPROVAL'],
          'candidate_sha256': artifacts.sha256(candpath.read_bytes().replace(b'\r\n', b'\n')),
          'code_identity': cand['code_identity']}
    freezepath.write_text(json.dumps(fr))
    with patch.object(runs, 'CANDIDATE_FILE', candpath), patch.object(runs, 'FREEZE_FILE', freezepath), \
         patch.object(ra, 'load_verified_snapshot', lambda: original_loader(repo=None)):
        accepted = runs.frozen_candidate()
        rd = runs.create_research_run(out / 'synthetic-manifests', run_id='metadata-only-not-executed')
        manifest = runs.load_run(rd)
        runs.check_resumable(manifest)
        case['software_mismatch'] = {'candidate_accepted': accepted == cand,
            'manifest_created': True, 'frozen_software': cand['software'], 'run_software': manifest['software'],
            'mismatch': manifest['software'] != cand['software'], 'check_resumable_accepted': True,
            'status': runs.status(rd), 'research_execute_called': False}

    dev = streams.defaults()['development_study_id']
    control_context = contexts.make_context(dev, 0)
    spec = observation.observation_spec(control_context, 'B')
    names, target = metrics.control_alarm_cells(), 'permuted_targets|B|1.0'
    per, nulls, rows = {}, {}, []
    # R2: independent synthetic contexts, constant valid sin/cos observations.
    # Standardised features are zero. W=0 and b=mean(U_train) for every permutation.
    for cid, seed in enumerate((0, 1)):
        rng = np.random.default_rng(seed)
        U = [rng.uniform(-1, 1, (n, 4)) for n in (30, 12, 20)]
        X = [observation.observe(control_context, spec,
                                 np.zeros((len(u), len(snap.C))), np.zeros((len(u), len(snap.C)))) for u in U]
        pt, pv = rng.permutation(30), rng.permutation(12)
        model = training.fit_ridge(spec, X[0], U[0][pt], X[1], U[1][pv])
        pred = metrics.project(decoders.predict(model, X[2]))
        gain = metrics.scores(*metrics.episode_losses(pred, U[2]))['G']
        null = training.permuted_null_gains(X[0], U[0], X[1], U[1], X[2], U[2], np.random.default_rng(99+cid), 9999)
        per[cid] = {name: (np.zeros_like(pred), U[2]) for name in names}
        per[cid][target] = (pred, U[2])
        nulls[cid] = {name: np.zeros(9999) for name in names if name.startswith('permuted')}
        nulls[cid][target] = null
        rows.append({'seed': seed, 'observed_G': gain, 'null_min': float(null.min()),
                     'null_max': float(null.max()), 'null_unique': int(len(np.unique(null))),
                     'observed_minus_null': float(gain-null[0])})
        np.savez(out / f'tie_control_context_{cid}.npz', X_train=X[0], U_train=U[0], X_val=X[1], U_val=U[1],
                 X_test=X[2], U_test=U[2], train_permutation=pt, val_permutation=pv, predictions=pred, null_G=null)
    inputs = runner.alarm_inputs(per, dev, nulls=nulls)
    alarms = metrics.control_alarms(inputs)
    case['roundoff_tie'] = {'contexts': rows, 'features': 'observe of zero states/measurement errors: sin=0, cos=1; all columns constant', 'exact_mathematical_p': 1.0,
        'cell': inputs[target], 'alarm_cell': alarms['cells'][target],
        'positive_alarm': alarms['positive_spurious_success_alarm'],
        'dependence_alarm': alarms['target_dependence_alarm']}

    # Independent normal-equation calculation (no training/decoder functions),
    # positive reference for the vectorised refits on nondegenerate inputs.
    rng = np.random.default_rng(17)
    U = [rng.uniform(-1, 1, (n, 4)) for n in (30, 12, 20)]
    M = rng.normal(size=(4, spec.n_features))
    X = [u @ M + rng.normal(size=(len(u), spec.n_features)) for u in U]
    mean, sd = X[0].mean(0), X[0].std(0)
    Z = [(x-mean)/sd for x in X]; xc = Z[0]-Z[0].mean(0)
    replay, direct = np.random.default_rng(91), []
    grid = np.array(training.LAMBDA_GRID)
    for _ in range(20):
        u, v = U[0][replay.permutation(30)], U[1][replay.permutation(12)]
        ym = u.mean(0); solutions = []
        for lam in grid:
            W = np.linalg.solve(xc.T @ xc / 30 + lam*np.eye(spec.n_features), xc.T @ (u-ym) / 30)
            b = ym-Z[0].mean(0)@W
            mse = np.mean((np.clip(Z[1]@W+b,-1,1)-v)**2)
            solutions.append((mse, -lam, W, b))
        _, _, W, b = min(solutions, key=lambda z: (z[0],z[1]))
        p = np.clip(Z[2]@W+b,-1,1)
        direct.append(3*np.mean(np.mean(U[2]**2,1)-np.mean((p-U[2])**2,1)))
    fast = training.permuted_null_gains(X[0],U[0],X[1],U[1],X[2],U[2],np.random.default_rng(91),20)
    case['independent_refit_reference'] = {'draws':20,'max_abs_error':float(np.max(np.abs(fast-direct)))}

    # R4: actual development trajectories via observe, two contexts, same task,
    # each through the first alarm cell. Only synthetic development data.
    with patch.object(ra, 'load_verified_snapshot', lambda: original_loader(repo=None)):
        rd = runs.create_run(out / 'development', 'smoke', [0,1], run_id='null-binding', conditions=('lantern',),
                             tasks=('B',), sizes={'train':30,'val':12,'test':20}, proposals=1)
    run = runs.load_run(rd); cells=[]
    for cid in (0,1):
        ctx = contexts.make_context(dev,cid)
        prep = runner.prepare_context(ctx,np.array(snap.C),run['grid']['sizes'],1)
        def score(model,cell,X,U):
            c={'context_id':cid, **{k:cell[k] for k in ('condition','control','task','time','time_index')}}
            return runs._persist_cell(rd,run,ctx,c,model,X,U,null_G=cell.get('null_G'),null_meta=cell.get('null_meta'))
        for cell in runner.iter_cells(ctx,prep,float(snap.structure['g']),'lantern','permuted_targets',('B',),scorer=score):
            if cell['time']==1.0:break
        c={'context_id':cid,'condition':'lantern','control':'permuted_targets','task':'B','time':1.0,'time_index':2}
        rec=runs.verify_record(rd,run,c,ctx)
        cells.append((c,ctx,rec,rd/'cells'/runs.cell_dir_name(c)))
    c0,ctx0,rec0,p0=cells[0]; c1,ctx1,rec1,p1=cells[1]
    original_null_hash=rec0['null']['sha256']
    shutil.copyfile(p0/'null.npz',out/'original_context0_null.npz')
    shutil.copyfile(p1/'null.npz',p0/'null.npz')
    rec0['null']=rec1['null']  # Copy the valid null file AND its valid metadata from context 1.
    (p0/'record.json').write_text(json.dumps(rec0))
    try:
        runs.verify_record(rd,run,c0,ctx0)
        outcome={'accepted':True}
    except Exception as e:
        outcome={'accepted':False,'error':type(e).__name__,'message':str(e)}
    case['cross_context_null_with_its_record']={'source_context':1,'destination_context':0,
        'original_null_sha256':original_null_hash,'substituted_null_sha256':rec1['null']['sha256'],
        'different_null':original_null_hash!=rec1['null']['sha256'], 'verify_record':outcome,
        'model_predictions_cell_and_run_metadata_unchanged':True}
    assert not original_freeze.exists()
    result['original_freeze_still_absent']=True
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
