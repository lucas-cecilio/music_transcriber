from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import librosa
import os
from mt3 import note_seq
from pathlib import Path

app = FastAPI()

# Instantiate the model
MODEL = "ismir2021"
checkpoint_path = os.path.join(os.getenv('MT3_CHECKPOINT_DIR', '.'), 'ismir2021/')
#'/home/lucascecilio/code/lucas-cecilio/music_transcriber/checkpoints/ismir2021/'

inference_model = InferenceModel(checkpoint_path, MODEL)

UPLOAD_DIR = Path("./uploaded_audio")
MIDI_DIR = Path("./midi_output")

#upload audio
@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(('.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # Saving uploaded file
    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"filename": file.filename, "filepath": str(file_location)}

#transcribe audio
@app.post("/transcribe/")
async def transcribe_audio(filename: str):
    file_location = UPLOAD_DIR / filename
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    # Load audio file and run inference
    raw_audio = librosa.load(file_location, sr=16000)
    audio = raw_audio[0]
    est_ns = inference_model(audio)

    # Save the transcribed MIDI file
    midi_filename = filename.replace(".wav", ".mid")
    midi_filepath = MIDI_DIR / midi_filename
    note_seq.sequence_proto_to_midi_file(est_ns, midi_filepath)

    return {"midi_filename": midi_filename, "midi_filepath": str(midi_filepath)}

#download MIDI file
@app.get("/download-midi/")
async def download_midi(midi_filename: str):
    midi_filepath = MIDI_DIR / midi_filename
    if not midi_filepath.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found.")

    return FileResponse(midi_filepath, media_type='audio/midi', filename=midi_filename)
