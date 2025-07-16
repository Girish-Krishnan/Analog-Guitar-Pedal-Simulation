import pretty_midi
import numpy as np
import soundfile as sf


def generate_riff(filename='riff.wav', midi_file=None, instrument_name='Electric Guitar (jazz)', duration=4.0, fs=44100):
    """Generate a simple guitar riff and render to wav using FluidSynth."""
    if midi_file:
        pm = pretty_midi.PrettyMIDI(midi_file)
    else:
        pm = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(instrument_name))
        t = np.linspace(0, duration, 8)
        pitches = [40, 43, 47, 52, 55, 52, 47, 43]
        start = 0
        for pitch, end in zip(pitches, t[1:]):
            note = pretty_midi.Note(velocity=100, pitch=pitch, start=start, end=end)
            instrument.notes.append(note)
            start = end
        pm.instruments.append(instrument)
    audio = pm.fluidsynth(fs=fs)
    sf.write(filename, audio, fs)
    return audio, fs
