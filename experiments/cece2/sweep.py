"""Measure gait speed, lift/landing, stance slip and falls; never alter Cece 1."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, json, subprocess, sys

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--python',default=sys.executable)
args=parser.parse_args()
cases=[('baseline',.8,10),('ten_x_timing',.08,10)]
cases += [(f'p{int(phase*1000)}_h{hip}',phase,hip)
          for phase in (.12,.16,.20,.25,.32,.4) for hip in (10,15,20,25)]
def run(case):
    name,phase,hip=case
    cmd=[args.python,str(HERE/'simulate.py'),'--name',name,'--phase-seconds',str(phase),
         '--hip-deg',str(hip),'--steps','10']
    proc=subprocess.run(cmd,capture_output=True,text=True)
    if proc.returncode:
        raise RuntimeError(name+': '+proc.stderr[-2000:])
    report=json.loads((HERE/'results'/f'bullet_{name}_results.json').read_text())
    result=report['result']; duration=result['simulated_gait_time_s']
    # Existing model forward direction is negative Y.
    forward=-result['net_base_displacement_mm'][1]
    row={'name':name,'phase_s':phase,'hip_deg':hip,
         'speed_mm_s':round(forward/duration,3),'forward_mm':forward,
         'time_s':duration,'fell':result['fell'],
         'lift_land_count':result['observed_lift_and_land_count'],
         'completed_half_steps':result['completed_half_steps'],
         'max_tilt_deg':result['max_body_tilt_deg'],
         'max_tracking_error_deg':result['max_joint_tracking_error_deg'],
         'max_stance_drift_mm':max((s['stance_foot_max_horizontal_drift_mm'] for s in result['step_evidence']),default=None)}
    print(json.dumps(row),flush=True)
    return row
with ThreadPoolExecutor(max_workers=3) as pool:
    rows=list(pool.map(run,cases))
base=rows[0]['speed_mm_s']
for row in rows:
    row['speed_ratio_to_baseline']=round(row['speed_mm_s']/base,3)
    row['screen_pass']=(not row['fell'] and row['lift_land_count']==10 and row['forward_mm']>0
        and row['max_stance_drift_mm'] is not None and row['max_stance_drift_mm']<=2)
summary={'target_speed_ratio':10,'baseline_speed_mm_s':base,'target_speed_mm_s':base*10,
         'acceptance':'10/10 lift-and-land, no fall, positive travel, stance drift <=2 mm; screening only',
         'cases':rows}
(HERE/'speed_sweep.json').write_text(json.dumps(summary,indent=2))
