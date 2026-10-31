# ESP32-C3 Otto carrier: proposed electrical connections

**Engineering draft: not routed or approved for manufacture.** Validate all
pin mappings, component dimensions, power/current limits and the mechanical
fit before fabricating. This describes the intended circuit and is not yet a
KiCad schematic.

## Power

The intended battery is four AA cells in series in a switched holder. Battery
positive connects to the Pololu S13V30F5 VIN; battery negative connects to
GND. The module generates 5 V for the four servos, sensor, and buffer. The
5 V output connects to the ESP32-C3 SuperMini 5V pin **through a removable
jumper**. Remove the jumper before connecting USB. Do not assume the
SuperMini protects the USB host from external supply backfeed. The 5 V supply
must never connect to the ESP32 3V3 pin.

The regulator's small header pin sequence, in the orientation of the
manufacturer's top-view image, is EN, VIN, GND, GND, VOUT. Leave EN open for
always-on operation. Exact module mounting and pin orientation need physical
verification. Use a bulk electrolytic across 5 V and GND, with polarity
marked and voltage rating above the supply; final capacitance and connector
current ratings require prototype current measurements. The regulator's output
current depends on input voltage and temperature, and four stalled servos can
overload the supply; verify startup, simultaneous movement, battery sag and
stall behavior on the bench.

## Signals (provisional)

| Function | ESP32 GPIO | Other connection |
|---|---:|---|
| Left leg | 0 | AHCT125 1A pin 2; 1Y pin 3 to servo signal |
| Right leg | 1 | AHCT125 2A pin 5; 2Y pin 6 to servo signal |
| Left foot | 3 | AHCT125 3A pin 9; 3Y pin 8 to servo signal |
| Right foot | 4 | AHCT125 4A pin 12; 4Y pin 11 to servo signal |
| HC-SR04 TRIG | 5 | TRIG input, verify selected sensor's 3.3 V HIGH threshold |
| HC-SR04 ECHO | 6 | 5 V ECHO via 10k series / 15k to GND divider |
| Passive piezo | 7 | Piezo driver to be selected and checked |

Each servo uses GND, 5 V, and the buffered signal. The AHCT125 is powered
from 5 V, has pin 7 to GND and pin 14 to 5 V, with output-enable pins
1, 4, 10, 13 active low; include startup pull-downs on signal inputs and a
100 nF bypass capacitor. Its output and startup behavior, and unpowered-input
behavior, require validation before ordering. GPIO2, 8 and 9 are boot-strapping
pins and are not allocated. GPIO18/19 remain reserved for native USB.

The HC-SR04 connector is VCC, TRIG, ECHO, GND in the common sensor's order.
Confirm order on the actual sensor; use a short keyed harness if the sensor is
in the head and the carrier is in the body. The listed resistors divide a
nominal 5 V echo to 3.0 V; account for 5 V tolerance and resistor tolerance
against ESP32 electrical limits before selecting final resistor values.

Sources: https://www.pololu.com/product/4082 ;
https://www.robotgear.com.au/cache/files/productimageoriginals/81536_5v_3a_step_up_step_down_voltage_regulator_s13v30f5_top_view_with_labeled_pinout_.jpg ;
https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf ;
https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html
