import FreeCAD as App, Part
from pathlib import Path
s=Part.read(str(Path(__file__).resolve().parent/'reference/piicodev_ce09181.step'))
for i,v in enumerate(s.Solids):
 b=v.BoundBox
 if b.ZMax>4:print(i,'bounds',(round(b.XMin,2),round(b.YMin,2),round(b.ZMin,2)),(round(b.XMax,2),round(b.YMax,2),round(b.ZMax,2)))
