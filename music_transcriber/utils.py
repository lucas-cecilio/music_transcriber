import os
import librosa
import note_seq

from midi2audio import FluidSynth
from selenium import webdriver
from bokeh.io.export import export_png
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from music_transcriber.inference_model import InferenceModel
from music_transcriber.params import *


def process_audio(audio_file: str):
    '''TODO: write docstring'''
    
    # Check audio format
    if not audio_file.endswith(('.wav', '.mp3')):
        print("\n❌ Format not supported, only .wav or .mp3.")
        return None

    audio_path = os.path.join(BASE_DIR, 'input_audio', audio_file)
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


def transcribe_audio(model, audio_processed):
    '''Transcribes audio to MIDI using the selected model.'''
    
    print('\nTranscripting audio 🔄')
    notes_sequence = model(audio_processed)
    
    print('\nTranscription done ✅')
    return notes_sequence


def download_midi(notes_sequence):
    '''Saves the transcribed MIDI to a file.'''
    
    midi_file_path = os.path.join(BASE_DIR, 'outputs', 'midi_file', 'transcribed.mid')
    
    print('\nDownloading midi 🔄')
    note_seq.sequence_proto_to_midi_file(notes_sequence, midi_file_path)
    
    print('\nThe midi file is ready! ✅')

def midi_to_audio():
    '''TODO: Write docstring'''
    print('\nDownloading transcribed audio 🔄')
    
    midi_file_path = os.path.join(BASE_DIR, 'outputs', 'midi_file', 'transcribed.mid')
    midi_audio_path = os.path.join(BASE_DIR, 'outputs', 'midi_audio', 'transcribed_audio.wav')
    fs = FluidSynth(sound_font=SF2_PATH, sample_rate=SAMPLE_RATE)
    fs.midi_to_audio(midi_file_path, midi_audio_path)
    
    print('\nThe transcribed audio is ready! ✅')


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
    midi_plot_path = os.path.join(BASE_DIR, 'outputs', 'midi_plot', 'plot.png')
    # Configure Chrome driver in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Export the figure as a high-quality PNG
    export_png(plot_midi, filename=midi_plot_path, webdriver=driver)

    # Close the Chrome driver
    driver.quit()