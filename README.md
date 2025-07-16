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

Use the provided command line interface to generate a test riff or render your
own MIDI file:

```bash
python -m guitarpedals.cli generate --midi-file my_riff.mid
```
You can also pass `--random-melody` or `--random-chords` to create a simple
random riff on the fly.

Then process the riff with one of the available circuits, for example:

```bash
python -m guitarpedals.cli simulate --circuit two_stage_fuzz --oversample 2
```

By default this writes the processed audio to `outputs/out.wav`, saves a schematic image and waveform plots and optionally applies convolution reverb with `--reverb-ir path/to/impulse.wav`. Use `--outdir DIR` to choose a different location for generated files.

### Command-line arguments

| Argument | Applies To | Description |
|----------|------------|-------------|
| `--outdir DIR` | both | Output directory for generated files |
| `generate --duration SECONDS` | `generate` | Length of generated riff |
| `generate --midi-file PATH` | `generate` | Render this MIDI file instead of a built-in riff |
| `generate --random-melody` | `generate` | Generate a random melody |
| `generate --random-chords` | `generate` | Generate random chords |
| `simulate --input PATH` | `simulate` | Input WAV file (defaults to `outdir/riff.wav`) |
| `simulate --midi PATH` | `simulate` | MIDI file to render and process |
| `simulate --duration SECONDS` | `simulate` | Length when generating riff if no input WAV |
| `simulate --random-melody` | `simulate` | Generate a random melody |
| `simulate --random-chords` | `simulate` | Generate random chords |
| `simulate --circuit {fuzz,overdrive,two_stage_fuzz}` | `simulate` | Circuit model to apply |
| `simulate --output PATH` | `simulate` | Output WAV file name |
| `simulate --reverb-ir PATH` | `simulate` | Impulse response WAV for convolution reverb |
| `simulate --oversample N` | `simulate` | Oversampling factor before simulation |

## Expected Results

After running `python -m guitarpedals.cli simulate`, the chosen output directory (default `outputs`) will contain:

- `riff.wav` – the clean, generated guitar riff
- `out.wav` – the riff processed by the selected circuit
- `<circuit>_schematic.png` – schematic diagram of the chosen circuit
- `riff_waveform.png` – plot of the generated riff
- `output_waveform.png` – plot of the circuit output

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
outputs/              # Default directory for results
```

Enjoy experimenting with analog-inspired guitar tones in the digital domain!
