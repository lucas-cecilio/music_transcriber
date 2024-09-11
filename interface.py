import streamlit as st
import requests
import base64
import io
import json
from bokeh.embed import json_item

# Set the base API URL
API_URL = "http://127.0.0.1:8000"

# Set the response_type for transcribe endpoint
response_type = "binary" # 'binary' for encoded files, 'path' for path files

# Title of the website
st.title("Music Transcription with Transformers")

# How to use it
st.markdown("""
### How to use it:
This site is an interactive demo of a few music transcription models created by our team. 
You can upload audio and have one of our models automatically transcribe it.

**Instructions:**
1. In the Load Model cell, choose either `Piano` for piano transcription or `Multi-instrument` for multi-instrument transcription.
2. In the Upload Audio cell, choose an MP3 or WAV file from your computer when prompted.
3. Transcribe the audio using the Transcribe Audio cell (it may take a few minutes depending on the length of the audio).
""")

# Choose between two models
model_type = st.radio("Choose a model", ["Piano", "Multi-instrument"]).lower()

# Upload audio
uploaded_file = st.file_uploader("Upload your audio file (.mp3 or .wav)", type=["mp3", "wav"])

if uploaded_file is not None:
    # Convert uploaded file to the path in the directory and send to API
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    upload_response = requests.post(f"{API_URL}/upload-audio/", files=files)
    
    # Immediately play the uploaded audio file
    st.audio(uploaded_file, format="audio/mp3")
    
    if upload_response.status_code == 200:
        st.success("Audio file uploaded successfully!")
        file_data = upload_response.json()
        filename = file_data["filename"]

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
                    
                    if response_type=='binary':
                        # Decode the Base64 encoded data
                        midi_file = base64.b64decode(transcription_data["midi_file_base64"])
                        midi_audio = base64.b64decode(transcription_data["midi_audio_base64"])
                        midi_score_pdf = base64.b64decode(transcription_data["midi_score_base64"])
                        midi_plot = base64.b64decode(transcription_data["midi_plot_base64"])
                    
                    if response_type=='path':
                        midi_file = transcription_data["midi_file_path"]
                        midi_audio = transcription_data["midi_audio_path"]
                        midi_score_pdf = transcription_data["midi_score_path"]
                        midi_plot = transcription_data["midi_plot_path"]

                    
                    # Generate and display Music Score
                    st.image(midi_plot)
                    
                    # Play transcribed audio
                    st.audio(midi_audio, format="audio/wav")

                    
                    # Função para criar o botão de download
                    def download_button(data, filename, label):
                        filename = str(filename).replace(".wav", "")
                        b64 = base64.b64encode(data).decode()  # Codifica os dados em base64
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{label}</a>'
                        return href
                    
                    # Criar colunas para organizar os botões de download
                    col1, col2 = st.columns(2)
                    
                    # Botão para download do arquivo MIDI (.mid)
                    with col1:
                        st.markdown(download_button(midi_file, f"{filename}_transcribed.mid", "Download MIDI"), unsafe_allow_html=True)

                    # Botão para download do arquivo PDF (.pdf)
                    with col2:
                        st.markdown(download_button(midi_score_pdf, f"{filename}_transcribed.pdf", "Download PDF"), unsafe_allow_html=True)
                        
                    # # Download buttons
                    # # st.download_button(label="Download Score", data=midi_score_pdf)
                    # st.download_button(label="Download MIDI File", data=midi_file)


                else:
                    st.error("Transcription failed!")
    else:
        st.error("Failed to upload audio file.")

# # Add the GitHub link and sources button
# st.markdown("[GitHub Project](https://github.com/lucas-cecilio/music_transcriber)")





                    # # Show Bokeh plot
                    # bokeh_plot_json = transcription_data["bokeh_plot_json"]
                    # if bokeh_plot_json:
                    #     st.bokeh_chart(json_item(bokeh_plot_json))
                    # else:
                    #     st.error("Failed to load Bokeh plot.")