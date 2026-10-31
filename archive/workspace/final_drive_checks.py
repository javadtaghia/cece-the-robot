import json,itertools
import drive_study as s

c=json.loads((s.OUT/'recommended_research_config.json').read_text())
numerical=[]
for dt in [.001,.0005,.00025]:
    cc=c.copy();cc['timestep']=dt
    r,_,_,_=s.run(cc,12);numerical.append(r)
(s.OUT/'timestep_sensitivity.json').write_text(json.dumps(numerical,indent=2))
print('Numerical timestep sensitivity:',[(r['config']['timestep'],r['travel_mm'],r['upright']) for r in numerical],flush=True)
audio=[]
for f,duty,rear in itertools.product([1.,1.5,2.,2.5],[.25,.4,.55],[.010,.014]):
    cc=c.copy();cc.update(audio_low=True,realistic_hardware=True,frequency=f,duty=duty,rear=rear)
    r,_,_,_=s.run(cc,10);r['clearance']=s.clearance_audit(cc)
    r['score']=(100 if r['upright'] else 0)+r['travel_mm'][0]-abs(r['travel_mm'][1])*.7-r['max_tilt_deg']-100*r['hard_stop_fraction']
    audio.append(r)
audio.sort(key=lambda r:r['score'],reverse=True)
(s.OUT/'low_audio_sweep.json').write_text(json.dumps(audio,indent=2))
(s.OUT/'low_audio_config.json').write_text(json.dumps(audio[0]['config'],indent=2))
print(json.dumps(audio[:2],indent=2))
