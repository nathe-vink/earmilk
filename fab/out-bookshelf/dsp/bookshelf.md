# DSP starting point: the bookshelf

Amplifier: Hypex FusionAmp FA122. Channels: CH1 woofer, SB17NRX2C35-8; CH2 tweeter, Illuminator D3004/602200.

| | woofer | tweeter |
|---|---|---|
| acoustic centre behind the front (mm) | 32 | 91 |
| delay (ms) | 0.173 | 0.0 |
| sensitivity, 2.83 V (dB) | 87.0 | 90.5 |
| gain to start (dB) | 0.0 | -3.5 |

Crossovers: woofer-tweeter 2400 Hz, Linkwitz-Riley 24 dB/octave.

Woofer EQ: [{"type": "linkwitz-transform", "from_fc_hz": 72.6, "from_q": 0.83, "to_f0_hz": 45.0, "to_q": 0.707, "low_shelf_db": 8.3, "why": "the sealed box's corner moved down to 45 Hz (fab/acoustics.py)"}]

The waveguide's on-axis level against its level at the crossover (from the simulation): 1600 Hz -2.6 dB, 2500 Hz +0.0 dB, 4000 Hz -3.8 dB, 6300 Hz -3.8 dB, 10000 Hz -6.4 dB. Flatten it with a shelf after measuring.

Workflow: (1) Load the channels and the crossovers in Hypex Filter Design (Windows), USB to the amplifier. (2) Measure each driver alone at 1 m on the tweeter axis (REW, UMIK-1), gated. (3) Set levels and delays from the measurements (these numbers are where to start). (4) Check the summed response and the reverse-null at each crossover, then EQ the system flat on axis. (5) Save to the amplifier; it stays silent until a filter is loaded.
