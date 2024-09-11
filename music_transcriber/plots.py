import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors

# Function to map each instrument to a pastel color
def get_instrument_color_map(df):
    unique_instruments = df['instrument'].unique()
    pastel_colors = plt.cm.Pastel1.colors  # Use a pastel color palette
    color_map = {instrument: pastel_colors[i % len(pastel_colors)] for i, instrument in enumerate(unique_instruments)}
    return color_map

# Function to plot the piano roll with matplotlib
def plot_notes_seq(df, dpi=300):
    fig, ax = plt.subplots(figsize=(14, 8))

    # Get the color mapping for the instruments
    color_map = get_instrument_color_map(df)

    for idx, row in df.iterrows():
        # Create a rectangle for each note without border
        rect = patches.Rectangle(
            (row['start_time'], row['pitch'] - 0.5),  # (x, y) starting position
            row['duration'],  # Rectangle width
            1,  # Rectangle height
            linewidth=1,
            edgecolor='black',
            facecolor=color_map[row['instrument']]  # Color based on instrument
        )
        ax.add_patch(rect)

    # Adjust axis limits
    ax.set_xlim([df['start_time'].min() - 0.5, df['end_time'].max() + 0.5])
    ax.set_ylim([df['pitch'].min() - 2, df['pitch'].max() + 2])
    ax.set_xlabel('Time(s)', fontsize=14)
    ax.set_ylabel('Pitch', fontsize=14)

    # Export as high-resolution PNG
    plt.grid(True)
    plt.tight_layout()
    
    return fig