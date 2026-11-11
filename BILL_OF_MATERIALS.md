# Cece bill of materials — Australian prototype

Prices checked **11 November 2026** (Sydney), in **AUD**, before freight. This is the purchased prototype basket, including spares, plus a separate list of items to check before building. “Ordered” is supported by an order confirmation; it does not mean delivered, installed or tested. Price links go to public retailer listings. Retail pack sizes matter: a pack of resistors makes more than one robot.

## What the project ordered

| Original supplier | Items | Recorded merchandise | Same basket at listed prices |
| --- | --- | ---: | ---: |
| MLAB | ESP32-S3 Sense with camera and microphone | $32.00 | $32.00 |
| Rapid Robotics Australia | Four positional SG90 servos | $18.00 | $18.00 |
| Supercheap Hobbies | Battery and UBEC | $45.39 | $45.39 |
| Little Bird Electronics | OLED and 28 mm speaker | $51.65 | $51.65 |
| Core Electronics | 21 lines of electronics, connectors, wire and bench stock below | $78.38 | $78.38 |
| **Total** | **Ordered merchandise only** | **$225.42** | **$225.42** |

These totals use the order line amounts and the public single-unit or pack prices. They exclude shipping, the charger, PLA and any missing mechanical hardware. They are not a minimum build price or a delivered quote.

### Controller, actuators, power, display and speaker

| Item and original supplier | Qty | Listed price each | Order line | Purpose |
| --- | ---: | ---: | ---: | --- |
| [Seeed Studio XIAO ESP32-S3 Sense — MLAB](https://www.mlab.com.au/products/seeed-studio-xiao-esp32-s3-sense) | 1 | $32.00 | $32.00 | U1. Buy the **Sense** version: camera and digital mic are included. No separate camera or mic purchase for this build. |
| [SG90 positional micro servo — Rapid Robotics](https://rapidroboticsaustralia.com.au/products/sg90-micro-servo) · RR-MOT-SG90 | 4 | $4.50 | $18.00 | M1–M4: two hips, two feet. Use the horns and retaining screws; not a continuous-rotation servo. |
| [Dualsky 550 mAh 2S LiPo — Supercheap Hobbies](https://www.supercheaphobbies.com.au/store/550mah-dualsky-lipo-battery-with-connector-p-51186.html) · DSBXP05502ULT | 1 | $19.99 | $19.99 | BT1. The main power lead and three-wire balance lead have different functions. |
| [Hobbywing UBEC-5A-V2-Air — Supercheap Hobbies](https://www.supercheaphobbies.com.au/store/hobbywing-ubec-p-62554.html) · HW30607000 | 1 | $25.40 | $25.40 | U3. Set and measure 5.0 V before connecting the servo supply. This does not charge the battery. |
| [Adafruit 1.5-inch 128 × 128 grayscale OLED — Little Bird](https://littlebirdelectronics.com.au/products/adafruit-grayscale-1-5-128x128-oled-graphic-display-stemma-qt-qwiic) · 4741 / SSD1327 | 1 | $47.10 | $47.10 | U6. Four-wire STEMMA QT; shares the 3.3 V I²C bus with U4. |
| [Thin 28 mm speaker — Little Bird](https://littlebirdelectronics.com.au/products/thin-speaker-4-ohm-2-5w-28mm) · COM-21311 | 1 | $4.55 | $4.55 | The **ordered** speaker is **4 Ω, 2.5 W**. Connect through the amplifier. The 8 Ω version discussed earlier is not this order line. |

For a replacement, Core also lists the [same OLED at $41.80](https://core-electronics.com.au/adafruit-grayscale-1-5-128x128-oled-graphic-display-stemma-qt-qwiic.html) and [same speaker at $3.75](https://core-electronics.com.au/thin-speaker-4-ohm-25w-28mm.html). Those alternatives are not added to the total.

### Core Electronics order, including through-hole parts

“Qty” is the number of retail units ordered, not the number installed. The current price is per retail unit, including GST.

| Item, supplier link and SKU | Qty | Current unit | Order line | Use on Cece |
| --- | ---: | ---: | ---: | --- |
| [PiicoDev four-channel servo driver](https://core-electronics.com.au/piicodev-servo-driver.html) · CE09181 | 1 | $14.65 | $14.65 | U4; one board for all four SG90s. |
| [Mini pushbutton power switch, LV](https://core-electronics.com.au/pololu-mini-pushbutton-power-switch-with-reverse-voltage-protection-lv.html) · POLOLU-2808 | 1 | $8.30 | $8.30 | U2; between the pack and UBEC. |
| [HC-SR04 ultrasonic module](https://core-electronics.com.au/hc-sr04-ultrasonic-module-distance-measuring-sensor.html) · CE05112 | 1 | $1.95 | $1.95 | U5; use the ECHO divider below. |
| [MAX98357 I²S speaker amplifier](https://core-electronics.com.au/max98357-i2s-amplifier-module.html) · DFR0954 | 1 | $9.84 | $9.84 | One for speaker output; not on the current bench wiring sheet. The S3 Sense already has a microphone. |
| [PiicoDev protoboard](https://core-electronics.com.au/piicodev-protoboard.html) · CE07686 | 1 | $1.75 | $1.75 | One through-hole board for the bench circuit. |
| [PiicoDev breadboard adapter](https://core-electronics.com.au/piicodev-breadboard-adapter.html) · CE07691 | 1 | $1.65 | $1.65 | Breaks the 3.3 V I²C bus out to pins. |
| [100 mm PiicoDev cable](https://core-electronics.com.au/piicodev-cable-100mm.html) · CE07773 | 2 | $0.85 | $1.70 | Two: ESP-side adapter to driver; spare driver socket to OLED. |
| [600-piece ¼ W, 1% resistor kit](https://core-electronics.com.au/600-pack-of-1-4-watt-1-resistors-30-values-20-of-each.html) · CE05092 | 1 | $2.95 | $2.95 | Use one 2.2 kΩ (R1) and one 3.3 kΩ (R2) for HC-SR04 ECHO. Both values are in the kit. |
| [0.1 µF (100 nF) ceramic capacitor](https://core-electronics.com.au/capacitor-ceramic-0-1uf.html) · COM-08375 | 2 | $0.53 | $1.06 | C2: one by the sensor; use ≥25 V per drawing. Second is spare. |
| [1,000 µF / 25 V electrolytic](https://core-electronics.com.au/electrolytic-decoupling-capacitors-1000uf-25v.html) · COM-08982 | 2 | $0.98 | $1.96 | C1: one at servo power input; second spare. Observe polarity. |
| [1N5819 axial Schottky diode](https://core-electronics.com.au/schottky-diode.html) · COM-10926 | 2 | $0.53 | $1.06 | D1: one for ESP supply branch; second spare. |
| [120-piece electrolytic capacitor kit](https://core-electronics.com.au/120-pack-of-electrolytic-capacitors-12-types-10-of-each.html) · CE05130 | 1 | $2.40 | $2.40 | Bench stock; not needed in addition to the specified C1. |
| [2.54 mm male header, 1 × 40](https://core-electronics.com.au/male-pin-header-2-54mm-1x40.html) · CE07828 | 1 | $0.45 | $0.45 | Cut to length for modules and JP1; the removable shunt is separate. |
| [2.54 mm female header, 1 × 20](https://core-electronics.com.au/0-100-2-54-mm-female-header-1x20-pin-straight.html) · CE07759 | 2 | $0.29 | $0.58 | Two strips for sockets; cut to fit. |
| [20 cm female–female jumper ribbon, 40 wires](https://core-electronics.com.au/solderless-breadboard-jumper-cable-wires-female-female-40-pieces.html) · CE05098 | 1 | $3.95 | $3.95 | Logic and bench connections, not motor power. |
| [18 AWG silicone power wire, red and black](https://core-electronics.com.au/high-temperature-resistant-silicone-wire-18awg-0-75mm2-1m-red-black.html) · FIT0585 | 1 | $5.28 | $5.28 | One retail pack for the power harness. |
| [JST RCY male pigtail, 10 cm](https://core-electronics.com.au/jst-rcy-plug-with-10cm-leads-male.html) · POLOLU-2181 | 1 | $4.95 | $4.95 | One of each mating half was ordered. Confirm the actual pack plug and polarity. |
| [JST RCY female pigtail, 10 cm](https://core-electronics.com.au/jst-rcy-plug-with-10cm-leads-female.html) · POLOLU-2180 | 1 | $4.95 | $4.95 | Matching harness half; only one mating half is needed at the battery. |
| [JST PH two-pin cable, male header, 200 mm](https://core-electronics.com.au/jst-ph-2-pin-cable-male-header-200mm.html) · ADA3814 | 1 | $1.60 | $1.60 | Accessory; verify pitch, polarity and mating part before use. |
| [JST-PH two-pin jumper cable, 100 mm](https://core-electronics.com.au/jst-ph-2-pin-jumper-cable-100mm-long.html) · ADA4714 | 1 | $1.90 | $1.90 | Accessory; not the three-wire 2S balance lead. |
| [USB Type-C plug breakout](https://core-electronics.com.au/adafruit-usb-type-c-plug-breakout.html) · ADA5978 | 1 | $5.45 | $5.45 | Bench accessory; this is a plug, not a panel charging socket or a LiPo charger. |
| **Core merchandise subtotal** | | | **$78.38** | |

## Items to check separately

These prices are examples for missing items, not evidence of purchase.

| Check before ordering | Quantity and example price | What to verify |
| --- | --- | --- |
| JP1 removable programming link | 1 × [2.54 mm shunt, Core — $0.86](https://core-electronics.com.au/jumper-2-pin.html) | Fit to two pins cut from the purchased male header. Remove JP1 before connecting PC USB as shown in the schematic. |
| External 2S LiPo balance charger | 1 required for recharging; [ISDT UC2 study candidate, M1 Hobby Store — $19.95](https://m1hobbystore.com.au/isdt-uc2-1s-2s-usb-c-lipo-charger/) | Charger purchase and installed charge port are unconfirmed. Match the actual balance plug, polarity and pack charge rating to the charger; the UC2 is fixed at 0.8 A. Disconnect the robot load for charging. See the [charging interface review](experiments/cece/packaging_study/CHARGING_INTERFACE_REVIEW.md). |
| Horns, ankle retainers and ties | Four servo horn sets; for the captive-ankle design, two pointed M2 × 8 mm screws and four narrow ties. Examples: [2 × 8 tapping screws, $5.90/10](https://plaig.com.au/product/2x8mm-button-head-screws-with-tapping-thread-pack-of-10/) and [2.5 mm nylon ties, $4.55/100](https://www.altronics.com.au/product/h4012a-100mm-natural-cable-ties-pk-100) | Check the servo bags first. Confirm screw tip, head, pilot grip and tie-slot fit against the [ankle assembly notes](experiments/cece/ankle_v2/README.md). |
| Printed parts and PLA | [1 kg eSUN green PLA+, Jaycar — $19.95](https://www.jaycar.com.au/esun-green-pla-filament-1kg-1-75mm/p/TL4462) | Slicer estimates: [prototype plate](experiments/cece/print_preparation/README.md) 150.7 g (about $3.01 of PLA); [R16 carrier](experiments/cece/esp_head_carrier/R16_REVIEW.md) 5.99 g (about $0.12). Excludes reprints. |
| Bench supplies | USB-C **data** cable, solder, insulation/heat-shrink and battery retention as needed | Reuse what is on hand. Final harness lengths, enclosure fasteners and physical fits depend on the chosen printed revision; no confirmed purchase price. |

Use the [combined KiCad schematic](experiments/cece/electronics/kicad_s3_bench/Cece_USB_Bench_Wiring.kicad_sch) for wiring and the [power and charging notes](experiments/cece/electronics/kicad_s3_bench/POWER_AND_CHARGING.txt) for power modes. A USB breakout alone cannot charge a 2S pack. The amplifier and speaker are ordered expansion parts, not a validated S3 audio-output circuit. No separate LED mouth or earlier controller is required for this revision.
