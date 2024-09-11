import streamlit as st
import requests
import base64
from pathlib import Path

import pandas as pd
from music_transcriber.plots import plot_notes_seq

st.set_page_config(
    page_title="Music Transcriber", 
    page_icon="🎵",
    layout="centered", 
    initial_sidebar_state="auto"
)

# Set the base API URL
API_URL = "http://127.0.0.1:8000"

# Set the response_type for transcribe endpoint
response_type = "binary"  # 'binary' for encoded files, 'path' for path files

# Title of the website
st.markdown("<h1 style='font-size: 48px; text-align: left;'>Music Transcriber 🎵</h1>", unsafe_allow_html=True)

# Greetings
st.markdown("""
#### Transcribe an instrumental song to MIDI and to music score!

**Upload your audio and AI will do the magic ✨**
""")
st.write("")

# Choose between two models
model_type = st.radio("Select if your audio is a piano or a multi-instrumental song:", ["Piano", "Multi-instrument"]).lower()
st.write("")

# Upload audio
uploaded_file = st.file_uploader("Upload your audio file (.mp3 or .wav)", type=["mp3", "wav"])

# Initialize or update session state for file upload
if uploaded_file is not None:
    # Clear transcription data and download button states only if a new file is uploaded
    if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
        st.session_state.transcription_data = None
        st.session_state.midi_downloaded = False
        st.session_state.pdf_downloaded = False
        st.session_state.uploaded_filename = uploaded_file.name  # Track current file name

    # Convert uploaded file to the path in the directory and send to API
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    upload_response = requests.post(f"{API_URL}/upload-audio/", files=files)

    if upload_response.status_code == 200:
        st.success("Audio file uploaded successfully!")
        file_data = upload_response.json()
        filename = file_data["filename"]

        # Play the uploaded audio file
        st.write("")
        st.markdown("<p style='text-align: left; font-size: 15px;'>Original audio:</p>", unsafe_allow_html=True)
        st.audio(uploaded_file, format="audio/mp3")
        st.write("")

        # Display the "Transcribe" button
        if st.button("Transcribe"):
            with st.spinner('Transcribing...'):
                params = {
                    "filename": filename,
                    "model_type": model_type,
                    "response_type": response_type
                }

                transcribe_response = requests.get(f"{API_URL}/transcribe/", params=params)

                if transcribe_response.status_code == 200:
                    transcription_data = transcribe_response.json()

                    # Store transcription data in session state to avoid losing it on rerun
                    st.session_state.transcription_data = transcription_data
                    st.session_state.filename = filename
                    st.session_state.response_type = response_type

                    st.success("Transcription completed!")

                else:
                    st.error("Transcription failed!")
    else:
        st.error("Failed to upload audio file.")

# Check if transcription data is available in session state
if "transcription_data" in st.session_state and st.session_state.transcription_data is not None:
    transcription_data = st.session_state.transcription_data
    filename = str(Path(st.session_state.filename).stem)
    response_type = st.session_state.response_type

    if response_type == 'binary':
        # Decode the Base64 encoded data
        midi_file = base64.b64decode(transcription_data["midi_file_base64"])
        midi_audio = base64.b64decode(transcription_data["midi_audio_base64"])
        midi_score_pdf = base64.b64decode(transcription_data["midi_score_base64"])

    if response_type == 'path':
        midi_file = transcription_data["midi_file_path"]
        midi_audio = transcription_data["midi_audio_path"]
        midi_score_pdf = transcription_data["midi_score_path"]

    # Display a MIDI Graphic
    st.write("")
    st.markdown("<p style='text-align: center; font-size: 18px;'>Graphic representation of generated MIDI</p>", unsafe_allow_html=True)
    
    df_notes = pd.DataFrame(transcription_data["notes_dict"]) # Creating a dataframe with notes
    st.pyplot(plot_notes_seq(df_notes))
    st.markdown(
        "<p style='text-align: center; font-size: 13px;'><i>Work on your file with a <a href='https://signal.vercel.app/edit' target='_blank'>Online MIDI Editor</a></i></p>", 
        unsafe_allow_html=True
    )
    st.write("")
    
    # Play transcribed audio
    st.write("")
    st.markdown("<p style='text-align: left; font-size: 15px;'>Transcribed audio:</p>", unsafe_allow_html=True)
    st.audio(midi_audio, format="audio/wav")
    st.write("")

    # Function to create download buttons
    def create_download_buttons():
        # Create columns to organize the download buttons
        col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 3, 2])

        # Button to download MIDI file (.mid)
        with col2:
            st.download_button(
                label="Download MIDI",
                data=midi_file,
                file_name=f"{filename}_transcribed.mid"
            )

        # Button to download PDF file (.pdf)
        with col4:
            st.download_button(
                label="Download Score",
                data=midi_score_pdf,
                file_name=f"{filename}_transcribed.pdf"
            )

    # Create the download buttons
    create_download_buttons()
