import streamlit as st
import requests
import base64
import json
from bokeh.embed import json_item

# Set the API URL
API_URL = "http://127.0.0.1:8000"

# Title of the website
st.title("Music Transcription with Transformers")

# How to use it
st.markdown("""
### How to use it:
This site is an interactive demo of a few music transcription models created by our team. 
You can upload audio and have one of our models automatically transcribe it.

**Instructions:**
1. In the Load Model cell, choose either `piano` for piano transcription or `multi-instrument` for multi-instrument transcription.
2. In the Upload Audio cell, choose an MP3 or WAV file from your computer when prompted.
3. Transcribe the audio using the Transcribe Audio cell (it may take a few minutes depending on the length of the audio).
""")

# Choose between two models
model_type = st.selectbox("Choose a model", ["piano", "multi-instrument"])

# # Map the user-friendly names to the actual model types
# model_type_mapping = {
#     "piano": "ismir2021",
#     "multi-instrument": "mt3"
# }

# Upload audio
uploaded_file = st.file_uploader("Upload your audio file (.mp3 or .wav)", type=["mp3", "wav"])

if uploaded_file is not None:
    # Immediately play the uploaded audio file
    st.audio(uploaded_file, format="audio/mp3")

    # Convert uploaded file to the path in the directory and send to API
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    upload_response = requests.post(f"{API_URL}/upload-audio/", files=files)
    # st.write(upload_response)
    
    if upload_response.status_code == 200:
        st.success("Audio file uploaded successfully!")
        file_data = upload_response.json()
        filename = file_data["filename"]

        # Display the "Transcribe" button
        if st.button("Transcribe"):
            with st.spinner('Transcribing...'):
                # Initialize progress bar
                progress_bar = st.progress(0)

                # Step 2: Transcribe the audio (50% progress)
                transcribe_payload = {"filename": filename, "model_type": model_type}
                # st.write(transcribe_payload)
                # st.write(type(transcribe_payload['filename']))
                # st.write(type(transcribe_payload['model_type']))
                
                # http://127.0.0.1:8000/transcribe/?filename=piano_chopin_5s.wav&model_type=piano
                # transcribe_response = requests.get(f"{API_URL}/transcribe/", json=transcribe_payload)
  
                transcribe_response = requests.get(f"{API_URL}/transcribe/?filename={filename}&model_type={model_type}&response_type=binary")
                st.write(transcribe_response)
                
                progress_bar.progress(50)

                if transcribe_response.status_code == 200:
                    transcription_data = transcribe_response.json()
                    progress_bar.progress(75)

                    # Decode the Base64 encoded data
                    midi_file = base64.b64decode(transcription_data["midi_file_base64"])
                    midi_audio = base64.b64decode(transcription_data["midi_audio_base64"])
                    midi_score_pdf = base64.b64decode(transcription_data["midi_score_pdf_base64"])
                    midi_plot = base64.b64decode(transcription_data["midi_plot_base64"])
                    
                    # midi_file = transcription_data["midi_file_path"]
                    # midi_audio = transcription_data["midi_audio_path"]
                    # midi_score_pdf = transcription_data["midi_score_path"]
                    # midi_plot = transcription_data["midi_plot_path"]

                    # Show Bokeh plot
                    # bokeh_plot_json = transcription_data["bokeh_plot_json"]
                    # if bokeh_plot_json:
                    #     st.bokeh_chart(json_item(bokeh_plot_json))
                    # else:
                    #     st.error("Failed to load Bokeh plot.")

                    # Play transcribed audio
                    st.audio(midi_audio, format="audio/wav")

                    # Generate and display Music Score
                    st.image(midi_plot, caption=f"Music Score for {filename}")

                    # Download buttons
                    st.download_button(label="Download Score", data=midi_score_pdf)
                    st.download_button(label="Download MIDI File", data=midi_file)

                    progress_bar.progress(100)
                else:
                    st.error("Transcription failed!")
    else:
        st.error("Failed to upload audio file.")

# Add the GitHub link and sources button
st.markdown("[GitHub Project](https://github.com/lucas-cecilio/music_transcriber)")