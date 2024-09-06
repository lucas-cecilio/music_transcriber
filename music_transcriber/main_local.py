import os
import librosa
import note_seq
from utils import process_audio, load_model, transcript_audio, download_midi, plot_midi
from inference_model import InferenceModel

# Global variables
SAMPLE_RATE = 16000
AVAILABLE_MODELS = {
    "piano": "ismir2021",
    "multi-instrument": "mt3"
}

# Get the absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SF2_PATH = os.path.join(BASE_DIR, 'mt3', 'SGM-v2.01-Sal-Guit-Bass-V1.3.sf2')


def complete_transcribe(model_type, audio_file):
    '''TODO: Docstring'''
    audio_processed = process_audio(audio_file)
    model = load_model(model_type)
    notes_sequence = transcript_audio(model, audio_processed)
    download_midi(notes_sequence)
    plot_midi(notes_sequence, save_png=True)

def complete_transcribe_terminal():
    # Model selection with validation
    print("\n🤖 Please, select the model (piano or multi-instrument) [piano]: ", end="")
    model_input = input().strip().lower()
    
    # Default to 'piano' if input is empty
    if model_input == "":
        model_input = "piano"
    
    # Loop until a valid model is entered
    while model_input not in AVAILABLE_MODELS:
        print(f"\n⚠️ Invalid model. Please, choose piano or multi-instrument [piano]: ", end="")
        model_input = input().strip().lower()
        
        if model_input == "":  # Default to 'piano' if input is empty
            model_input = "piano"
    
    # Print selected model
    if model_input == 'piano':
        print(f"\nSelected model: {model_input} 🎹")
    elif model_input == 'multi-instrument':
        print(f"\nSelected model: {model_input} 🎶")
    
    # Get the right name to input into model
    model_type = AVAILABLE_MODELS[model_input]
    
    # Audio input
    print("\nPlease, input the audio file name (.wav or .mp3): ", end="")
    audio_file_name = input().strip().lower()
    
    # Check audio format
    while not audio_file_name.endswith(('.wav', '.mp3')):
        print("\n❌ Format not supported, only .wav or .mp3. Try again: ", end="")
        audio_file_name = input().strip().lower()
    
    # Load audio
    audio_path = os.path.join(BASE_DIR, 'input_audio', audio_file_name)
    print('\nLoading audio 🔄')
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    print('\nAudio loaded ✅')
    
    # Initialize model
    print('\nInitializing model 🔄')
    CHECKPOINT_PATH = os.path.join(BASE_DIR, 'checkpoints', model_type)
    model = InferenceModel(CHECKPOINT_PATH, model_type=model_type)
    print('\nModel initialized ✅')

    # Transcript audio
    print('\nTranscripting audio 🔄')
    est_ns = model(audio)
    print('\nTranscription done ✅')

    # Save midi file
    print('\nDownloading midi 🔄')
    midi_output_path = os.path.join(BASE_DIR, 'outputs/midi_file', 'transcribed.mid')
    note_seq.sequence_proto_to_midi_file(est_ns, midi_output_path)
    print('\nThe midi file is ready! ✅')

if __name__ == "__main__":
    # complete_transcribe_terminal()
    # process_audio('piano_chopin_5s.wav')
    # load_model('ismir2021')
    # transcript_audio(load_model('ismir2021'), process_audio('piano_chopin_5s.wav'))
    # download_midi(transcript_audio(load_model('ismir2021'), process_audio('piano_chopin_5s.wav')))
    complete_transcribe('ismir2021', 'piano_chopin_5s.wav')