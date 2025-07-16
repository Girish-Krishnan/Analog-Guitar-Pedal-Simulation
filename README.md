# Analog Guitar Pedal Simulation

This project demonstrates how to combine analog circuit simulation using **PySpice** with basic digital signal processing to explore how classic guitar pedals shape audio signals. It generates short guitar riffs (or you can supply your own MIDI file), runs the audio through simulated circuits like fuzz or overdrive, and outputs the processed sound as a WAV file along with plots of the resulting waveform.

## Features

- Generation of simple guitar riffs with [PrettyMIDI](https://github.com/craffel/pretty-midi) and FluidSynth
- PySpice transient simulation of example fuzz and overdrive circuits
- Basic DSP filtering and normalization
- Output WAV files and waveform plots for easy listening and inspection

## Installation

1. Create a Python 3 environment (Python 3.8+ recommended).
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

PySpice depends on **ngspice**. On many systems it can be installed via a package manager (e.g. `apt-get install ngspice`). Rendering MIDI to audio requires the optional `pyfluidsynth` package and an installed FluidSynth library.

## Usage

Use the provided command line interface to generate a test riff:

```bash
python -m guitarpedals.cli generate
```

Then process the riff with one of the available circuits, for example:

```bash
python -m guitarpedals.cli simulate --circuit twostagefuzz --oversample 2
```

This writes the processed audio to `outputs/out.wav`, saves a schematic image and optionally applies convolution reverb with `--reverb-ir path/to/impulse.wav`.

## Expected Results

After running `python -m guitarpedals.cli simulate`, the `outputs` directory will contain:

- `riff.wav` – the clean, generated guitar riff
- `out.wav` – the riff processed by the selected circuit
- `<circuit>_schematic.png` – schematic diagram of the chosen circuit

Listen to the WAV files and open the plot image to observe how the analog circuit model affects the waveform.

## Directory Structure

```
src/
  guitarpedals/
    __init__.py
    circuits.py      # PySpice circuit definitions
    dsp.py           # DSP helper functions
    generate.py      # Guitar riff generation
    cli.py           # Command line interface
outputs/              # Created automatically for results
```

Enjoy experimenting with analog-inspired guitar tones in the digital domain!
