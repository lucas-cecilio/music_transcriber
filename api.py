import os
import note_seq
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from music_transcriber.utils import process_audio, load_model, transcript_audio, download_midi, plot_midi
from music_transcriber.params import *

app = FastAPI()

UPLOAD_AUDIO_DIR = Path(os.path.join(BASE_DIR, 'input_audio'))
MIDI_FILE_DIR = Path(os.path.join(BASE_DIR, 'outputs', 'midi_file'))
MIDI_PLOT_DIR = Path(os.path.join(BASE_DIR, 'outputs', 'midi_plot'))

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
    file_location = UPLOAD_AUDIO_DIR / file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"filename": file.filename, "filepath": str(file_location)}

# Transcribe audio with chosen model
@app.post("/transcribe/")
async def transcribe_audio(filename: str, model_type: str = "piano"):
    if model_type not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid model type. Choose from 'piano' or 'multi-instrument'.")

    file_location = UPLOAD_AUDIO_DIR / filename
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    # Load the model based on user choice
    selected_model = load_model(AVAILABLE_MODELS[model_type])

    # Process audio
    audio = process_audio(filename)
    if audio is None:
        raise HTTPException(status_code=400, detail="Audio processing failed.")

    # Run inference
    est_ns = transcript_audio(selected_model, audio)

    # Save the transcribed MIDI file
    midi_filename = filename.replace(".wav", ".mid")
    midi_filepath = MIDI_FILE_DIR / midi_filename
    download_midi(est_ns)

    return {"midi_filename": midi_filename, "midi_filepath": str(midi_filepath)}

# Download MIDI file
@app.get("/download-midi/")
async def download_midi_file(midi_filename: str):
    midi_filepath = MIDI_FILE_DIR / midi_filename
    if not midi_filepath.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found.")

    return FileResponse(midi_filepath, media_type='audio/midi', filename=midi_filename)

# Plot MIDI file
@app.get("/plot-midi/")
async def plot_midi_file(midi_filename: str, save_png: bool = False):
    midi_filepath = MIDI_FILE_DIR / midi_filename
    if not midi_filepath.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found.")

    # Load and plot the MIDI file
    est_ns = note_seq.midi_file_to_note_sequence(midi_filepath)
    plot = plot_midi(est_ns, save_png=save_png)

    if save_png:
        plot_png_path = MIDI_PLOT_DIR / 'plot.png'
        return {"plot_png_path": str(plot_png_path)}

    return {"message": "MIDI plot generated."}
