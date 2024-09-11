import note_seq
from pathlib import Path
from selenium import webdriver
from bokeh.io.export import export_png
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from music_transcriber.params import *


def plot_midi(notes_sequence, midi_file_name, save_png=True):
    '''TODO: write docstring'''
    
    print('\nCreating a MIDI plot 🔄')
    midi_plot_name = str(Path(midi_file_name).with_suffix(".png"))
    midi_plot_path = str(OUTPUT_MIDI_PLOT_PATH / midi_plot_name)
    
    plot_midi = note_seq.plot_sequence(notes_sequence, show_figure=False)
 
    # Add and adjust title
    plot_midi.title.text = f'MIDI sequence of {midi_plot_name.replace(".png", "")}'
    plot_midi.title.text_font_size = "20pt"
    plot_midi.title.align = "center"
    
    # Adjust axis labels
    plot_midi.xaxis.axis_label = "Time(s)" 
    plot_midi.yaxis.axis_label = "Pitch Notes"
    plot_midi.xaxis.axis_label_text_font_size = "16pt"
    plot_midi.yaxis.axis_label_text_font_size = "16pt"  
    
    # Adjust the size of tick labels
    plot_midi.xaxis.major_label_text_font_size = "14pt" 
    plot_midi.yaxis.major_label_text_font_size = "14pt" 
    
    if save_png:
        # Disable toolbar and change dimensions
        plot_midi.toolbar_location = None  # Remove the toolbar
        plot_midi.width = 1600  # Increase width for higher quality
        plot_midi.height = 900  # Increase height for higher quality
        
        print('\nSaving a png of MIDI plot 📥')
        save_plot_midi(plot_midi, midi_plot_path)
        
    print('\nMIDI plot done ✅')
    return midi_plot_path, plot_midi
    
def save_plot_midi(plot_midi, midi_plot_path):
    '''TODO: write docstring'''

    # Configure Chrome driver in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Export the figure as a high-quality PNG
    export_png(plot_midi, filename=midi_plot_path, webdriver=driver)

    # Close the Chrome driver
    driver.quit()