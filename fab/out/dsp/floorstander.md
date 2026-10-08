# DSP starting point: the floorstander

Amplifier: Hypex FusionAmp FA253. Channels: CH1 woofer, Dayton Audio RSS315HF-4 (Reference HF subwoofer, 12 in); CH2 mid, SB Acoustics Satori MR16P-8 (6.5 in dedicated midrange, papyrus); CH3 tweeter, Satori TW29DN-B (faceplate removed).

| | woofer | mid | tweeter |
|---|---|---|---|
| acoustic centre behind the front (mm) | 53 | 32 | 172 |
| delay (ms) | 0.347 | 0.407 | 0.0 |
| sensitivity, 2.83 V (dB) | 90.3 | 88.0 | 96.5 |
| gain to start (dB) | -2.3 | 0.0 | -8.5 |

Crossovers: woofer-mid 300 Hz; mid-tweeter 2800 Hz, Linkwitz-Riley 24 dB/octave.

Woofer EQ: [{"type": "peaking", "f_hz": 37.0, "gain_db": -3.3, "q": 1.2, "why": "the vented alignment's bump (fab/research/drivers-floorstander.md)"}]

The waveguide's on-axis level against its level at the crossover (from the simulation): 1250 Hz -2.8 dB, 2000 Hz +1.6 dB, 3150 Hz +0.0 dB, 5000 Hz -2.0 dB, 8000 Hz -5.3 dB. Flatten it with a shelf after measuring.

Workflow: (1) Load the channels and the crossovers in Hypex Filter Design (Windows), USB to the amplifier. (2) Measure each driver alone at 1 m on the tweeter axis (REW, UMIK-1), gated. (3) Set levels and delays from the measurements (these numbers are where to start). (4) Check the summed response and the reverse-null at each crossover, then EQ the system flat on axis. (5) Save to the amplifier; it stays silent until a filter is loaded.
