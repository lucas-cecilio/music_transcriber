import librosa
import note_seq
import subprocess
import collections
import pandas as pd 
import numpy as np

from pathlib import Path
from midi2audio import FluidSynth
from music_transcriber.inference_model import InferenceModel
from music_transcriber.params import *


def process_audio(audio_file: str):
    '''TODO: write docstring'''
    
    # Check audio format
    if not audio_file.endswith(('.wav', '.mp3')):
        print("\n❌ Format not supported, only .wav or .mp3.")
        return None

    audio_file_name = str(Path(audio_file).stem)
    audio_file_path = INPUT_AUDIO_PATH / audio_file
    
    print('\nProcessing audio 🔄')
    audio_processed, _ = librosa.load(audio_file_path, sr=SAMPLE_RATE)
    print('\nAudio Processed ✅')
    
    return audio_processed, audio_file_name


def load_model(model_type: str):
    ''' TODO: write docstring'''

    print('\nInitializing model 🔄')
    checkpoint_model_path = os.path.join(CHECKPOINT_PATH, model_type)
    model = InferenceModel(checkpoint_path=checkpoint_model_path, model_type=model_type)
    print('\nModel initialized ✅')
    
    return model


def transcribe_audio(model, audio_processed):
    '''Transcribes audio to MIDI using the selected model.'''
    
    print('\nTranscripting audio 🔄')
    notes_sequence = model(audio_processed)
    
    print('\nTranscription done ✅')
    return notes_sequence


def download_midi(notes_sequence, audio_file_name):
    '''Saves the transcribed MIDI to a file.'''
    
    print('\nDownloading midi 🔄')
    midi_file_name = str(Path(audio_file_name).stem) + '_transcribed.mid'
    midi_file_path = str(OUTPUT_MIDI_FILE_PATH / midi_file_name)
    note_seq.sequence_proto_to_midi_file(notes_sequence, midi_file_path)
    
    print('\nThe midi file is ready! ✅')
    return midi_file_name, midi_file_path

def midi_to_audio(midi_file_name: str, midi_file_path: str):
    '''TODO: Write docstring'''
    print('\nDownloading transcribed audio 🔄')
    
    midi_audio_name = str(Path(midi_file_name).with_suffix(".wav"))
    midi_audio_path = str(OUTPUT_MIDI_AUDIO_PATH / midi_audio_name)
    
    fs = FluidSynth(sound_font=SF2_PATH, sample_rate=SAMPLE_RATE)
    fs.midi_to_audio(midi_file_path, midi_audio_path)
    
    print('\nThe transcribed audio is ready! ✅')
    
    return midi_audio_path

def midi_to_score(midi_file_name: str, midi_file_path: str):
    """ TODO: Docstring"""
    
    print('\nCreating a music score 🔄')

    midi_score_name = str(Path(midi_file_name).stem).replace("_transcribed", "")
    midi_score_xml_path = str(OUTPUT_MIDI_SCORE_PATH / Path(midi_file_name).with_suffix(".xml"))
    midi_score_pdf_path = str(OUTPUT_MIDI_SCORE_PATH / Path(midi_file_name).with_suffix(".pdf"))
  
    # Convert MIDI to MusicXML
    subprocess.run(["musescore", midi_file_path, "-o", midi_score_xml_path])

    # Edit the MusicXML file to add a title and subtitle
    with open(midi_score_xml_path, "r", encoding="utf-8") as xml_file:
        xml_data = xml_file.read()

    # Insert title and subtitle into the MusicXML in a more robust way
    if "<work-title>" in xml_data:
        # Replace existing <work-title> if found
        new_xml_data = xml_data.replace(
            "<work-title></work-title>",  # Insert the title where it's found empty
            f"<work-title>Transcription of {midi_score_name} made with Music Transcriber</work-title>"
        )
    else:
        # Insert title if not present, adding it after the opening <score-partwise> tag
        new_xml_data = xml_data.replace(
            "<score-partwise", 
            f"<score-partwise>\n<work>\n<work-title>Transcription of {midi_score_name} made with Music Transcriber</work-title></work>"
        )

    # Save the modified MusicXML temporarily
    with open(midi_score_xml_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(new_xml_data)

    # Convert the modified MusicXML to PDF
    subprocess.run(["musescore", midi_score_xml_path, "-o", midi_score_pdf_path])

    # Remove the temporary XML file
    if os.path.exists(midi_score_xml_path):
        os.remove(midi_score_xml_path)

    print(f"Score successfully generated ✅")
    
    return midi_score_pdf_path

def sequence_to_dict(notes_sequence):
    """Generates a pandas dataframe from a sequence."""
    notes_dict = collections.defaultdict(list)
    for note in notes_sequence.notes:
      notes_dict['start_time'].append(note.start_time)
      notes_dict['end_time'].append(note.end_time)
      notes_dict['duration'].append(note.end_time - note.start_time)
      notes_dict['pitch'].append(note.pitch)
      notes_dict['bottom'].append(note.pitch - 0.4)
      notes_dict['top'].append(note.pitch + 0.4)
      notes_dict['velocity'].append(note.velocity)
      notes_dict['fill_alpha'].append(note.velocity / 128.0)
      notes_dict['instrument'].append(note.instrument)
      notes_dict['program'].append(note.program)

    # If no velocity differences are found, set alpha to 1.0.
    if np.max(notes_dict['velocity']) == np.min(notes_dict['velocity']):
      notes_dict['fill_alpha'] = [1.0] * len(notes_dict['fill_alpha'])

    return dict(notes_dict)
    
def sequence_to_pandas_dataframe(notes_sequence):
    """Generates a pandas dataframe from a sequence."""
    notes_dict = sequence_to_dict(notes_sequence)
    
    return pd.DataFrame(notes_dict)