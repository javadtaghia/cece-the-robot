"""Build a separate Gazebo scene using Cece's geometry and Cece 2's range needs.

This is a visualization/controller trial, not the validated Bullet contact model.
Run inside Ubuntu with ROS Jazzy sourced so mesh paths use Linux file URLs.
"""
from pathlib import Path
import copy,importlib.util,math,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'cece'/'ros2_sim'/'build_prototype_world.py'
spec=importlib.util.spec_from_file_location('cece_original_world',SOURCE)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
OUT=HERE/'generated'/'cece2_room.sdf'
OUT.parent.mkdir(exist_ok=True)
builder.OUT=OUT
builder.main()
tree=ET.parse(OUT);world=tree.getroot().find('world')
world.set('name','cece2_room')
model=world.find("model[@name='cece_prototype']");model.set('name','cece2')
for joint in model.findall('joint'):
    limit=joint.find('axis/limit')
    # Cece 2's edge-transfer target reaches 34.248 degrees. The old world's
    # 30-degree stop clipped it. This range is still a model assumption.
    limit.find('lower').text=str(-math.pi/4)
    limit.find('upper').text=str(math.pi/4)
    limit.find('velocity').text=str(math.radians(500))
gui=ET.SubElement(world,'gui',{'fullscreen':'false'})
config=Path('/opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/gui/gui.config')
raw=config.read_text().replace('<?xml version="1.0"?>','')
defaults=ET.fromstring('<config>'+raw+'</config>')
for plugin in defaults.findall('plugin'):
    gui.append(copy.deepcopy(plugin))
scene=gui.find("plugin[@filename='MinimalScene']")
scene.find('camera_pose').text='0.25 -0.32 0.24 0 0.38 2.23'
ET.indent(tree,space='  ');tree.write(OUT,encoding='utf-8',xml_declaration=True)
print('Cece 2 viewer world:',OUT)
