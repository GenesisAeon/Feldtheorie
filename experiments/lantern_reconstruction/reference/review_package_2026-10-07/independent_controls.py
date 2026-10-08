"""Independent analytical controls for the Lantern planning package.

No Feldtheorie/SCF imports, no training, no research episodes. NumPy/SciPy only.
Run: python independent_controls.py --output independent_control_results.json
"""
from __future__ import annotations
import argparse
import json
import math
import platform
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.integrate import solve_ivp


def run():
    rows = []
    def check(name, condition, values=None):
        if not bool(condition):
            raise AssertionError(name)
        rows.append(dict(id=name, passed=True, values=values or {}))
    def wrap(x):
        return np.arctan2(np.sin(x), np.cos(x))
    E = np.zeros((10, 4))
    for j in range(4):
        E[2*j, j], E[2*j+1, j] = 1/math.sqrt(2), -1/math.sqrt(2)
    check('K01_encoding', np.allclose(E.T@E, np.eye(4)) and np.allclose(E.sum(0), 0))
    u = np.array([.9, -.3, .1, -.8]); a=.35; p=wrap(3.1+a*E@u)
    recovered = np.array([wrap(p[2*j]-p[2*j+1])/(math.sqrt(2)*a) for j in range(4)])
    check('K02_immediate_inverse', np.allclose(recovered,u,atol=1e-14))
    def features(x, ref=9):
        d=np.delete(x-x[ref],ref)
        return np.r_[np.sin(d),np.cos(d)]
    check('K03_global_rotation', np.allclose(features(p),features(wrap(p+2.2)),atol=1e-14))
    omega=np.linspace(-.1,.1,10); dt=.02; q=p.copy()
    for _ in range(500):q=wrap(q+dt*omega)
    err=float(np.max(abs(wrap(q-wrap(p+10*omega)))))
    check('K04_free_drift',err<1e-12,dict(max_circular_error=err))
    sigma=.03; D=np.c_[np.eye(9),-np.ones(9)]
    covariance=sigma**2*D@D.T
    check('K05_reference_covariance',np.allclose(covariance,sigma**2*(np.eye(9)+np.ones((9,9)))))
    check('K06_common_reference_cancels_in_pair', abs(float((D[0]-D[1])@(D[0]-D[1]))-2)<1e-14)
    delta0=.4; k=.7; t=1.3
    exact=2*math.atan(math.tan(delta0/2)*math.exp(-2*k*t))
    numerical=solve_ivp(lambda _,y:-2*k*np.sin(y),(0,t),[delta0],rtol=1e-12,atol=1e-14).y[0,-1]
    check('K07_two_oscillator_exact',abs(numerical-exact)<1e-11,dict(delta=exact))
    jac=math.exp(-2*k*t)*(1+math.tan(delta0/2)**2)/(1+math.exp(-4*k*t)*math.tan(delta0/2)**2)
    check('K08_finite_time_not_erasure',0<jac<1,dict(derivative=jac))
    C=np.ones((4,4))-np.eye(4); L=np.diag(C.sum(1))-C
    v=np.array([1,-1,0,0])/math.sqrt(2)
    check('K09_complete_graph_decay',np.allclose(expm(-L*.3)@v,math.exp(-1.2)*v,atol=1e-14))
    check('K10_uniform_remote_zero',np.linalg.norm((expm(-L*.3)@v)[2:])<1e-14)
    C=np.zeros((4,4))
    for i,j in [(0,2),(2,3),(3,1)]:C[i,j]=C[j,i]=1
    L=np.diag(C.sum(1))-C
    peak_t=math.atanh(1/math.sqrt(2))/math.sqrt(2)
    H=lambda t: math.exp(-2*t)*math.sinh(math.sqrt(2)*t)
    vals=[]
    for t in [0,.1,peak_t,1,4]:
        out=expm(-L*t)@v
        vals.append(abs((out[2]-out[3])-H(t)))
    check('K11_remote_path_transfer',max(vals)<1e-14,dict(peak_time=peak_t,peak_gain=H(peak_t)))
    check('K12_remote_peak',H(peak_t)>H(peak_t-.01) and H(peak_t)>H(peak_t+.01))
    t=.8; g=.4; unit=1000
    check('K13_time_rescaling',np.allclose(expm(-g*L*t),expm(-(g/unit)*L*(unit*t)),atol=1e-14))
    evals=np.linalg.eigvalsh(expm(-L*.5))
    check('K14_symmetric_linear_contraction',evals.min()>0 and evals.max()<=1+1e-14)
    oldvar=lambda dt:sigma**2*2*dt
    newvar=lambda dt:sigma**2*2
    check('K15_noise_scaling',math.isclose(oldvar(.01)/oldvar(.02),.5) and newvar(.01)==newvar(.02),dict(old_variance_dt_002=oldvar(.02),brownian_variance=newvar(.02)))
    W=np.array([[0,.2,.3,.4],[.2,0,.5,.6],[.3,.5,0,.7],[.4,.6,.7,0]])
    V=W.copy();delta=.1
    for i,j,sign in [(0,1,1),(2,3,1),(0,2,-1),(1,3,-1)]:
        V[i,j]+=sign*delta;V[j,i]+=sign*delta
    check('K16_strength_preserving_switch',np.allclose(W.sum(1),V.sum(1)) and not np.allclose(W,V) and V.min()>=0 and V.max()<=1)
    perm=[2,0,3,1];x=np.array([.1,.2,-.3,.6]);D0=np.diag(W.sum(1))-W; WP=W[np.ix_(perm,perm)]
    DP=np.diag(WP.sum(1))-WP
    check('K17_joint_permutation',np.allclose((D0@x)[perm],DP@x[perm]))
    check('K18_wrong_order_detected',not np.allclose((D0@x)[perm],DP@x))
    target=np.array([[.1]*4,[.2]*4]); pred=np.zeros_like(target)
    mse=float(np.mean((target-pred)**2)); S=1-3*mse;G=3*float(np.mean(target**2-(target-pred)**2))
    check('K19_score_not_gain',G==0 and S>.9,dict(S=S,G=G))
    p=np.array([.03,.04]);adj=np.maximum.accumulate(p*np.array([2,1]))
    check('K20_holm_two_tests',np.allclose(adj,[.06,.06]) and np.all(adj>.05))
    z=np.log1p(np.array([0,.5,1,2,3,5,10]));w=np.zeros(len(z));w[:-1]+=np.diff(z)/2;w[1:]+=np.diff(z)/2;w/=z[-1]-z[0]
    check('K21_fixed_grid_aggregate',abs(w.sum()-1)<1e-14 and np.all(w>0),dict(weights=w.tolist()))
    bad=np.ones((2,4)); Gbad=3*float(np.mean(target**2-(target-bad)**2))
    check('K22_negative_gain_is_valid',Gbad<0,dict(G=Gbad))
    return dict(schema='lantern-independent-controls-v1',scope='analytical controls; no production integration or study',python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,passed=len(rows),total=len(rows),checks=rows)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=run();text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    print(text)
