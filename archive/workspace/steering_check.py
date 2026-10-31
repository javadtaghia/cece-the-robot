import json
import drive_study as s
c=json.loads((s.OUT/'audio_demo_config.json').read_text());results=[]
for gain in [-.2,-.1,-.05,-.025,0,.025,.05,.1,.2]:
    cc=c.copy();cc['heading_gain']=gain;r,_,_,_=s.run(cc,20);results.append(r)
results.sort(key=lambda r:(r['upright'] and r['travel_mm'][0]>60, r['travel_mm'][0]-abs(r['travel_mm'][1])*2-abs(r['final_yaw_deg'])),reverse=True)
(s.OUT/'steering_trials.json').write_text(json.dumps(results,indent=2))
print(json.dumps([{'gain':r['config']['heading_gain'],'travel_mm':r['travel_mm'],'yaw':r['final_yaw_deg'],'upright':r['upright']} for r in results],indent=2))
