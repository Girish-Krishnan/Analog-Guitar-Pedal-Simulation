import argparse
import os
import soundfile as sf
import librosa

from .generate import generate_riff
from .simulate import simulate_circuit
from .dsp import normalize, low_pass, oversample, downsample, convolution_reverb
from .circuits import (
    fuzz_circuit,
    overdrive_circuit,
    two_stage_fuzz_circuit,
    save_circuit_schematic,
)

CIRCUITS = {
    "fuzz": fuzz_circuit,
    "overdrive": overdrive_circuit,
    "two_stage_fuzz": two_stage_fuzz_circuit,
}


def load_audio(path):
    data, sr = sf.read(path)
    return data, sr


def main(argv=None):
    parser = argparse.ArgumentParser(description="Guitar pedal simulations")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a test riff")
    gen.add_argument("--duration", type=float, default=4.0, help="Length of riff in seconds")

    sim = sub.add_parser("simulate", help="Simulate a circuit on an audio file")
    sim.add_argument("--input", default="outputs/riff.wav", help="Input WAV file")
    sim.add_argument("--circuit", choices=list(CIRCUITS), default="fuzz", help="Circuit to simulate")
    sim.add_argument("--output", default="outputs/out.wav", help="Output WAV file")
    sim.add_argument("--reverb-ir", help="Impulse response WAV for convolution reverb")
    sim.add_argument("--oversample", type=int, default=1, help="Oversampling factor")

    args = parser.parse_args(argv)

    if args.command == "generate":
        os.makedirs("outputs", exist_ok=True)
        generate_riff(duration=args.duration)
        return

    if args.command == "simulate":
        if not os.path.exists(args.input):
            parser.error(f"Input file '{args.input}' not found")
        audio, fs = load_audio(args.input)
        circuit = CIRCUITS[args.circuit]()
        save_circuit_schematic(circuit, f"outputs/{circuit.title.lower()}_schematic.png")

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

        y = normalize(low_pass(y, fs))
        sf.write(args.output, y, fs)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
