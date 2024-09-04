import os
import librosa
import note_seq
from inference_model import InferenceModel

# import nest_asyncio
# nest_asyncio.apply()

# Variables
SAMPLE_RATE = 16000
MODEL = "ismir2021"

# Get the absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SF2_PATH = os.path.join(BASE_DIR, 'mt3', 'SGM-v2.01-Sal-Guit-Bass-V1.3.sf2')
CHECKPOINT_PATH = os.path.join(BASE_DIR, 'checkpoints', MODEL)


def main():
    # Initialize model
    print('Initializing model 🔃')
    model = InferenceModel(CHECKPOINT_PATH, model_type=MODEL)
    print('Model initialized ✔')

    # Load audio
    audio_path = os.path.join(BASE_DIR, 'audio_files', 'chopin_30s.wav')
    print('Loading audio 🔃')
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    print('Audio loaded ✔')

    # Transcript audio
    print('Transcripting audio 🔃')
    est_ns = model(audio)
    print('Transcription done ✔')

    # Save midi file
    print('Downloading midi 🔃')
    midi_output_path = os.path.join(BASE_DIR, 'midi_files', 'transcribed_main_local.mid')
    note_seq.sequence_proto_to_midi_file(est_ns, midi_output_path)
    print('The midi file is ready! ✔')

    # Play midi sequence
    # note_seq.play_sequence(est_ns, synth=note_seq.fluidsynth,
    #                        sample_rate=SAMPLE_RATE, sf2_path=SF2_PATH)

    # # Plot midi sequence
    # note_seq.plot_sequence(est_ns)

if __name__ == "__main__":
    main()




