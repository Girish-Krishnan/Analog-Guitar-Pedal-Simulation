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

Run the main simulation script:

```bash
python -m guitarpedals.simulate
```

This will:

1. Generate a short guitar riff and save it to `outputs/riff.wav`.
2. Simulate the fuzz pedal circuit and create `outputs/fuzz.wav`.
3. Plot the first part of the resulting waveform to `outputs/fuzz_waveform.png`.

You can modify the code in `guitarpedals/generate.py` to load your own MIDI file or adjust the riff generation parameters.

## Expected Results

After running `python -m guitarpedals.simulate`, the `outputs` directory will contain:

- `riff.wav` – the clean, generated guitar riff
- `fuzz.wav` – the same riff processed by the fuzz pedal simulation
- `fuzz_waveform.png` – plot of the first few milliseconds of the processed audio

Listen to the WAV files and open the plot image to observe how the analog circuit model affects the waveform.

## Directory Structure

```
src/
  guitarpedals/
    __init__.py
    circuits.py      # PySpice circuit definitions
    dsp.py           # DSP helper functions
    generate.py      # Guitar riff generation
    simulate.py      # Main script to run simulation
outputs/              # Created automatically for results
```

Enjoy experimenting with analog-inspired guitar tones in the digital domain!
