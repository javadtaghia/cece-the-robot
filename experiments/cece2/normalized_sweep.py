"""Refine at the intended 50 Hz command rate and two solver steps."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,sys
HERE=Path(__file__).resolve().parent
configs=[(15,[.12,.06,.20,.06,.12]),(16,[.12,.06,.20,.06,.12]),
         (17,[.12,.06,.24,.06,.12]),(18,[.14,.06,.24,.06,.14])]
def run(case):
    i,hz=case;hip,durations=configs[i];name=f'normalized_{i}_{hz}'
    proc=subprocess.run([sys.executable,str(HERE/'simulate.py'),'--name',name,
        '--steps','40','--hip-deg',str(hip),'--phase-seconds','1',
        '--phase-weights',','.join(map(str,durations)), '--command-hz','50','--normalized-controller','--hz',str(hz)],capture_output=True,text=True)
    if proc.returncode:raise RuntimeError(proc.stderr[-2000:])
    r=json.loads((HERE/'results'/f'bullet_{name}_results.json').read_text())['result']
    row={'name':name,'hip_deg':hip,'phase_durations_s':durations,'physics_hz':hz,
        'speed_mm_s':round(-r['net_base_displacement_mm'][1]/r['simulated_gait_time_s'],3),
        'fell':r['fell'],'lifts':r['observed_lift_and_land_count'],
        'contact_slip_mm':max((s['stance_contact_slip_integral_mm'] for s in r['step_evidence']),default=999),
        'stance_drift_mm':max((s['stance_foot_max_horizontal_drift_mm'] for s in r['step_evidence']),default=999),
        'stance_airborne_s':max((s['stance_foot_airborne_duration_s'] for s in r['step_evidence']),default=999)}
    row['screen_pass']=not row['fell'] and row['lifts']==40 and row['stance_drift_mm']<=2 and row['stance_airborne_s']==0
    row['ten_x_speed']=row['speed_mm_s']>=21.22
    print(json.dumps(row),flush=True);return row
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,[(i,hz) for i in range(len(configs)) for hz in (240,480)]))
(HERE/'normalized_refinement.json').write_text(json.dumps(rows,indent=2))
