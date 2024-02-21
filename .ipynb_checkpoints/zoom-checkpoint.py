import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class AudioVisualizerApp:
    def __init__(self, root, audio_data, audio_duration):
        self.root = root
        self.root.title("Audio Visualizer")
        
        self.audio_data = audio_data
        self.audio_duration = audio_duration
        
        # Initial x-axis range
        self.initial_x_range = (0, self.audio_duration)
        self.x_range = self.initial_x_range
        
        # Zoom parameters
        self.zoom_factor = 0.8
        self.max_zoom_count = int(1 / (1 - self.zoom_factor)) - 1
        self.cursor_position = 8
        
        # Zoom counter
        self.zoom_count = 0
        
        # Create initial figure
        self.create_figure()
        
        # Create zoom in and zoom out buttons
        self.create_zoom_in_button()
        self.create_zoom_out_button()
        
    def create_figure(self):
        # Create a figure and axis
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        
        # Plot the initial audio waveform
        self.ax.plot(self.audio_data)
        
        # Create a cursor line
        self.cursor_line = self.ax.axvline(x=self.cursor_position, color='r', linestyle='--')
        
        # Set initial x-axis range
        self.ax.set_xlim(self.x_range)
        
        # Embed Matplotlib figure in Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
    def create_zoom_in_button(self):
        # Create a button for zooming in
        zoom_in_button = tk.Button(self.root, text="Zoom In", command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT)
        
    def create_zoom_out_button(self):
        # Create a button for zooming out
        zoom_out_button = tk.Button(self.root, text="Zoom Out", command=self.zoom_out)
        zoom_out_button.pack(side=tk.RIGHT)
        
    def zoom_in(self):
        # Check if max zoom count is reached
        if self.zoom_count >= self.max_zoom_count:
            return
        
        # Calculate new x-axis range
        x_range_length = self.x_range[1] - self.x_range[0]
        new_x_range_length = x_range_length * self.zoom_factor
        cursor_position = self.cursor_line.get_xdata()[0]
        
        # Calculate new min and max
        if cursor_position - new_x_range_length / 2 < 0 or cursor_position + new_x_range_length / 2 > self.initial_x_range[1]:
            if cursor_position - new_x_range_length / 2 < 0:
                new_min = 0
                new_max = new_min + new_x_range_length
            else:
                new_max = self.initial_x_range[1]
                new_min = new_max - new_x_range_length
        else:
            new_min = max(self.x_range[0], cursor_position - new_x_range_length / 2)
            new_max = min(self.x_range[1], cursor_position + new_x_range_length / 2)
        
        # Update x-axis range
        self.x_range = (new_min, new_max)
        
        # Increment zoom count
        self.zoom_count += 1
        
        # Redraw the figure
        self.ax.set_xlim(self.x_range)
        self.canvas.draw()
        
    def zoom_out(self):
        # Check if at the original range
        if self.x_range >= self.initial_x_range:
            return
        
        # Calculate new x-axis range for zooming out
        x_range_length = self.x_range[1] - self.x_range[0]
        new_x_range_length = x_range_length / self.zoom_factor
        cursor_position = self.cursor_line.get_xdata()[0]
        
        # Calculate new min and max
        if cursor_position - new_x_range_length / 2 < 0 or cursor_position + new_x_range_length / 2 > self.initial_x_range[1]:
            if cursor_position - new_x_range_length / 2 < 0:
                new_min = 0
                new_max = new_min + new_x_range_length
            else:
                new_max = self.initial_x_range[1]
                new_min = new_max - new_x_range_length
        else:
            new_min = max(self.x_range[0], cursor_position - new_x_range_length / 2)
            new_max = min(self.x_range[1], cursor_position + new_x_range_length / 2)
        
        # Update x-axis range
        self.x_range = (new_min, new_max)
        
        # Decrement zoom count
        self.zoom_count -= 1
        
        # Redraw the figure
        self.ax.set_xlim(self.x_range)
        self.canvas.draw()

if __name__ == "__main__":
    # Dummy audio data and duration (replace with your actual data)
    audio_duration = 40  # seconds
    audio_data = [random.uniform(-3, 3) for _ in range(audio_duration)]
    
    root = tk.Tk()
    app = AudioVisualizerApp(root, audio_data, audio_duration)
    root.mainloop()
