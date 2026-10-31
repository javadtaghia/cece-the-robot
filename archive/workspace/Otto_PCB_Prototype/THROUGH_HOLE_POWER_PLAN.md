# Otto through-hole prototype: preliminary power plan

Status: purchasing and engineering draft; not a tested or complete build.

Use the existing ESP32-C3 SuperMini, four 180-degree SG90 servos, HC-SR04, piezo, and a hand-soldered 2.54 mm prototyping board. The earlier KiCad PCB and its power and connector layout do not implement this arrangement.

Candidate power: Dualsky XP05502ULT 2S 550 mAh LiPo (52 x 31 x 12 mm), Hobbywing UBEC-5A-V2-Air set to 5 V, and a compatible 2S balance charger. The battery and regulator are in the Supercheap Hobbies cart. Confirm pack balance-connector pinout, power-plug mating, current ratings, battery protection, low-voltage cutoff, enclosure fit, and charger integration before connecting or ordering.

The battery's two-cell voltage must never be connected directly to the 5 V electronics. The UBEC is not a charger and is not a battery-management system. Prevent 5 V backfeeding when the ESP32 USB is connected. Servo supply wiring and connectors must carry the combined current; a solderless breadboard is not the servo power bus. Set and measure the UBEC output before connecting electronics. Verify HC-SR04 echo is shifted to a safe ESP32 voltage.

Target body charging port: USB-C input to a properly matched 2S balance charger, with charging while robot power is off unless the chosen charger explicitly supports the system arrangement. The USB socket alone cannot charge a 2S battery. The selected charger, mounting geometry and cell protection are not yet specified; no body STL has been changed. Do not connect USB directly to the battery or its balance lead.

Open items: through-hole SN74AHCT125N, resistors for sensor divider and servo input pull-downs, correctly rated battery connector and wiring, fuse, switch, two-cell protection, matched charging module and USB-C panel mount, and a mechanically checked layout. The currently selected SG90 vendor does not specify stall current. Confirm the actual servo and horn fit, battery mounting and printed clearances.
