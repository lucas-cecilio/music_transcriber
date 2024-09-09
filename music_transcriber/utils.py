import librosa
import note_seq
import subprocess

from pathlib import Path
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

    audio_path = INPUT_AUDIO_PATH / audio_file
    
    print('\nProcessing audio 🔄')
    audio_processed, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    print('\nAudio Processed ✅')
    
    return audio_processed


def load_model(model_type: str):
    ''' TODO: write docstring'''

    checkpoint_model_path = os.path.join(CHECKPOINT_PATH, model_type)
    print('\nInitializing model 🔄')
    
    model = InferenceModel(checkpoint_path=checkpoint_model_path, model_type=model_type)
    print('\nModel initialized ✅')
    
    return model


def transcribe_audio(model, audio_processed):
    '''Transcribes audio to MIDI using the selected model.'''
    
    print('\nTranscripting audio 🔄')
    notes_sequence = model(audio_processed)
    
    print('\nTranscription done ✅')
    return notes_sequence


def download_midi(notes_sequence, midi_file_name):
    '''Saves the transcribed MIDI to a file.'''
    
    midi_file_path = OUTPUT_MIDI_FILE_PATH / midi_file_name
    
    print('\nDownloading midi 🔄')
    note_seq.sequence_proto_to_midi_file(notes_sequence, midi_file_path)
    
    print('\nThe midi file is ready! ✅')
    
def plot_midi(notes_sequence, midi_plot_name, save_png=True):
    '''TODO: write docstring'''
    
    print('\nCreating a MIDI plot 🔄')
    plot_midi = note_seq.plot_sequence(notes_sequence, show_figure=False)
    midi_plot_path = OUTPUT_MIDI_PLOT_PATH / midi_plot_name
    
    # Add and adjust title
    plot_midi.title.text = f'MIDI sequence of {str(midi_plot_name).replace(".png", "")}'
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
        save_plot_midi(plot_midi, midi_plot_path)
        
    print('\nMIDI plot done ✅')
    return plot_midi
    
def save_plot_midi(plot_midi, midi_plot_path):
    '''TODO: write docstring'''

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

def midi_to_audio(midi_filename: str):
    '''TODO: Write docstring'''
    print('\nDownloading transcribed audio 🔄')
    
    midi_file_path = os.path.join(BASE_DIR, 'outputs', 'midi_file', midi_filename)
    midi_audio_path = os.path.join(BASE_DIR, 'outputs', 'midi_audio', f'{midi_filename.replace(".mid", "")}_audio.wav')
    fs = FluidSynth(sound_font=SF2_PATH, sample_rate=SAMPLE_RATE)
    fs.midi_to_audio(midi_file_path, midi_audio_path)
    
    print('\nThe transcribed audio is ready! ✅')

def midi_to_score(midi_filename: str):
    """ TODO: Docstring"""
    
    print('\nCreating a music score 🔄')
    
    # Define relative paths
    midi_path = os.path.join("outputs", "midi_file", midi_filename)
    output_xml_path = os.path.join("outputs", "midi_score", midi_filename.replace(".mid", ".xml"))
    output_pdf_path = os.path.join("outputs", "midi_score", midi_filename.replace(".mid", ".pdf"))

    # Check if the MIDI file exists
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"The file {midi_path} was not found.")

    # Convert MIDI to MusicXML
    subprocess.run(["mscore", midi_path, "-o", output_xml_path])

    # Edit the MusicXML file to add a title and subtitle
    with open(output_xml_path, "r", encoding="utf-8") as xml_file:
        xml_data = xml_file.read()

    # Title (based on the MIDI file name)
    # title = midi_filename.replace(".mid", "")

    # Insert title and subtitle into the MusicXML in a more robust way
    if "<work-title>" in xml_data:
        # Replace existing <work-title> if found
        new_xml_data = xml_data.replace(
            "<work-title></work-title>",  # Insert the title where it's found empty
            f"<work-title>Transcription made with Music Transcriber</work-title>"
        )
    else:
        # Insert title if not present, adding it after the opening <score-partwise> tag
        new_xml_data = xml_data.replace(
            "<score-partwise", 
            f"<score-partwise>\n<work>\n<work-title>Transcription made with Music Transcriber</work-title></work>"
        )

    # Save the modified MusicXML temporarily
    with open(output_xml_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(new_xml_data)

    # Convert the modified MusicXML to PDF
    subprocess.run(["mscore", output_xml_path, "-o", output_pdf_path])

    # Remove the temporary XML file
    if os.path.exists(output_xml_path):
        os.remove(output_xml_path)

    print(f"Score successfully generated ✅")



    