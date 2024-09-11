import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse #, FileResponse
from bokeh.embed import json_item
from music_transcriber.utils import *
from music_transcriber.params import *

app = FastAPI()

def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')

# Endpoint to list available models
@app.get("/available-models/")
async def list_available_models():
    """
    Returns a list of available models and their descriptions.
    """
    return {"available_models": AVAILABLE_MODELS}

# Upload audio
@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(('.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # Saving uploaded file
    file_location = INPUT_AUDIO_PATH / file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"filename": file.filename, "filepath": str(file_location)}

# Transcribe audio with chosen model
@app.get("/transcribe/")
async def transcribe(filename: str, model_type: str = "piano", response_type: str = "binary"):
    if model_type not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid model type. Choose from 'piano' or 'multi-instrument'.")

    file_location = INPUT_AUDIO_PATH / filename
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found.")

     # Process audio
    audio_processed, audio_file_name = process_audio(filename)
    if audio_processed is None:
        raise HTTPException(status_code=400, detail="Audio processing failed.")
    
    # Load the model based on user choice
    selected_model = load_model(AVAILABLE_MODELS[model_type])

    # Run inference
    notes_sequence = transcribe_audio(selected_model, audio_processed)

    # Save the transcribed MIDI file
    midi_file_name, midi_file_path = download_midi(notes_sequence, audio_file_name)
    
    # Generate and save the .wav of transcribed audio
    midi_audio_path = midi_to_audio(midi_file_name, midi_file_path)
    
    # Generate and save the .pdf of a music score
    midi_score_path = midi_to_score(midi_file_name, midi_file_path)
    
    # Generate a dataframe of notes sequence
    notes_dict = sequence_to_dict(notes_sequence)
    
    # Plot the notes sequence
    # midi_plot_path, bokeh_plot = plot_midi(notes_sequence, midi_file_name, save_png=True)
    # bokeh_plot_json = json_item(bokeh_plot)
    
    if response_type == "path":
        return {
            "notes_dict": notes_dict,
            "midi_file_name": midi_file_name, 
            "midi_file_path": midi_file_path, 
            "midi_audio_path": midi_audio_path,
            "midi_score_path": midi_score_path
        }

    # Encode files to base64
    midi_file_base64 = encode_file_to_base64(midi_file_path)
    midi_audio_base64 = encode_file_to_base64(midi_audio_path)
    midi_score_base64 = encode_file_to_base64(midi_score_path)

    
    return JSONResponse(content={
        "notes_dict": notes_dict,
        "midi_file_name": midi_file_name,
        "midi_file_base64": midi_file_base64,
        "midi_audio_base64": midi_audio_base64,
        "midi_score_base64": midi_score_base64
    })