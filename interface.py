import streamlit as st
import requests
from pathlib import Path
import os
from midi2audio import FluidSynth

# Define the API URL
API_URL = "http://127.0.0.1:8000"

# Directories for file handling (same as in FastAPI)
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(BASE_DIR, 'input_audio')
MIDI_DIR = Path(BASE_DIR, 'outputs/midi_file')
AUDIO_OUTPUT_DIR = Path(BASE_DIR, 'outputs/midi_audio')

def upload_file(file):
    """Upload an audio file to the FastAPI backend."""
    files = {"file": (file.name, file, file.type)}
    response = requests.post(f"{API_URL}/upload-audio/", files=files)
    return response

def transcribe_audio(filename, model_type):
    """Trigger the transcription process via the FastAPI backend."""
    response = requests.post(f"{API_URL}/transcribe/", json={"filename": filename, "model_type": model_type})
    return response

def download_midi(filename):
    """Download the transcribed MIDI file."""
    response = requests.get(f"{API_URL}/download-midi/", params={"midi_filename": filename})
    midi_path = MIDI_DIR / filename
    with open(midi_path, "wb") as f:
        f.write(response.content)
    return midi_path

def convert_midi_to_wav(midi_path, output_path):
    """Convert MIDI to WAV using FluidSynth."""
    fs = FluidSynth()
    fs.midi_to_audio(str(midi_path), str(output_path))

# Streamlit UI
st.title("Music Transcription App")
st.write("Upload an MP3 or WAV file to transcribe it to MIDI.")

# Model selection dropdown
model_type = st.selectbox(
    "Choose the transcription model:",
    ("mt3 (all instruments)", "ismir2021 (piano only)")
)

# Map the user-friendly names to the model identifiers expected by the API
model_map = {
    "mt3 (all instruments)": "multi-instrument",
    "ismir2021 (piano only)": "piano"
}

# Upload audio file
uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "wav"])

if uploaded_file is not None:
    # Save the uploaded file to disk
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Play the audio
    st.write("Playing the uploaded audio file:")
    st.audio(str(file_path))  # Convert Path to string

    # Upload the file to the FastAPI server
    st.write("Uploading file...")
    upload_response = upload_file(uploaded_file)

    if upload_response.status_code == 200:
        st.write(f"File uploaded successfully: {upload_response.json()['filename']}")

        # Run transcription using the selected model
        selected_model = model_map[model_type]
        st.write(f"Transcribing the audio file using the {selected_model} model...")
        transcribe_response = transcribe_audio(upload_response.json()['filename'], selected_model)

        if transcribe_response.status_code == 200:
            midi_filename = transcribe_response.json()['midi_filename']
            st.write(f"Transcription successful! MIDI file generated: {midi_filename}")

            # Download the MIDI file
            st.write("Downloading the MIDI file...")
            midi_path = download_midi(midi_filename)

            # Convert MIDI to WAV
            wav_filename = midi_filename.replace(".mid", ".wav")
            wav_path = AUDIO_OUTPUT_DIR / wav_filename
            st.write("Converting MIDI to WAV...")
            convert_midi_to_wav(midi_path, wav_path)

            # Play the converted WAV file
            st.write("Playing the transcribed WAV file:")
            st.audio(str(wav_path))  # Convert Path to string

            # Provide a download link for the MIDI file
            with open(midi_path, "rb") as midi_file:
                st.download_button(
                    label="Download MIDI",
                    data=midi_file.read(),
                    file_name=midi_filename,
                    mime="audio/midi"
                )

            st.write("MIDI file ready for download!")
        else:
            st.write("Transcription failed. Please try again.")
    else:
        st.write("File upload failed. Please try again.")
