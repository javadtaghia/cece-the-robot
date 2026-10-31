import json,itertools
import drive_study as s

c=json.loads((s.OUT/'low_audio_config.json').read_text());results=[]
for bias in [-.15,-.10,-.05,0,.05,.10,.15]:
    cc=c.copy();cc['bias']=bias;r,_,_,_=s.run(cc,15);results.append(r)
results.sort(key=lambda r:(r['upright'] and r['travel_mm'][0]>.06*1000, r['travel_mm'][0]-abs(r['travel_mm'][1])*2),reverse=True)
best=results[0]['config']
(s.OUT/'bias_calibration.json').write_text(json.dumps(results,indent=2))
(s.OUT/'audio_demo_config.json').write_text(json.dumps(best,indent=2))
print('Selected nominal bias',best.get('bias'),results[0]['travel_mm'],flush=True)
robust=[]
for friction,voltage,mass in itertools.product([.4,.65,1.],[2.4,3.0],[1.,1.2]):
    cc=best.copy();cc.update(friction=friction,stall=.0363*voltage/3,no_load=6.807*voltage/3,mass_scale=mass)
    r,_,_,_=s.run(cc,15);robust.append(r)
(s.OUT/'audio_robustness.json').write_text(json.dumps(robust,indent=2))
r,_,_,_=s.run(best,30);r['clearance']=s.clearance_audit(best)
(s.OUT/'audio_long_trial.json').write_text(json.dumps(r,indent=2))
print(json.dumps(dict(long_trial=r,upright_cases=sum(x['upright'] for x in robust),walking_screen_cases=sum(x['walking_screen_pass'] for x in robust)),indent=2))
