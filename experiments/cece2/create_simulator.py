"""Create the isolated Cece 2 parameter study from the preserved Cece model.

This generator only writes inside experiments/cece2; source assets stay read-only.
"""
from pathlib import Path
import hashlib

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'cece' / 'bullet_gait' / 'simulate_bullet.py'
text = SOURCE.read_text(encoding='utf-8')
text = text.replace('HERE=Path(__file__).resolve().parent',
    "OUT=Path(__file__).resolve().parent\nHERE=OUT.parent/'cece'/'bullet_gait'")
text = text.replace("parser.add_argument('--friction'", """parser.add_argument('--hip-deg',type=float,default=10.)
parser.add_argument('--roll-deg',type=float,default=12.)
parser.add_argument('--no-load-speed',type=float,default=500.)
parser.add_argument('--phase-weights',default='1,1,1,1,1')
parser.add_argument('--command-hz',type=float,default=240.)
parser.add_argument('--normalized-controller',action='store_true')
parser.add_argument('--gui',action='store_true')
parser.add_argument('--friction'""")
text = text.replace('args=parser.parse_args()', """args=parser.parse_args()
weights=[float(v) for v in args.phase_weights.split(',')]
if len(weights)!=5 or min(weights)<=0 or not 0<args.hip_deg<=30 or not 0<args.roll_deg<=20 or args.no_load_speed<=0:
    raise ValueError('Invalid Cece 2 gait parameters')
""")
text = text.replace('math.radians(500)', 'math.radians(args.no_load_speed)')
text = text.replace('positionGain=.12,velocityGain=.8',
    'positionGain=(1-math.exp(math.log(.88)*240/args.hz) if args.normalized_controller else .12),velocityGain=.8')
text = text.replace('cid=p.connect(p.DIRECT)', '''cid=p.connect(p.GUI if args.gui else p.DIRECT)
if args.gui:
    p.resetDebugVisualizerCamera(cameraDistance=.5,cameraYaw=40,cameraPitch=-15,cameraTargetPosition=[0,-.08,.07])''')
text = text.replace('p.stepSimulation();tstep+=1', 'p.stepSimulation();tstep+=1\n            if args.gui:time.sleep(1/args.hz)')
start = text.index('def target(half,phase,u):')
end = text.index('\ndef base_state():', start)
target = '''from gait import targets as cece2_targets
def target(half,phase,u):
    return cece2_targets(half,phase,u,args.hip_deg,args.roll_deg)
'''
text = text[:start] + target + text[end:]
text = text.replace('tstep=0;steps_per_phase=', 'last_command_tick=-1;held_angles=[0,0,0,0]\ntstep=0;steps_per_phase=')
text = text.replace('angles=target(half,phase,u);limits=commands(angles)', '''command_tick=int(tstep*args.command_hz/args.hz)
            if command_tick!=last_command_tick:
                held_angles=target(half,phase,u);last_command_tick=command_tick
            angles=held_angles;limits=commands(angles)''')
text = text.replace("'hip_amplitude_deg':args.hip_deg", "'target_command_hz':args.command_hz,'hip_amplitude_deg':args.hip_deg")
text = text.replace("for k in range(steps_per_phase):", "for k in range(round(steps_per_phase*weights[phase])):")
text = text.replace('u=(k+1)/steps_per_phase;', 'u=(k+1)/round(steps_per_phase*weights[phase]);')
text = text.replace("HERE/f'bullet_{args.name}", "OUT/'results'/f'bullet_{args.name}")
text = text.replace("'phase_duration_s':args.phase_seconds", "'normalized_position_response':args.normalized_controller,'position_response_reference_gain_at_240hz':.12,'target_command_hz':args.command_hz,'hip_amplitude_deg':args.hip_deg,'roll_deg':args.roll_deg,'phase_weights':weights,'phase_duration_s':args.phase_seconds")
text = text.replace("'assumed_no_load_speed_deg_per_s':500", "'assumed_no_load_speed_deg_per_s':args.no_load_speed")
text = text.replace('stance_anchor=None;stance_max_drift=0.;stance_airborne_ticks=0',
                    'stance_anchor=None;stance_max_drift=0.;stance_airborne_ticks=0;stance_slip_m=0.')
text = text.replace('for c in contacts:\n                if c[3]', '''if phase in (1,2,3):
                cs=[c for c in contacts if c[3]==stance_index]
                if cs:
                    st=p.getLinkState(shape,stance_index,computeLinkVelocity=True)
                    vc=np.asarray(st[6]);omega=np.asarray(st[7]);com=np.asarray(st[0])
                    tangential=[np.linalg.norm((vc+np.cross(omega,np.asarray(c[5])-com))[:2]) for c in cs]
                    stance_slip_m+=float(np.mean(tangential))/args.hz
            for c in contacts:
                if c[3]''')
text = text.replace("'stance_foot_max_horizontal_drift_mm':round(stance_max_drift*1000,2)",
                    "'stance_contact_slip_integral_mm':round(stance_slip_m*1000,3),'stance_foot_max_horizontal_drift_mm':round(stance_max_drift*1000,2)")
text = text.replace("'limitations':[", "'cece2_source_baseline_sha256':'"+hashlib.sha256(SOURCE.read_bytes()).hexdigest()+"',\n 'limitations':[")
(OUT/'simulate.py').write_text(text,encoding='utf-8')
print('Created Cece 2 simulator; Cece 1 source and assets unchanged')
