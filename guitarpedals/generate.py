import pretty_midi
import numpy as np
import soundfile as sf


def generate_riff(
    filename="riff.wav",
    midi_file=None,
    instrument_name="Electric Guitar (jazz)",
    duration=4.0,
    fs=44100,
    random_melody=False,
    random_chords=False,
):
    """Generate a guitar riff or render a provided MIDI file.

    The ``random_melody`` and ``random_chords`` options create simple random
    sequences for a bit more variety when no MIDI file is supplied.
    """

    if midi_file:
        pm = pretty_midi.PrettyMIDI(midi_file)
    else:
        pm = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(
            program=pretty_midi.instrument_name_to_program(instrument_name)
        )

        if random_chords:
            times = np.linspace(0, duration, 5)
            for start, end in zip(times[:-1], times[1:]):
                root = np.random.randint(40, 55)
                chord = [root, root + 4, root + 7]
                for pitch in chord:
                    note = pretty_midi.Note(
                        velocity=100, pitch=pitch, start=start, end=end
                    )
                    instrument.notes.append(note)
        elif random_melody:
            times = np.linspace(0, duration, 9)
            for start, end in zip(times[:-1], times[1:]):
                pitch = np.random.randint(40, 60)
                note = pretty_midi.Note(
                    velocity=100, pitch=pitch, start=start, end=end
                )
                instrument.notes.append(note)
        else:
            t = np.linspace(0, duration, 8)
            pitches = [40, 43, 47, 52, 55, 52, 47, 43]
            start = 0
            for pitch, end in zip(pitches, t[1:]):
                note = pretty_midi.Note(
                    velocity=100, pitch=pitch, start=start, end=end
                )
                instrument.notes.append(note)
                start = end

        pm.instruments.append(instrument)

    audio = pm.fluidsynth(fs=fs)
    if filename:
        sf.write(filename, audio, fs)
    return audio, fs
