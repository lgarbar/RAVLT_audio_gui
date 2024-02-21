import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import pygame
import threading
import time
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set the backend to 'Agg' to avoid Qt error
import matplotlib
matplotlib.use('Agg')

class AudioPlayer:
    def __init__(self, audio_file, rate=44100):
        self.audio_file = audio_file
        self.rate = rate
        self.audio_length = len(AudioSegment.from_file(self.audio_file)) / 1000.0  # Audio length in seconds
        self.audio_data = self.load_audio()
        self.playing = False
        self.cursor_position = 0
        self.mouse_position = None

        pygame.mixer.init()

        self.root = tk.Tk()
        self.root.title("Audio Player")

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.get_time_axis(), self.audio_data)
        self.red_cursor_line = self.ax.axvline(x=self.cursor_position, color='red', linestyle='-', linewidth=2)
        self.green_cursor_line, = self.ax.plot([0, 0], [-1, 1], color='green', linestyle='-', linewidth=2, visible=False)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Amplitude')
        self.init_plot()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        # Variable to store the clicked time position
        self.clicked_position = None

    def get_time_axis(self):
        return np.linspace(0, self.audio_length, len(self.audio_data))

    def load_audio(self):
        audio = AudioSegment.from_file(self.audio_file)
        return np.array(audio.get_array_of_samples()) / 32768.0  # Normalize to the range [-1, 1]

    def init_plot(self):
        return self.red_cursor_line, self.green_cursor_line

    def update_plot(self, frame):
        cursor_line_x = frame
        self.red_cursor_line.set_xdata([cursor_line_x, cursor_line_x])
        self.green_cursor_line.set_xdata([self.mouse_position, self.mouse_position])
        self.canvas.draw()  # Redraw the canvas
        return self.red_cursor_line, self.green_cursor_line

    def play_audio(self):
        self.playing = True
        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()

        while self.playing:
            elapsed_time = pygame.mixer.music.get_pos() / 1000.0  # Elapsed time in seconds
            self.cursor_position = elapsed_time

            if self.cursor_position >= self.audio_length:
                self.stop_audio()

            self.update_plot(self.cursor_position)  # Call update_plot to update the cursor position

            time.sleep(0.01)  # Adjust as needed for smoother animation

    def start_audio(self):
        self.play_thread = threading.Thread(target=self.play_audio)
        self.play_thread.start()

        # Bind mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def stop_audio(self):
        self.playing = False
        self.play_thread.join()  # Wait for the play_thread to finish
        self.root.quit()  # Quit the Tkinter app

    def run(self):
        self.root.mainloop()

    def on_motion(self, event):
        if event.xdata is not None:
            cursor_line_x = event.xdata
            self.mouse_position = cursor_line_x
            self.green_cursor_line.set_xdata([self.mouse_position, self.mouse_position])
            self.green_cursor_line.set_visible(True)
        else:
            self.green_cursor_line.set_visible(False)

        self.canvas.draw()

    def on_click(self, event):
        if event.xdata is not None:
            self.clicked_position = event.xdata
            print(f"Clicked at time: {self.clicked_position} seconds")

if __name__ == "__main__":
    audio_file = "/data2/Projects/NKI_RS2/RAVLT/ravlt_audio_gui/RAVLT/sub-M10971818_ses-MOBI1A_task-ravlt1_run-001_lsl/Block1Recall.wav"
    player = AudioPlayer(audio_file)
    player.start_audio()
    player.run()
