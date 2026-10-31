from pathlib import Path
import FreeCAD as App, Mesh
repo=Path(r'C:\Users\user\OneDrive\Documents\ChatGPT\simple_robot\xgoduck_project_repo')
out=Path(r'C:\Users\user\OneDrive\Documents\ChatGPT\simple_robot\Cece_Prototype_Plate')
doc=App.openDocument(str(repo/'experiments/cece/no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd'))
names=['Rounded_Head_Study','Rear_Cover_Study','Body','Heart_Frame_V3','Antenna','Left_Arm','Right_Arm','Left_Leg','Right_Leg','Left_Foot','Right_Foot','Left_Washer','Right_Washer','Charger_Tray','Charger_Bezel']
for name in names:
 o=doc.getObject(name)
 if o is None: print('MISSING',name);continue
 Mesh.export([o],str(out/(name+'.stl')))
 print(name,round(o.Shape.Volume,2))
App.closeDocument(doc.Name)
