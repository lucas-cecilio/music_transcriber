import os

##################  VARIABLES  ##################
SAMPLE_RATE = int(os.environ.get("SAMPLE_RATE"))
AVAILABLE_MODELS = {
    "piano": "ismir2021",
    "multi-instrument": "mt3"
}

##################  PATHS  #####################
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SF2_PATH = os.path.join(BASE_DIR, 'mt3', 'SGM-v2.01-Sal-Guit-Bass-V1.3.sf2')
UPLOAD_AUDIO_DIR = os.path.join(BASE_DIR, 'input_audio')
MIDI_FILE_DIR = os.path.join(BASE_DIR, 'outputs', 'midi_file')
MIDI_PLOT_DIR = os.path.join(BASE_DIR, 'outputs', 'midi_plot')
