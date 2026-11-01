"""Independent timing study: speed up transfers without rushing the hip swing."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, subprocess, sys
HERE=Path(__file__).resolve().parent
cases=[(f'timing_{i}_h{hip}',hip,durations) for i,durations in enumerate([
    [.15,.06,.20,.06,.10], [.12,.06,.20,.06,.12],
    [.15,.08,.20,.08,.12], [.12,.08,.24,.08,.12],
    [.16,.05,.24,.05,.12], [.12,.05,.26,.05,.10],
    [.15,.05,.28,.05,.12], [.16,.08,.28,.08,.16],
]) for hip in (15,20)]
def run(case):
    name,hip,durations=case
    proc=subprocess.run([sys.executable,str(HERE/'simulate.py'),'--name',name,
        '--steps','10','--hip-deg',str(hip),'--phase-seconds','1',
        '--phase-weights',','.join(map(str,durations))],capture_output=True,text=True)
    if proc.returncode:raise RuntimeError(proc.stderr[-2000:])
    result=json.loads((HERE/'results'/f'bullet_{name}_results.json').read_text())['result']
    row={'name':name,'hip_deg':hip,'phase_durations_s':durations,
        'speed_mm_s':round(-result['net_base_displacement_mm'][1]/result['simulated_gait_time_s'],3),
        'fell':result['fell'],'lifts':result['observed_lift_and_land_count'],
        'max_tilt_deg':result['max_body_tilt_deg'],
        'stance_drift_mm':max((s['stance_foot_max_horizontal_drift_mm'] for s in result['step_evidence']),default=999),
        'stance_airborne_s':max((s['stance_foot_airborne_duration_s'] for s in result['step_evidence']),default=999)}
    row['screen_pass']=not row['fell'] and row['lifts']==10 and row['stance_drift_mm']<=2 and row['stance_airborne_s']==0
    print(json.dumps(row),flush=True)
    return row
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,cases))
(HERE/'timing_sweep.json').write_text(json.dumps(rows,indent=2))
