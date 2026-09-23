# Modular Smart Glasses: PCB Layer Stackup, Mechanical & Electrical Specification

## 1. System Hardware Architecture Overview

The modular smart glasses hardware is divided into three interconnected electro-mechanical assemblies:

1. **Right Smart Temple (Primary Control & Compute Board)**:
   - Microcontroller / Edge NPU: Espressif ESP32-S3 (Dual-core Xtensa LX7 @ 240MHz + Vector Instructions for AI) or Sub-1.2W Micro-NPU SoC.
   - Power Management: X-Powers AXP2101 PMIC with multi-rail dynamic voltage scaling (0.8V–3.3V).
   - Audio Subsystem: Maxim MAX98357A I2S Class-D amplifier driving an open-ear transducer + Knowles SPU0410HR5H-PB PDM mic.
   - Motion Sensing: Bosch BNO085 9-DoF Intelligent IMU with integrated sensor fusion.
   - Interconnect: 6-pin gold-plated spring-loaded pogo-pin array for high-cycle modular temple swapping.

2. **Bridge Flexible Printed Circuit (FPC Nose & Brow Circuitry)**:
   - High-density polyimide flexible substrate (2-layer FPC) running inside the optical frame bridge.
   - Dual Micro-ISP / Camera Interface (OmniVision OV2640 / OV3660 ultra-compact camera modules).
   - Dual Knowles MSM261D PDM digital microphones positioned for directional beamforming.
   - Ambient Light & Proximity Sensor (Vishay VCNL4040).

3. **Left Modular Temple (Battery & Audio Secondary Module)**:
   - High-Density Lithium-Polymer Cell: 3.85V 300mAh (balanced weight distribution with Right Temple).
   - Battery Protection & Fuel Gauge: TI BQ27441-G1 I2C fuel gauge + DW01A protection IC.
   - Bone-Conduction / Open-Ear Acoustic Driver.
   - Capacitive Multi-Touch Strip (Microchip CAP1208).
   - Gold-plated magnetic charging contacts for TWS-style charging case dock.

---

## 2. 6-Layer Rigid-Flex PCB Stackup Specification

The Smart Temple uses a **6-Layer HDI (High Density Interconnect) Rigid-Flex** construction with blind and buried micro-vias:

| Layer | Type | Copper Thickness | Material | Dielectric Thickness | Target Impedance / Signal Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Top (L1)** | Signal (RF / High Speed) | 1.0 oz (35 µm) | ENIG Gold Finish | 0.075 mm (Prepreg 1080) | 50Ω Single-Ended / 90Ω USB Diff |
| **Inner 1 (L2)** | Ground Plane (Continuous) | 0.5 oz (18 µm) | Low-loss Polyimide | 0.100 mm (FR4 Core) | Solid Low-Noise Ground Reference |
| **Inner 2 (L3)** | High-Speed Digital / MIPI | 0.5 oz (18 µm) | Low-loss Polyimide | 0.100 mm (Prepreg 2116) | 100Ω Diff Pairs (MIPI CSI-2 & I2S) |
| **Inner 3 (L4)** | Power Planes (VCC_3V3, 1V8, 1V2) | 1.0 oz (35 µm) | Copper Foil | 0.100 mm (FR4 Core) | Low-ESR Power Distribution Bus |
| **Inner 4 (L5)** | Ground & Control Signals | 0.5 oz (18 µm) | Low-loss Polyimide | 0.075 mm (Prepreg 1080) | Return current isolation |
| **Bottom (L6)** | Signal / SMD Contact Pads | 1.0 oz (35 µm) | ENIG Gold Finish | Solder Mask 0.020 mm | Battery & Pogo-pin Contact Pads |

**Total Board Thickness**: 0.80 mm ± 0.05 mm  
**Minimum Trace / Space**: 0.075 mm / 0.075 mm (3 mil / 3 mil)  
**Minimum Micro-Via**: 0.10 mm drill / 0.25 mm pad (Laser drilled L1-L2, L5-L6)

---

## 3. Pogo-Pin Interconnect & Signal Pinout

The modular temple hinge incorporates a sealed 6-pin gold spring contact block ($R_{contact} < 15 \text{ m}\Omega$, rated for $>10,000$ mating cycles):

```
+-------------------------------------------------------------+
| PIN 1: VBAT_SYS (3.85V Nom, 1.2A Max Power Delivery Bus)    |
| PIN 2: GND_PWR  (Primary High-Current Ground Return)        |
| PIN 3: I2S_SDATA_L (Left Audio Bone Conduction Channel)     |
| PIN 4: I2C_SDA  (Shared Inter-Temple Sensor & Fuel Gauge)   |
| PIN 5: I2C_SCL  (Shared Inter-Temple Sensor Clock 400kHz)   |
| PIN 6: INT_TOUCH (Capacitive Touch / Hinge Latch Detection)  |
+-------------------------------------------------------------+
```

---

## 4. Complete Bill of Materials (BOM)

| Designator | Component / Part Number | Description | Manufacturer | Package | DigiKey / LCSC Part |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **U1** | ESP32-S3FN8 / ESP32-S3-WROOM-1 | Dual-Core 240MHz MCU + Vector AI, 8MB Flash | Espressif | QFN-56 / LGA | 1965-ESP32-S3FN8-ND |
| **U2** | AXP2101 | Ultra-low Power PMIC, 5 DCDC, 8 LDOs, Li-ion Chg | X-Powers | QFN-40 (5x5mm) | C2838977 |
| **U3** | MAX98357AETE+ | Digital I2S Mono Class-D Audio Amplifier (3.2W) | Analog Devices | TQFN-16 (3x3mm) | MAX98357AETE+-ND |
| **U4** | BNO085 | 9-DoF Orientation Sensor / IMU with Sensor Fusion | CEVA / Bosch | LGA-28 (5.2x3.8mm) | 2082-BNO085-ND |
| **U5** | BQ27441-G1 | System-Side Fuel Gauge with Impedance Track | Texas Instruments | DSBGA-12 (1.6x2.0mm)| 296-30230-1-ND |
| **U6** | CAP1208 | 8-Channel Capacitive Touch Sensor Controller | Microchip | QFN-16 (3x3mm) | CAP1208-1-SL-ND |
| **CAM1** | OV2640-CSP | 2 Megapixel 1/4" CMOS Image Sensor (or OV3660) | OmniVision | Ultra-Compact CSP | C115982 |
| **MIC1, MIC2** | MSM261D4030H1AP | High-SNR (-26dBFS) PDM Digital MEMS Microphone | MEMSensing | SMD 4.0x3.0mm | C2913166 |
| **SPK1** | BST-0815-BC | 15x8x3.5mm Bone-Conduction / Open-Ear Transducer | BeStar | Surface Mount Frame | BST-0815-ND |
| **BAT1** | LP401530-PCM | 3.85V 300mAh LiPo Cell with NTC Thermistor | Renata / EEMB | 4.0x15x30mm | LP401530-PCM |
| **J1, J2** | POGO-6P-1.27MM | 6-Pin Gold-Plated Spring Pogo-Pin Connector Block | Mill-Max | SMD Right-Angle | ED90412-ND |
| **L1..L4** | DFE201610E-1R0M | 1.0µH 2.5A Shielded Power Inductor (PMIC Bucks) | Murata | 0806 (2016 Metric) | 490-13612-1-ND |
| **C1..C48** | 0402/0201 X5R/X7R | Decoupling Ceramic Capacitors (100nF, 1µF, 10µF)| TDK / Yageo | 0402 / 0201 SMD | Generic |

---

## 5. Thermal & Ergonomic Equilibrium Analysis

- **Thermal Throttling Target**: Temple surface temperature facing skin $\le 36.8^\circ \text{C}$ ($< 1.5^\circ \text{C}$ above skin ambient).
- **Thermal Heat-Spreading**: Copper ground thermal via stitching under ESP32-S3 routes heat toward the outer magnesium/titanium frame spine away from the user's temporal bone.
- **Center of Gravity (CoG)**:
  - Right Temple Mass (Electronics + Frame): $14.8 \text{ g}$
  - Left Temple Mass (Battery + Frame + Speaker): $14.6 \text{ g}$
  - Optical Front Frame + Lenses: $18.2 \text{ g}$
  - **Total Weight**: $47.6 \text{ g}$ (Perfect bilateral weight symmetry across the sagittal plane, minimizing ear-bridge pressure fatigue).
