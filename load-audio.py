import os  # Standard library for file and directory management
import numpy as np  # Numerical operations
import librosa  # Audio processing library
import note_seq  # Library for handling musical note sequences

SAMPLE_RATE = 16000
SF2_PATH = 'SGM-v2.01-Sal-Guit-Bass-V1.3.sf2'

def load_audio(file_path, sample_rate=SAMPLE_RATE):
    """Load and process an audio file from a local path."""
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")

    # Load the audio file using librosa
    audio_data, _ = librosa.load(file_path, sr=sample_rate)

    # Return the loaded audio data
    return audio_data

# Example:
audio_file_path = '/Users/ilyabelov/code/lucas-cecilio/Test_music.wav'
audio_data = load_audio(audio_file_path)
