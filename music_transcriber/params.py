import os
from pathlib import Path

##################  VARIABLES  ##################
SAMPLE_RATE = int(os.environ.get("SAMPLE_RATE"))
AVAILABLE_MODELS = {
    "piano": "ismir2021",
    "multi-instrument": "mt3"
}

##################  PATHS  #####################
BASE_PATH = Path(__file__).resolve().parent.parent
SF2_PATH = BASE_PATH / 'mt3' / 'SGM-v2.01-Sal-Guit-Bass-V1.3.sf2'
INPUT_AUDIO_PATH = BASE_PATH / 'input_audio'
CHECKPOINT_PATH = BASE_PATH / 'checkpoints'
OUTPUT_MIDI_FILE_PATH = BASE_PATH / 'outputs' / 'midi_file'
OUTPUT_MIDI_PLOT_PATH = BASE_PATH / 'outputs' / 'midi_plot'
OUTPUT_MIDI_AUDIO_PATH = BASE_PATH / 'outputs' / 'midi_audio'
OUTPUT_MIDI_SCORE_PATH = BASE_PATH / 'outputs' / 'midi_score'
