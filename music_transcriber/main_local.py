import os
import librosa
import note_seq
from utils import *
from params import *
from inference_model import InferenceModel

def complete_transcribe(model_type, audio_file):
    '''TODO: Docstring'''
    audio_processed, audio_file_name = process_audio(audio_file)
    model = load_model(model_type)
    notes_sequence = transcribe_audio(model, audio_processed)
    midi_file_name, midi_file_path = download_midi(notes_sequence, audio_file_name)
    # midi_plot_path, _, _ = plot_midi(notes_sequence, midi_file_name, save_png=True)
    midi_audio_path = midi_to_audio(midi_file_name, midi_file_path)
    midi_score_pdf_path = midi_to_score(midi_file_name, midi_file_path)
    

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
    audio_path = os.path.join(BASE_PATH, 'input_audio', audio_file_name)
    print('\nLoading audio 🔄')
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    print('\nAudio loaded ✅')
    
    # Initialize model
    print('\nInitializing model 🔄')
    CHECKPOINT_PATH = os.path.join(BASE_PATH, 'checkpoints', model_type)
    model = InferenceModel(CHECKPOINT_PATH, model_type=model_type)
    print('\nModel initialized ✅')

    # Transcript audio
    print('\nTranscripting audio 🔄')
    est_ns = model(audio)
    print('\nTranscription done ✅')

    # Save midi file
    print('\nDownloading midi 🔄')
    midi_output_path = os.path.join(BASE_PATH, 'outputs/midi_file', 'transcribed.mid')
    note_seq.sequence_proto_to_midi_file(est_ns, midi_output_path)
    print('\nThe midi file is ready! ✅')

if __name__ == "__main__":
    complete_transcribe('ismir2021', 'piano_chopin_5s.wav')