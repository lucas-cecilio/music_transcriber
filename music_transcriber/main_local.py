import os
import librosa
import note_seq
from selenium import webdriver
from bokeh.io.export import export_png
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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

def process_audio(audio_file: str):
    '''TODO: write docstring'''
    
    # Check audio format
    if not audio_file.endswith(('.wav', '.mp3')):
        print("\n❌ Format not supported, only .wav or .mp3.")
        return None

    audio_path = os.path.join(BASE_DIR, 'audio_files', audio_file)
    print('\nProcessing audio 🔄')
    audio_processed, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    print('\nAudio Processed ✅')
    
    return audio_processed


def load_model(model_type: str):
    ''' TODO: write docstring'''

    checkpoint_path = os.path.join(BASE_DIR, 'checkpoints', model_type)
    print('\nInitializing model 🔄')
    model = InferenceModel(checkpoint_path, model_type=model_type)
    print('\nModel initialized ✅')
    
    return model


def transcript_audio(model, audio_processed):
    '''Transcribes audio to MIDI using the selected model.'''
    
    print('\nTranscripting audio 🔄')
    notes_sequence = model(audio_processed)
    
    print('\nTranscription done ✅')
    return notes_sequence


def download_midi(notes_sequence):
    '''Saves the transcribed MIDI to a file.'''
    
    midi_output_path = os.path.join(BASE_DIR, 'midi_files', 'transcribed_audio.mid')
    
    print('\nDownloading midi 🔄')
    note_seq.sequence_proto_to_midi_file(notes_sequence, midi_output_path)
    
    print('\nThe midi file is ready! ✅')


def plot_midi(notes_sequence, save_png=False):
    '''TODO: write docstring'''
    print('\nCreating a MIDI plot 🔄')
    plot_midi = note_seq.plot_sequence(notes_sequence, show_figure=False)
    
    # Add and adjust title
    plot_midi.title.text = "MIDI"
    plot_midi.title.text_font_size = "20pt"
    plot_midi.title.align = "center"
    
    # Adjust axis labels
    plot_midi.xaxis.axis_label = "Time(s)" 
    plot_midi.yaxis.axis_label = "Pitch Notes"
    plot_midi.xaxis.axis_label_text_font_size = "16pt"
    plot_midi.yaxis.axis_label_text_font_size = "16pt"  
    
    # Adjust the size of tick labels
    plot_midi.xaxis.major_label_text_font_size = "14pt" 
    plot_midi.yaxis.major_label_text_font_size = "14pt" 
    
    if save_png:
        # Disable toolbar and change dimensions
        plot_midi.toolbar_location = None  # Remove the toolbar
        plot_midi.width = 1600  # Increase width for higher quality
        plot_midi.height = 900  # Increase height for higher quality
        
        print('\nSaving a png of MIDI plot 📥')
        save_plot_midi(plot_midi)
        
    print('\nMIDI plot done ✅')
    return plot_midi
    
def save_plot_midi(plot_midi):
    '''TODO: write docstring'''
    plot_midi_file = os.path.join(BASE_DIR, 'plot_files', 'plot_midi.png')
    # Configure Chrome driver in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Export the figure as a high-quality PNG
    export_png(plot_midi, filename=plot_midi_file, webdriver=driver)

    # Close the Chrome driver
    driver.quit()


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
    audio_path = os.path.join(BASE_DIR, 'audio_files', audio_file_name)
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
    midi_output_path = os.path.join(BASE_DIR, 'midi_files', 'transcribed_main_local.mid')
    note_seq.sequence_proto_to_midi_file(est_ns, midi_output_path)
    print('\nThe midi file is ready! ✅')

if __name__ == "__main__":
    # complete_transcribe_terminal()
    # process_audio('piano_chopin_5s.wav')
    # load_model('ismir2021')
    # transcript_audio(load_model('ismir2021'), process_audio('piano_chopin_5s.wav'))
    # download_midi(transcript_audio(load_model('ismir2021'), process_audio('piano_chopin_5s.wav')))
    complete_transcribe('ismir2021', 'piano_chopin_5s.wav')