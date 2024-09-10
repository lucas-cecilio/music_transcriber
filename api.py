from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from bokeh.embed import json_item
from music_transcriber.utils import *
from music_transcriber.params import *

app = FastAPI()

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
@app.post("/transcribe/")
async def transcribe(filename: str, model_type: str = "piano"):
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
    midi_score_pdf_path = midi_to_score(midi_file_name, midi_file_path)
    
    # Plot the notes sequence
    midi_plot_path, bokeh_plot = plot_midi(notes_sequence, midi_file_name, save_png=True)
    bokeh_plot_json = json_item(bokeh_plot)

    return {
        "midi_file_name": midi_file_name, 
        "midi_file_path": midi_file_path, 
        "midi_audio_path": midi_audio_path,
        "midi_score_path": midi_score_pdf_path,
        "midi_plot_path": midi_plot_path,
        "bokeh_plot_json": bokeh_plot_json
    }

# Download MIDI file
@app.get("/download-midi/")
async def download_midi_file(midi_file_name: str):
    midi_file_path = OUTPUT_MIDI_FILE_PATH / midi_file_name
    if not midi_file_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found.")

    return FileResponse(midi_file_path, media_type='audio/midi', filename=midi_file_name)
