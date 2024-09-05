import os
import librosa
import note_seq
from inference_model import InferenceModel

# import nest_asyncio
# nest_asyncio.apply()

# Variables
SAMPLE_RATE = 16000
AVAILABLE_MODELS = {
    "piano": "ismir2021",
    "multi-instrument": "mt3"
}

# Get the absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SF2_PATH = os.path.join(BASE_DIR, 'mt3', 'SGM-v2.01-Sal-Guit-Bass-V1.3.sf2')


def main():
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
    MODEL = AVAILABLE_MODELS[model_input]
    
    # Audio input
    print("\nPlease, input the audio file name (.wav or .mp3): ", end="")
    audio_file_name = input().strip().lower()
    
    # Check audio format
    while not audio_file_name.endswith(('.wav', '.mp3')):
        print("\n❌ Format not supported, only .wav or .mp3. Try again: ", end="")
        audio_file_name = input().strip().lower()
    
    # Load audio
    audio_path = os.path.join(BASE_DIR, 'audio_files', audio_file_name)
    print('\nLoading audio 🔃')
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    print('\nAudio loaded ✅')
    
    # Initialize model
    print('\nInitializing model 🔃')
    CHECKPOINT_PATH = os.path.join(BASE_DIR, 'checkpoints', MODEL)
    model = InferenceModel(CHECKPOINT_PATH, model_type=MODEL)
    print('\nModel initialized ✅')

    # Transcript audio
    print('\nTranscripting audio 🔃')
    est_ns = model(audio)
    print('\nTranscription done ✅')

    # Save midi file
    print('\nDownloading midi 🔃')
    midi_output_path = os.path.join(BASE_DIR, 'midi_files', 'transcribed_main_local.mid')
    note_seq.sequence_proto_to_midi_file(est_ns, midi_output_path)
    print('\nThe midi file is ready! ✅')

    # Play midi sequence
    # note_seq.play_sequence(est_ns, synth=note_seq.fluidsynth,
    #                        sample_rate=SAMPLE_RATE, sf2_path=SF2_PATH)

    # # Plot midi sequence
    # note_seq.plot_sequence(est_ns)

if __name__ == "__main__":
    main()