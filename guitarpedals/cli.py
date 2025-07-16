import argparse
import os
import soundfile as sf
import librosa

from .dsp import (
    normalize,
    low_pass,
    oversample,
    downsample,
    convolution_reverb,
    save_waveform_plot,
)

from .generate import generate_riff
from .simulate import simulate_circuit
from .dsp import normalize, low_pass, oversample, downsample, convolution_reverb
from .circuits import (
    fuzz_circuit,
    overdrive_circuit,
    two_stage_fuzz_circuit,
    three_stage_fuzz_circuit,
    tone_stack_fuzz_circuit,
    save_circuit_schematic,
)

CIRCUITS = {
    "fuzz": fuzz_circuit,
    "overdrive": overdrive_circuit,
    "two_stage_fuzz": two_stage_fuzz_circuit,
    "three_stage_fuzz": three_stage_fuzz_circuit,
    "tone_stack_fuzz": tone_stack_fuzz_circuit,
}


def load_audio(path):
    data, sr = sf.read(path)
    return data, sr


def main(argv=None):
    parser = argparse.ArgumentParser(description="Guitar pedal simulations")
    parser.add_argument(
        "--outdir",
        default="outputs",
        help="Directory to place generated files",
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a test riff")
    gen.add_argument("--duration", type=float, default=4.0, help="Length of riff in seconds")
    gen.add_argument("--midi-file", help="Render this MIDI file instead of the default riff")
    gen.add_argument("--random-melody", action="store_true", help="Generate a random melody")
    gen.add_argument("--random-chords", action="store_true", help="Generate random chords")

    sim = sub.add_parser("simulate", help="Simulate a circuit on an audio file")
    sim.add_argument("--input", help="Input WAV file")
    sim.add_argument("--midi", help="MIDI file to render and use as input")
    sim.add_argument("--duration", type=float, default=4.0, help="Length of generated riff if no input file")
    sim.add_argument("--random-melody", action="store_true", help="Generate a random melody")
    sim.add_argument("--random-chords", action="store_true", help="Generate random chords")
    sim.add_argument("--circuit", choices=list(CIRCUITS), default="fuzz", help="Circuit to simulate")
    sim.add_argument("--output", help="Output WAV file")
    sim.add_argument("--reverb-ir", help="Impulse response WAV for convolution reverb")
    sim.add_argument("--oversample", type=int, default=1, help="Oversampling factor")

    args = parser.parse_args(argv)
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    if args.command == "generate":
        filename = os.path.join(outdir, "riff.wav")
        audio, _ = generate_riff(
            filename=filename,
            midi_file=args.midi_file,
            duration=args.duration,
            random_melody=args.random_melody,
            random_chords=args.random_chords,
        )
        save_waveform_plot(audio, os.path.join(outdir, "riff_waveform.png"), "Generated Riff")
        return

    if args.command == "simulate":
        if args.midi or args.random_melody or args.random_chords or not args.input:
            input_path = args.input or os.path.join(outdir, "riff.wav")
            audio, fs = generate_riff(
                filename=input_path,
                midi_file=args.midi,
                duration=args.duration,
                random_melody=args.random_melody,
                random_chords=args.random_chords,
            )
        else:
            input_path = args.input
            if not os.path.exists(input_path):
                parser.error(f"Input file '{input_path}' not found")
            audio, fs = load_audio(input_path)

        save_waveform_plot(audio, os.path.join(outdir, "input_waveform.png"), "Input Riff")
        circuit = CIRCUITS[args.circuit]()
        save_circuit_schematic(circuit, os.path.join(outdir, f"{circuit.title.lower()}_schematic.png"))

        if args.oversample > 1:
            audio = oversample(audio, args.oversample)
            fs *= args.oversample

        y = simulate_circuit(circuit, audio, fs)

        if args.oversample > 1:
            y = downsample(y, args.oversample)

        if args.reverb_ir:
            ir, ir_fs = load_audio(args.reverb_ir)
            if ir_fs != fs:
                ir = librosa.resample(ir, orig_sr=ir_fs, target_sr=fs)
            y = convolution_reverb(y, ir)

        output_path = args.output or os.path.join(outdir, "out.wav")
        y = normalize(low_pass(y, fs))
        sf.write(output_path, y, fs)
        save_waveform_plot(y, os.path.join(outdir, "output_waveform.png"), f"{circuit.title} Output")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
