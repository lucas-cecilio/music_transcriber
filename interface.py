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

# Create three tabs
tab1, tab2, tab3 = st.tabs(["Home", "About", "Team"])

# Home Tab
with tab1:
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
                    label="📥 Download MIDI",
                    data=midi_file,
                    file_name=f"{filename}_transcribed.mid"
                )

            # Button to download PDF file (.pdf)
            with col4:
                st.download_button(
                    label=" 📥 Download Score",
                    data=midi_score_pdf,
                    file_name=f"{filename}_transcribed.pdf"
                )

        # Create the download buttons
        create_download_buttons()

# About Tab
with tab2:
    st.markdown("<h2 style='font-size: 40px; text-align: left;'>About the project 🛈</h2>", unsafe_allow_html=True)
    st.write("")
    
    # Function to load image
    def load_image(image_file):
        with open(image_file, "rb") as img:
            return base64.b64encode(img.read()).decode()

    # Path to your logo image
    logo_path = 'images/le_wagon_logo.png'

    # Encode image to base64
    logo_base64 = load_image(logo_path)

    # Display the image and text with added space
    st.markdown(
        f'<img src="data:image/png;base64,{logo_base64}" style="vertical-align:middle; width:35px; height:35px; margin-right:10px;"> This is a final project of #1752 Data Science Bootcamp at Le Wagon',
        unsafe_allow_html=True
    )
    st.write("")
    
    # Paragraph 1: Why
    st.write("""
    **Why**\n
    The process of manually transcribing music is not only time-consuming but also requires a considerable level of expertise. Musicians and composers often find it challenging to transcribe complex audio, particularly when dealing with intricate harmonies or fast passages. This can stifle creativity, as time spent on manual transcription could be better used for composing or arranging. Moreover, many individuals lack the technical skills needed to accurately transcribe music, making it an inaccessible task for amateurs or those new to music production. An AI-powered music transcriber can alleviate these issues, providing a more efficient, accurate, and user-friendly alternative.
    """)
    st.write("")

    # Paragraph 2: Target
    st.write("""
    **Target**\n
    Our AI-powered music transcriber is designed for a wide range of users. Musicians and composers can quickly transcribe their improvisations or arrangements, making it easier to capture fleeting ideas. Music producers benefit from being able to edit and arrange transcribed MIDI files, streamlining the production process. Educators and students can use the tool to analyze music, aiding in both teaching and learning complex pieces. Sound engineers and audio technicians will find it invaluable for quickly creating transcriptions from recordings, improving workflow efficiency. Even amateurs, who might not have formal training in music theory, can use the tool to transcribe and edit music with ease.
    """)
    st.write("")
    
    # Paragraph 3: What is MIDI
    st.write("""
    **What is MIDI**\n
    MIDI (Musical Instrument Digital Interface) is a technical standard that describes a communications protocol, digital interface, and electrical connectors that connect a wide variety of electronic musical instruments, computers, and related audio devices. MIDI enables the creation and transfer of digital music data, making it an essential tool for modern music production. It allows for the manipulation of pitch, tempo, and other musical elements, offering extensive creative control to musicians and producers. MIDI files are compact, easy to edit, and can be used to trigger virtual instruments, making them highly versatile in music production.
    """)
    st.write("")

    # Paragraph 4: How the app works
    st.write("""
    **How the app works**
    
    1. Choose between the two models based on your transcription needs.
    2. Upload an audio file in MP3 or WAV format.
    3. Play the original audio to verify the input.
    4. Click on the 'Transcribe' button to start the transcription process.
    5. View the MIDI graphic generated from the transcription.
    6. Play the transcribed audio to ensure accuracy.
    7. Download the MIDI file or the PDF file containing the music score for further use.
    """)
    st.write("")
    
    # Paragraph 5: How the model works
    st.write("""
    **How the model works**
    
    There are two pre-trained transformer models:

    - The piano transcription model, described on [ISMIR 2021 paper](https://archives.ismir.net/ismir2021/paper/000030.pdf), \
        and trained on [MAESTRO piano dataset](https://magenta.tensorflow.org/datasets/maestro). \
        It has a F1-score of **82.75%**.
    - The multi-instrument transcription model, described on [ICLR 2023 paper](https://openreview.net/pdf?id=iMSjopcOn0p), \
        and trained on large and varied datasets. 
    - Both models are available on [Magenta MT3](https://github.com/magenta/mt3).
    """)
    st.write("")
    st.write("For illustration, there's an image of the architecture:")
    st.image('images/architecture_diagram_transformer.png', caption='Simplified solution architecture')

# Team Tab
with tab3:
    st.markdown("<h2 style='font-size: 40px; text-align: left;'>Our team 🏆</h2>", unsafe_allow_html=True)
    st.write("")

    # Team member 1
    with st.expander("🏄‍♂️ Lucas Cecilio"):
        st.write("""
        I am a civil engineer with a background in Business Analysis and AI Consulting at IBM, where I worked for almost five years. My passion for data science led me to Le Wagon bootcamp, where I developed new skills in Machine Learning, Python, AI, and MLOPS. I am eager to apply these skills to data projects, advancing my career as a data scientist.
        
        [Lucas's LinkedIn](https://www.linkedin.com/in/lucasceciliocerqueira/)
        """)

    # Team member 2
    with st.expander("⚡ Gabriel Pereira"):
        st.write("""
        Passionate about innovation and cutting-edge technology, I have always enjoyed exploring software development and AI. Le Wagon bootcamp provided me with the hands-on experience and the latest knowledge in these fields, allowing me to stay ahead of trends and tackle new challenges in the tech industry.
        
        [Gabriel's LinkedIn](https://www.linkedin.com/in/gabr-pereira/)
        """)

    # Team member 3
    with st.expander("😎 Ilya Belov"):
        st.write("""
        I spent the majority of my career as a Credit Analyst in the banking industry, but my curiosity about coding and machine learning brought me to Le Wagon bootcamp. Here, I gained the practical skills necessary to transition into the tech industry, and I am now focused on pursuing a career in this exciting field.
        
        [Ilya's LinkedIn](https://www.linkedin.com/in/ilya-belov1/)
        """)

    # Team member 4
    with st.expander("👨‍🍳 Aloisio Marques"):
        st.write("""
        I graduated in Gastronomy and managed my own business for 12 years until the pandemic prompted me to seek new challenges. Le Wagon bootcamp opened the door to the world of data science, where I learned essential skills in Machine Learning, Python, and AI. I am now eager to apply this knowledge in my future career endeavors.
        
        [Aloisio's LinkedIn](https://www.linkedin.com/in/aloisio-marques-28b97a2a4/)
        """)
