"""Independent checks after exploration; reject interference before ranking."""
import json,itertools
import numpy as np
import drive_study as s
from crank_drive import run as crank_run

def evaluate():
    explored=json.loads((s.OUT/'outboard_sweep.json').read_text())
    candidates=[]
    # Select low-stop as well as fast configurations; do not rank contact chatter.
    eligible=sorted(explored,key=lambda r:r['score']-80*r['hard_stop_fraction'],reverse=True)
    for item in eligible:
        c=item['config'];audit=s.clearance_audit(c)
        if not audit['pass_no_interpenetration'] or audit['worst_separation_mm']<.5:continue
        if any(all(c[k]==e['config'][k] for k in ['frequency','duty','gap','rear','battery_z','limit_deg']) for e in candidates):continue
        cases=[]
        for friction,voltage,mass in itertools.product([.4,.65,1.],[2.4,3.0],[1.,1.2]):
            trial=c.copy();trial.update(friction=friction,stall=.0363*voltage/3,no_load=6.807*voltage/3,mass_scale=mass)
            result,_,_,_=s.run(trial,12);cases.append(result)
        upright=sum(r['upright'] for r in cases)
        passed=sum(r['walking_screen_pass'] for r in cases)
        record=dict(config=c,clearance=audit,cases=cases,upright_cases=upright,walking_screen_cases=passed,
            mean_stop_fraction=float(np.mean([r['hard_stop_fraction'] for r in cases])),
            mean_forward_mm=float(np.mean([r['travel_mm'][0] for r in cases])))
        candidates.append(record)
        print(f'candidate {len(candidates)}: upright {upright}/12, walking screen {passed}/12, mean stop {record["mean_stop_fraction"]:.2f}',flush=True)
        if len(candidates)==8:break
    candidates.sort(key=lambda r:(r['walking_screen_cases'],r['upright_cases'],-r['mean_stop_fraction']),reverse=True)
    (s.OUT/'robustness.json').write_text(json.dumps(candidates,indent=2))
    (s.OUT/'recommended_research_config.json').write_text(json.dumps(candidates[0]['config'],indent=2))
    # Crank ablation with identical settings tests the contribution of weight shift.
    cc=json.loads((s.OUT/'crank_config.json').read_text());ablation=[]
    for enabled in [True,False]:
        c=cc.copy();c['shift_enabled']=enabled
        r,_,_,_=crank_run(c,12);ablation.append(r)
    (s.OUT/'crank_ablation.json').write_text(json.dumps(ablation,indent=2))
    print(json.dumps({k:v for k,v in candidates[0].items() if k!='cases'},indent=2))

if __name__=='__main__':evaluate()
