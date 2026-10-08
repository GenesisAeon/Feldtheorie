"""Read-only source audit. Executes only explicitly selected AST class methods.

This is NOT a complete Lantern import/integration test. No repository package
initializers, CollectiveField, simulator, training, or research are executed.
Pass a trusted local repository via --source-root; output is a new audit JSON.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import yaml

EXPECTED={
 'v9_alpha/api/lantern_bridge.py':'db45f76fbae6c1a23be547f5ddf19d64f410f9d54ea4cdb628da2943903c54d4',
 'v9_alpha/config/lantern_hub.yaml':'5622d38e1ab5306fc69b34d87694ee0b4797f7e102dc1f48477fd907ffe16786',
 'v9_alpha/models/phase_dynamics.py':'3ad681d428d53e7b73692983904a53f80257c02e48b200b76e6e3982f22f259d',
}

def selected_class(text,name,methods,namespace):
    original=next(x for x in ast.parse(text).body if isinstance(x,ast.ClassDef) and x.name==name)
    chosen=[x for x in original.body if isinstance(x,ast.FunctionDef) and x.name in methods]
    if {x.name for x in chosen}!=set(methods):raise ValueError('missing expected method')
    original.body=chosen
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),original],type_ignores=[])
    exec(compile(ast.fix_missing_locations(module),'<selected-source-methods>','exec'),namespace)
    return namespace[name]

def run(root):
    hashes={}
    for path,expected in EXPECTED.items():
        raw=(root/path).read_bytes();normalized=raw.replace(b'\r\n',b'\n')
        hashes[path]={'raw_sha256':hashlib.sha256(raw).hexdigest(),'lf_sha256':hashlib.sha256(normalized).hexdigest()}
        if hashes[path]['lf_sha256']!=expected:raise ValueError('Source differs from reviewed baseline: '+path)
    rows=yaml.safe_load((root/'v9_alpha/config/lantern_hub.yaml').read_text(encoding='utf-8'))['lanterns']
    ids=[r['id'] for r in rows]
    if len(set(ids))!=len(ids):raise ValueError('duplicate IDs')
    nodes={r['id']:SimpleNamespace(beta=float(r['beta']),em_properties=SimpleNamespace(**{k:float(v) for k,v in r['em_properties'].items()})) for r in rows}
    Z=137.03599206*(1+math.sqrt(5))/2
    namespace={'np':np,'ALPHA_INV':137.03599206,'PHI':(1+math.sqrt(5))/2,'calculate_impedance':lambda:Z}
    methods=['calculate_em_coupling','calculate_impedance_matching','calculate_total_coupling','_build_coupling_matrix']
    cls=selected_class((root/'v9_alpha/api/lantern_bridge.py').read_text(encoding='utf-8'),'LanternNetwork',methods,namespace)
    obj=cls.__new__(cls);obj.lanterns=nodes;obj._build_coupling_matrix()
    ordered=sorted(ids);perm=[ids.index(i) for i in ordered];actual=obj.coupling_matrix[np.ix_(perm,perm)]
    independent=np.zeros_like(actual);clipped=0
    for i,key in enumerate(ordered):
        x=nodes[key]
        for j in range(i+1,len(ordered)):
            y=nodes[ordered[j]];ex=x.em_properties;ey=y.em_properties
            distance=min(1,abs(x.beta-y.beta)/20);wave=(ex.wavelength_cm+ey.wavelength_cm)/2
            raw=Z/100/(1+((ex.frequency_hz-ey.frequency_hz)/13.5e6)**2)*math.exp(-distance/(wave/10))*(ex.kappa_em+ey.kappa_em)/2
            clipped+=raw>1
            independent[i,j]=independent[j,i]=min(max(raw,0),1)/(1+abs(ex.impedance_z-ey.impedance_z)/Z)
    error=float(np.max(abs(actual-independent)))
    if error>1e-14:raise AssertionError('matrix comparison failed')
    strengths=independent.sum(1);g=1/strengths.max();L=g*(np.diag(strengths)-independent);ev=np.linalg.eigvalsh(L)
    phasecls=selected_class((root/'v9_alpha/models/phase_dynamics.py').read_text(encoding='utf-8'),'PhaseEvolver',['__init__','evolve_phases'],{'np':np})
    rng=np.random.default_rng(2026100701);phases=rng.normal(0,.1,34);omega=rng.normal(0,.1,34);omega-=omega.mean()
    evolver=phasecls(dt=.02,noise_level=0,coupling_strength_scale=g);x=phases.copy();y=phases.copy()
    np.random.seed(1234);before=np.random.get_state()[1].copy()
    for _ in range(200):
        x=evolver.evolve_phases(x,actual,omega)
        velocity=omega+g*np.sum(actual*np.sin(y[None,:]-y[:,None]),axis=1)
        y=np.arctan2(np.sin(y+.02*velocity),np.cos(y+.02*velocity))
    phase_error=float(np.max(abs(np.arctan2(np.sin(x-y),np.cos(x-y)))))
    if phase_error>1e-12:raise AssertionError('phase comparison failed')
    result=dict(scope='selected source methods only; full loader/import and experiment untested',source_hashes=hashes,nodes=len(ids),edges=int(np.count_nonzero(np.triu(independent,1))),kappa_clipped_edges=int(clipped),final_edges_at_one=int(np.count_nonzero(np.triu(independent,1)==1)),strength_min=float(strengths.min()),strength_max=float(strengths.max()),g=float(g),lambda2=float(ev[1]),lambda_max=float(ev[-1]),mean_weight=float(independent[np.triu_indices(34,1)].mean()),matrix_max_abs_error=error,phase_200_steps_max_circular_error=phase_error,zero_noise_consumes_global_rng=not np.array_equal(before,np.random.get_state()[1]),canonical_ids=ordered)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',type=Path);args=p.parse_args()
    result=run(args.source_root);text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    print(text)
