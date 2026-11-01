"""Cece 2 degree targets; joint order LH, LA, RH, RA.

The existing Cece edge-transfer table is retained. This is a simulated gait
candidate: hardware servo neutral angles/signs must be calibrated separately.
"""
from pathlib import Path
import bisect,json,math

HERE=Path(__file__).resolve().parent
PROFILE={'name':'cece2_candidate','hip_deg':15.,'roll_deg':12.,
         'phase_durations_s':[.14,.06,.20,.06,.10], 'command_hz':50.}
POSES=json.loads((HERE.parent/'cece'/'hip_drive_study'/'edge_transfer_results.json').read_text())['poses']
EDGE=sorted((abs(r['body_roll_deg']),abs(r['selected']['swing_ankle_deg']))
            for r in POSES if r['stance']=='left' and r['selected'])
def edge_angle(roll):
    if roll<=EDGE[0][0]:return EDGE[0][1]
    if roll>=EDGE[-1][0]:return EDGE[-1][1]
    i=bisect.bisect_right([r[0] for r in EDGE],roll)
    x0,y0=EDGE[i-1];x1,y1=EDGE[i]
    return y0+(y1-y0)*(roll-x0)/(x1-x0)

def targets(half,phase,u,hip_deg=15.,roll_deg=12.,direction='forward'):
    if half<0 or phase not in range(5) or not 0<=u<=1:
        raise ValueError('Invalid gait phase')
    e=u*u*(3-2*u)
    left=half%2==0
    h0=0 if half==0 else (-hip_deg if left else hip_deg)
    h1=hip_deg if left else -hip_deg
    contact=edge_angle(roll_deg);hip=h0
    if phase==0:
        a=roll_deg*e;b=edge_angle(a)
    elif phase==1:
        a=roll_deg;b=contact+(roll_deg-contact)*e
    elif phase==2:
        a=b=roll_deg;hip=h0+(h1-h0)*e
    elif phase==3:
        a=roll_deg;b=roll_deg+(contact-roll_deg)*e;hip=h1
    else:
        a=roll_deg*(1-e);b=edge_angle(a);hip=h1
    if direction=='backward':hip=-hip
    elif direction!='forward':
        raise ValueError('Cece 2 fast profile is only screened for forward motion')
    sign=1 if left else -1
    return [hip,sign*a,hip,sign*b] if left else [hip,sign*b,hip,sign*a]

def at_time(seconds,profile=PROFILE,direction='forward'):
    if not math.isfinite(seconds) or seconds<0:
        raise ValueError('Time must be finite and nonnegative')
    durations=profile['phase_durations_s'];period=sum(durations)
    half=int(seconds/period);remaining=seconds-half*period
    phase=0
    while phase<4 and remaining>=durations[phase]:
        remaining-=durations[phase];phase+=1
    return targets(half,phase,max(0.,min(1.,remaining/durations[phase])),
                   profile['hip_deg'],profile['roll_deg'],direction)
