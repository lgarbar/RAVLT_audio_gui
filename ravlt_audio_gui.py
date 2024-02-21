import tkinter as tk
from tkinter import filedialog, simpledialog, ttk, messagebox
import os
import pandas as pd
import numpy as np
import time
import os
import shutil
import matplotlib.pyplot as plt
import pygame
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set the backend to 'Agg' to avoid Qt error
import matplotlib
matplotlib.use('Agg')

try:
    import pygame
    from pydub import AudioSegment
    AUDIO_ENABLED = True
except ImportError:
    print('Audio is not enabled due to import error')
    AUDIO_ENABLED = False

class InitialsEntryApp:
    def __init__(self, root, initials_callback):
        self.root = root
        self.root.title("Initials Entry")
        self.initials_callback = initials_callback

        # Add label and entry box for entering initials
        self.label = tk.Label(root, text="Enter Your Initials:")
        self.label.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()

        # Add button to submit initials
        self.submit_button = tk.Button(root, text="Submit", command=self.submit_initials)
        self.submit_button.pack()

        # Variable to store entered initials
        self.entered_initials = None

    def submit_initials(self):
        initials = self.entry.get()
        if initials:
            self.entered_initials = initials
            self.initials_callback(initials)
            self.root.quit()  # Use quit() instead of destroy()

class AudioPlayerApp:
    def __init__(self, root, initials):
        self.root = root
        self.root.title("Audio Player App")

        self.df = None
        self.current_index = 0
        self.cursor_position = 0
        self.start_time = 0
        self.end_time = 0
        self.start_section = 0
        self.end_section = 0
        self.insert_start_section = 0
        self.insert_end_section = 0
        self.audio_segment = None
        self.file_path = None
        self.validation_pressed = False
        self.start_showing_text = False
        self.finished_file = False
        self.rate = 44100
        self.mouse_position = None
        self.onset_position = None
        self.offset_position = None
        self.edit = False
        self.insert = False
        
        # Zoom parameters
        self.zoom_factor = 0.8
        self.max_zoom_count = int(1 / (1 - self.zoom_factor)) + 2
        
        # Zoom counter
        self.zoom_count = 0

        self.initials = initials
        self.entered_text = None
        
        # Create an 'edited' folder if it doesn't exist
        self.edited_folder = 'edited'
        os.makedirs(self.edited_folder, exist_ok=True)

        pygame.mixer.init()

        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the CSV display
        self.csv_frame = ttk.Frame(self.root)
        self.csv_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create a Text widget to display the CSV content
        self.csv_text = tk.Text(self.csv_frame, wrap="none")
        self.csv_text.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar for the Text widget
        scrollbar_y = ttk.Scrollbar(self.csv_frame, command=self.csv_text.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.csv_text["yscrollcommand"] = scrollbar_y.set

        # Create a placeholder for the visualization at grid(row=0, column=1)
        self.canvas_placeholder = tk.Canvas(self.root, width=400, height=300, bg="white")
        self.canvas_placeholder.grid(row=0, column=2)

        # displaying gui buttons
        # LEFT COLUMN
        self.controls_label = tk.StringVar()
        self.controls_label.set('Controls')
        self.label_display_3 = tk.Label(self.root, textvariable=self.controls_label)
        self.label_display_3.grid(row=1, column=0, padx=0, pady=0)
        
        self.task_text = tk.StringVar()
        self.label_display_2 = tk.Label(self.root, textvariable=self.task_text)
        self.label_display_2.grid(row=1, column=0, padx=10, pady=10)
        
        self.start_button = tk.Button(self.root, text="Start", state=tk.DISABLED, command=self.start_playback)
        self.start_button.grid(row=2, column=0, padx=10, pady=0)

        self.restart_button = tk.Button(self.root, text="Restart", state=tk.DISABLED, command=self.restart)
        self.restart_button.grid(row=3, column=0, padx=10, pady=0)

        self.next_row_button = tk.Button(self.root, text="Next Row", state=tk.DISABLED, command=self.next_playback)
        self.next_row_button.grid(row=4, column=0, padx=10, pady=0)
        
        self.next_file_button = tk.Button(self.root, text="Next File", state=tk.DISABLED, command=self.next_file)
        self.next_file_button.grid(row=5, column=0, padx=10, pady=0)
        
        self.refresh_button = tk.Button(self.root, text="Refresh", state=tk.DISABLED, command=self.refresh)
        self.refresh_button.grid(row=6, column=0, padx=10, pady=0)

        self.import_button = tk.Button(self.root, text="Import", command=lambda: self.import_data(False))
        self.import_button.grid(row=7, column=0, padx=10, pady=0)

        self.whole_audio_button = tk.Button(self.root, text="Play Full Audio", state=tk.DISABLED, command=self.play_full_audio)
        self.whole_audio_button.grid(row=8, column=0, padx=10, pady=0)

        # MIDDLE COLUMN
        self.label_text = tk.StringVar()
        self.label_display_1 = tk.Label(self.root, textvariable=self.label_text)
        self.label_display_1.grid(row=0, column=1, padx=0, pady=0)
        
        self.zoom_in_button = tk.Button(self.root, text="Zoom In", command=self.zoom_in, state=tk.DISABLED)
        self.zoom_in_button.grid(row=1, column=1, padx=0, pady=0)
        
        self.zoom_out_button = tk.Button(self.root, text="Zoom Out", command=self.zoom_out, state=tk.DISABLED)
        self.zoom_out_button.grid(row=2, column=1, padx=0, pady=0)

        self.edit_label = tk.StringVar()
        self.edit_label.set('Edits')
        self.label_display_3 = tk.Label(self.root, textvariable=self.edit_label)
        self.label_display_3.grid(row=3, column=1, padx=0, pady=0)

        self.start_edit_button = tk.Button(self.root, text="Start Edit", state=tk.DISABLED, command=lambda: self.mark_edit_label('edit', 'edit'), bg='red')
        self.start_edit_button.grid(row=4, column=1, padx=0, pady=0)

        self.save_edit_button = tk.Button(self.root, text="Save Edit", state=tk.DISABLED, command=lambda: self.open_popup('edit'), bg='red')
        self.save_edit_button.grid(row=5, column=1, padx=0, pady=0)
        
        self.drop_button = tk.Button(self.root, text="Drop", state=tk.DISABLED, command=lambda: self.mark_edit_label('drop', 'drop'), bg='yellow')
        self.drop_button.grid(row=6, column=1, padx=0, pady=0)

        self.start_insert_button = tk.Button(self.root, text="Start Insert", state=tk.DISABLED, command=lambda: self.mark_edit_label('insert', 'insert'), bg='blue')
        self.start_insert_button.grid(row=7, column=1, padx=0)

        self.save_insert_button = tk.Button(self.root, text="Save Insert", state=tk.DISABLED, command=lambda: self.open_popup('insert'), bg='blue')
        self.save_insert_button.grid(row=8, column=1, padx=0)

        # RIGHT COLUMN
        self.space = tk.StringVar()
        self.space.set('Quality Check')
        self.label_display_2 = tk.Label(self.root, textvariable=self.space)
        self.label_display_2.grid(row=1, column=2, padx=0, pady=0)

        self.accept_button = tk.Button(self.root, text="Accept", state=tk.DISABLED, command=lambda: self.mark_qc_label('accept', 'accept'), bg='green')
        self.accept_button.grid(row=2, column=2, padx=0, pady=0)

        self.review_button = tk.Button(self.root, text="For Review", state=tk.DISABLED, command=lambda: self.mark_qc_label('for_review', 'for_review'), bg='yellow')
        self.review_button.grid(row=3, column=2, padx=10, pady=0)

        self.off_task_button = tk.Button(self.root, text="Off Task", state=tk.DISABLED, command=lambda: self.mark_qc_label('off_task', 'off_task'), bg='orange')
        self.off_task_button.grid(row=4, column=2, padx=10)

        self.add_note_button = tk.Button(self.root, text="Add Note", state=tk.DISABLED, command=lambda: self.mark_qc_label('add_note', 'add_note'))
        self.add_note_button.grid(row=5, column=2, padx=10)

        self.search_button = tk.Button(self.root, text="Search", command=lambda: self.open_popup('search'), state=tk.DISABLED)
        self.search_button.grid(row=6, column=2, padx=10)

        self.search_result_label = tk.Label(self.root, text="")
        self.search_result_label.grid(row=7, column=2, padx=10)
        
    def open_popup(self, button_val):
        def get_text_and_continue():
            entered_text = entry_var.get()
            print("Entered text:", entered_text)
            if button_val == 'search':
                self.search_data(entered_text)
            elif button_val == 'insert':
                self.mark_edit_label(button_val, entered_text)
            else:
                self.mark_edit_label(button_val, entered_text)
            # You can use 'entered_text' as needed
            popup.destroy()  # Close the popup window
            self.root.update()
        
        popup = tk.Toplevel(self.root)
        popup.title("Popup Window")
        
        # Add a textbox (Entry widget) to the popup
        entry_label = tk.Label(popup, text="Enter text:")
        entry_label.pack(padx=10, pady=5)
        
        entry_var = tk.StringVar()
        entry = tk.Entry(popup, textvariable=entry_var)
        entry.pack(padx=10, pady=10)
        
        # Add a "Continue" button to get the entered text and close the popup
        continue_button = tk.Button(popup, text="Continue", command=get_text_and_continue)
        continue_button.pack(pady=10)
    
    def display_csv(self):
        # Clear the Text widget
        self.csv_text.delete(1.0, "end")
        
        # Display the CSV content as a dataframe in the Text widget
        csv_string = self.df.iloc[:, :].to_string(index=True)
        lines = csv_string.split('\n')
        
        for i, line in enumerate(lines, start=1):
            if i == self.current_index + 2:  # Add 2 to account for the header row
                # Highlight the current row (adjust the formatting as needed)
                self.csv_text.insert("end", line + "\n", "highlight")
            else:
                self.csv_text.insert("end", line + "\n")
                
        # Configure the tag for highlighting
        self.csv_text.tag_configure("highlight", background="yellow")

    def refresh(self):
        self.display_csv()
        self.root.update()
        
    def get_time_axis(self):
        return np.linspace(0, self.audio_duration, len(self.audio_data))

    def load_audio(self):
        audio = AudioSegment.from_file(self.audio_file_path)
        return np.array(audio.get_array_of_samples()) / 32768.0  # Normalize to the range [-1, 1]

    def zoom_in(self):
        # Check if max zoom count is reached
        if self.zoom_count >= self.max_zoom_count:
            return
        
        # Calculate new x-axis range
        x_range_length = self.x_range[1] - self.x_range[0]
        new_x_range_length = x_range_length * self.zoom_factor
        cursor_position = self.red_cursor_line.get_xdata()[0]
        
        # Calculate new min and max
        if cursor_position - new_x_range_length / 2 < 0 or cursor_position + new_x_range_length / 2 > self.initial_x_range[1]:
            if cursor_position - new_x_range_length / 2 < 0:
                new_min = 0
                new_max = new_min + new_x_range_length
            else:
                new_max = self.initial_x_range[1]
                new_min = new_max - new_x_range_length
        else:
            new_min = cursor_position - new_x_range_length / 2
            new_max = cursor_position + new_x_range_length / 2
        
        # Update x-axis range
        self.x_range = (new_min, new_max)
        
        # Increment zoom count
        self.zoom_count += 1
        
        # Redraw the figure
        self.ax.set_xlim(self.x_range)
        self.canvas.draw()
        
    def zoom_out(self):
        # Check if at the original range
        if self.x_range[1] - self.x_range[0] >= self.initial_x_range[1] - self.initial_x_range[0]:
            print(self.x_range)
            print(self.initial_x_range)
            return
        
        # Calculate new x-axis range for zooming out
        x_range_length = self.x_range[1] - self.x_range[0]
        new_x_range_length = x_range_length / self.zoom_factor
        cursor_position = self.red_cursor_line.get_xdata()[0]
        
        # Calculate new min and max
        if cursor_position - new_x_range_length / 2 < 0 or cursor_position + new_x_range_length / 2 > self.initial_x_range[1]:
            if cursor_position - new_x_range_length / 2 < 0:
                new_min = 0
                new_max = new_min + new_x_range_length
            else:
                new_max = self.initial_x_range[1]
                new_min = new_max - new_x_range_length
        else:
            new_min = cursor_position - new_x_range_length / 2
            new_max = cursor_position + new_x_range_length / 2
        
        # Update x-axis range
        self.x_range = (new_min, new_max)
        
        # Decrement zoom count
        self.zoom_count -= 1
        
        # Redraw the figure
        self.ax.set_xlim(self.x_range)
        self.canvas.draw()
    
    def init_plot(self):
        # creating audio visualization
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.get_time_axis(), self.audio_data)
        # Playback cursor
        self.red_cursor_line = self.ax.axvline(x=self.cursor_position, color='red', linestyle='-', linewidth=2)
        # Tracking cursor
        self.green_cursor_line, = self.ax.plot([0, 0], [-1, 1], color='green', linestyle='-', linewidth=2, visible=False)
        # Current/edit word
        self.yellow_start_line = self.ax.axvline(x=self.start_section, color='yellow', linestyle='-', linewidth=1, visible=False)
        self.red_highlight_space = plt.axvspan(self.start_section, self.end_section, color='red', alpha=0, label='Highlighted Area')
        self.yellow_end_line = self.ax.axvline(x=self.end_section, color='yellow', linestyle='-', linewidth=1, visible=False)
        # Insert word
        self.blue_start_line = self.ax.axvline(x=self.start_section, color='blue', linestyle='-', linewidth=1, visible=False)
        self.blue_highlight_space = plt.axvspan(self.start_section, self.end_section, color='blue', alpha=0, label='Insert Area', visible=False)
        self.blue_end_line = self.ax.axvline(x=self.end_section, color='blue', linestyle='-', linewidth=1, visible=False)
        
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Amplitude')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=2, padx=10, pady=10)
        return self.red_cursor_line, self.green_cursor_line

    def update_plot(self):
        self.root.update()
        cursor_line_x = self.cursor_position
        self.red_cursor_line.set_xdata([cursor_line_x, cursor_line_x])
        # Current/edit
        self.yellow_start_line.set_visible(True)
        self.yellow_start_line.set_xdata([self.start_section, self.start_section])
        self.red_highlight_space.set_alpha(0.3)
        self.red_highlight_space.set_xy([[self.start_section, plt.ylim()[0]], [self.start_section, plt.ylim()[1]],
                       [self.end_section, plt.ylim()[1]], [self.end_section, plt.ylim()[0]]])
        self.yellow_end_line.set_visible(True)
        self.yellow_end_line.set_xdata([self.end_section, self.end_section])
        
        # Insert
        self.blue_start_line.set_xdata([self.insert_start_section, self.insert_start_section])
        self.blue_highlight_space.set_alpha(0.3)
        self.blue_highlight_space.set_xy([[self.insert_start_section, plt.ylim()[0]], [self.insert_start_section, plt.ylim()[1]],
                       [self.insert_end_section, plt.ylim()[1]], [self.insert_end_section, plt.ylim()[0]]])
        self.blue_end_line.set_xdata([self.insert_end_section, self.insert_end_section])
        
        self.green_cursor_line.set_xdata([self.mouse_position, self.mouse_position])
        
        self.canvas.draw()  # Redraw the canvas
        return self.red_cursor_line, self.green_cursor_line

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
            if self.onset_position != None:
                self.offset_position = event.xdata
                if self.edit:
                    self.end_section = self.offset_position
                if self.insert:
                    self.blue_end_line.set_visible(True)
                    self.blue_highlight_space.set_visible(True)
                    self.insert_end_section = self.offset_position
                self.update_plot()
                self.root.update()   
                print(f"Clicked at time: {self.offset_position} seconds")
            else:
                self.onset_position = event.xdata
                if self.edit:
                    self.start_section = self.onset_position
                if self.insert:
                    self.blue_start_line.set_visible(True)
                    self.insert_start_section = self.onset_position
                self.update_plot()
                self.root.update()
                print(f"Clicked at time: {self.onset_position} seconds")
        
    def restart(self):
        self.current_index = 0
        self.start_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.DISABLED)
        self.start_insert_button.config(state=tk.DISABLED)
        self.save_insert_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)
        self.next_row_button.config(state=tk.DISABLED)
        self.next_file_button.config(state=tk.DISABLED)
        self.accept_button.config(state=tk.DISABLED)
        self.start_edit_button.config(state=tk.DISABLED)
        self.save_edit_button.config(state=tk.DISABLED)
        self.drop_button.config(state=tk.DISABLED)
        self.review_button.config(state=tk.DISABLED)
        self.off_task_button.config(state=tk.DISABLED)
        self.add_note_button.config(state=tk.NORMAL)
        self.off_task_button.config(state=tk.NORMAL)
        self.word = ''
        self.display_csv()
        self.label_text.set(self.word)
    
    def search_data(self, search_query):
#         search_query = self.search_entry.get()

        # Check if the search query is numeric (time in milliseconds)
        if search_query.isdigit():
            t = self.find_closest_time(int(search_query))
            self.display_info_and_play_audio(t)
        else:
            # Search for the word in Column1 (case-insensitive)
            self.display_info_and_play_audio(self.find_matching_word(search_query.lower()))

    def display_info_and_play_audio(self, index):
        if 0 <= index < len(self.df):
            self.start_button.config(state=tk.DISABLED)
            self.start_showing_text = True
            self.restart_button.config(state=tk.NORMAL)
            self.next_row_button.config(state=tk.NORMAL)
            self.next_file_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
            self.accept_button.config(state=tk.NORMAL)
            self.start_edit_button.config(state=tk.NORMAL)
            self.save_edit_button.config(state=tk.DISABLED)
            self.review_button.config(state=tk.NORMAL)
            self.off_task_button.config(state=tk.NORMAL)
            self.add_note_button.config(state=tk.NORMAL)
            self.off_task_button.config(state=tk.NORMAL)
            self.start_insert_button.config(state=tk.NORMAL)
            self.save_insert_button.config(state=tk.DISABLED)
            self.drop_button.config(state=tk.NORMAL)
            
            self.root.update()
            self.search_result_label.config(text="")
            self.current_index = index
            self.get_audio_segment()
            self.current_index -= 1 
            self.next_playback()
        else:
            self.search_result_label.config(text="Please check spelling/submitted Start Time.")

    def find_matching_word(self, search_word):
        # Search for the word in Column1 (case-insensitive)
        matching_rows = self.df[self.df['word'].str.lower().eq(search_word)]
        if not matching_rows.empty:
            return matching_rows.index[0]
        else:
            return -1  # Indicate that the word was not found in the dataframe

    def find_closest_time(self, search_time):
        # Find the closest reported value in onset
        closest_index = np.argmin(np.abs(self.df['onset'] - search_time).values)
        return closest_index

    def get_audio_duration(self, file_path):
        # Load the audio file
        audio = AudioSegment.from_file(file_path)
        
        # Get the duration in milliseconds
        duration_ms = len(audio)
        
        return duration_ms

    def play_full_audio(self):
        pygame.init()
        pygame.mixer.init()
    
        try:
            pygame.mixer.music.load(self.audio_file_path)
            self.start_time = 0
            self.end_time = self.get_audio_duration(self.audio_file_path) - 50

            self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.canvas.mpl_connect('button_press_event', self.on_click)
            self.canvas.mpl_connect('button_press_event', self.on_click)
    
            # Start playback
            pygame.mixer.music.play()
    
            # Wait for a short time to allow playback to start
            time.sleep(0.01)
            
            self.cursor_position = self.start_time/1000
    
            # Wait for the specified duration
            while pygame.mixer.music.get_pos() < self.end_time - self.start_time:
                self.root.update()
                
                self.update_plot()  # Call update_plot to update the cursor position
              
                self.cursor_position = (self.start_time + pygame.mixer.music.get_pos()) / 1000.0  # Elapsed time in seconds
                    
                time.sleep(0.0001)
    
        except pygame.error as e:
            print(f"Error: {e}")
    
        finally:
            pygame.mixer.quit()
            pygame.quit()
        
    def play_audio_segment(self):
        pygame.init()
        pygame.mixer.init()
    
        try:
            pygame.mixer.music.load(self.audio_file_path)
            
            self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.canvas.mpl_connect('button_press_event', self.on_click)
            self.canvas.mpl_connect('button_press_event', self.on_click)
    
            # Start playback
            pygame.mixer.music.play()
    
            # Wait for a short time to allow playback to start
            time.sleep(0.01)
    
            # Set the starting position
            pygame.mixer.music.set_pos(self.start_time / 1000.0)
            self.cursor_position = self.start_time/1000
    
            # Wait for the specified duration
            while pygame.mixer.music.get_pos() < self.end_time - self.start_time:
                self.root.update()
                
                self.update_plot()  # Call update_plot to update the cursor position
              
                self.cursor_position = (self.start_time + pygame.mixer.music.get_pos()) / 1000.0  # Elapsed time in seconds
                    
                time.sleep(0.0001)
    
        except pygame.error as e:
            print(f"Error: {e}")
    
        finally:
            pygame.mixer.quit()
            pygame.quit()
    
    def start_playback(self):
        self.label_text.set('')
        self.start_button.config(state=tk.DISABLED)
        self.start_showing_text = True
        self.restart_button.config(state=tk.NORMAL)
        self.next_row_button.config(state=tk.NORMAL)
        self.next_file_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.NORMAL)
        self.accept_button.config(state=tk.NORMAL)
        self.start_edit_button.config(state=tk.NORMAL)
        self.save_edit_button.config(state=tk.DISABLED)
        self.review_button.config(state=tk.NORMAL)
        self.start_insert_button.config(state=tk.NORMAL)
        self.save_insert_button.config(state=tk.DISABLED)
        self.drop_button.config(state=tk.NORMAL)
        self.add_note_button.config(state=tk.NORMAL)
        self.off_task_button.config(state=tk.NORMAL)
        self.zoom_in_button.config(state=tk.NORMAL)
        self.zoom_out_button.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)

        self.display_word()
        self.root.update()

        if AUDIO_ENABLED:
            # Check if there's a valid audio segment
            if self.audio_segment is not None:
                self.play_audio_segment()

    def get_audio_segment(self):
        if AUDIO_ENABLED:
            self.start_time = (self.df.iloc[self.current_index, 1] * 1000) - 500
            self.cursor_position = self.start_time
            # if it's the last word in the file
            if self.current_index == len(self.df) - 1:
                # if the buffer reaches beyond the end of the audio clip
                if self.get_audio_duration(self.audio_file_path) < (self.df.iloc[self.current_index, 2] * 1000) + 2000:
                    self.end_time = self.get_audio_duration(self.audio_file_path)
                # otherwise, just use the buffer
                else:
                    self.end_time = (self.df.iloc[self.current_index, 2] * 1000) + 2000
            # if it isn't the last word in the file 
            else:
                self.end_time = (self.df.iloc[self.current_index, 2] * 1000) + 2000

            self.start_section = (self.df.iloc[self.current_index, 1])
            self.end_section = (self.df.iloc[self.current_index, 2])

            return True
        else:
            return None

    def display_word(self):
        if self.df is not None and self.current_index < len(self.df):
            if self.start_showing_text:
                self.word = self.df.iloc[self.current_index, 0]
                self.label_text.set(f'Current word: {self.word}')
                self.audio_segment = self.get_audio_segment()

    def next_playback(self):
        self.root.update()
        self.onset_position = None
        self.offset_position = None
        self.edit = False
        self.insert = False
        # Check if there are more rows in the DataFrame
        if self.current_index < len(self.df) - 1:
            # Move to the next row in the dataframe
            self.current_index += 1
        
            # Display the word for the new row
            self.display_word()

            # Update csv display
            self.display_csv()
            self.root.update()
        
            # Play the audio for the new row
            if AUDIO_ENABLED:
                self.audio_segment = self.get_audio_segment()
                self.play_audio_segment()
        
            # Check if it's the last row and if a validation button has been pressed
            if self.current_index == len(self.df) - 1 and self.validation_pressed:
                self.next_row_button.config(state=tk.DISABLED)
    
            self.start_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_row_button.config(state=tk.NORMAL)
            self.next_file_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
            self.accept_button.config(state=tk.NORMAL)
            self.start_edit_button.config(state=tk.NORMAL)
            self.save_edit_button.config(state=tk.DISABLED)
            self.review_button.config(state=tk.NORMAL)
            self.off_task_button.config(state=tk.NORMAL)
            self.add_note_button.config(state=tk.NORMAL)
            self.start_insert_button.config(state=tk.NORMAL)
            self.save_insert_button.config(state=tk.DISABLED)
            self.drop_button.config(state=tk.NORMAL)
            self.zoom_in_button.config(state=tk.NORMAL)
            self.zoom_out_button.config(state=tk.NORMAL)
            self.search_button.config(state=tk.NORMAL)
        
        else:
            # If it's not the last file
            if self.current_file != len(self.files):
                self.finished_file = True
                self.next_file_button.config(state=tk.NORMAL)
                self.label_text.set('Finished validating this file. Press "Next File" to continue.')
            # If it is the last file
            else:
                self.next_file_button.config(state=tk.DISABLED)
            
            self.start_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
            self.next_row_button.config(state=tk.DISABLED)
            self.accept_button.config(state=tk.DISABLED)
            self.start_edit_button.config(state=tk.DISABLED)
            self.save_edit_button.config(state=tk.DISABLED)
            self.review_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
            self.add_note_button.config(state=tk.DISABLED)
            self.start_insert_button.config(state=tk.DISABLED)
            self.save_insert_button.config(state=tk.DISABLED)
            self.drop_button.config(state=tk.DISABLED)
            self.zoom_in_button.config(state=tk.DISABLED)
            self.zoom_out_button.config(state=tk.DISABLED)
            self.search_button.config(state=tk.DISABLED)
                
        # Save the data
        self.save_data()

    def save_data(self):
        # Save the edited dataframe to a new CSV file
        directory = f'{self.edited_folder}/{os.path.basename(os.path.dirname(self.file_path))}'
        os.makedirs(directory, exist_ok=True)
        edited_file_path = os.path.join(directory, f'{os.path.splitext(os.path.basename(self.file_path))[0]}_edited_file.csv')
        self.df.to_csv(edited_file_path, index=False)

        print(f"Changes saved to: {edited_file_path}")

    def import_data(self, file):
        if not file:
            try:
                folder_path = filedialog.askdirectory(title="Select Folder")
                self.files = []
                for filename in os.listdir(folder_path):
                    if filename.endswith(".csv") and "Recall" in filename:
                        self.file_path = os.path.join(folder_path, filename)
                        self.files.append(self.file_path)
                self.current_file = 0
                self.files.sort()
            except Exception as e:
                print(e)
                
        self.file_path = self.files[self.current_file]
        # self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        dir = self.file_path.split('/')
        self.name = dir[-1].split('_')[0]
        self.task_text.set(f'Now displaying: {self.name}')
        self.audio_file_path = (f"{'/'.join(dir[:-1])}/{self.name}.wav")
        audio_list = self.audio_file_path.split('/')
        audio_list[-3] = 'RAVLT'
        self.audio_file_path = '/'.join(audio_list)
        if self.file_path:
            self.df = pd.read_csv(self.file_path)
            # Create a copy of the original dataframe (replace this with your logic)
            self.df = self.df.copy()
            # Display CSV content in the Text widget
            self.display_csv()
            # Replace this with logic to load audio duration
            self.audio_duration = self.get_audio_duration(self.audio_file_path)/1000
            self.audio_data = self.load_audio()
            self.initial_x_range = (0, self.audio_duration)
            self.x_range = self.initial_x_range
            self.init_plot()
                
            # Add Column6 if not already present
            if 'quality_check_label' not in self.df.columns:
                self.df['quality_check_label'] = pd.Series([float('nan')]*len(self.df), dtype='float')

            if 'note' not in self.df.columns:
                self.df['note'] = pd.Series([float('nan')]*len(self.df), dtype='float')
                
            # Enable buttons after importing data
            self.start_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_row_button.config(state=tk.DISABLED)
            self.next_file_button.config(state=tk.DISABLED)
            self.accept_button.config(state=tk.DISABLED)
            self.start_edit_button.config(state=tk.DISABLED)
            self.save_edit_button.config(state=tk.DISABLED)
            self.review_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
            self.add_note_button.config(state=tk.DISABLED)
            self.drop_button.config(state=tk.DISABLED)
            self.start_insert_button.config(state=tk.DISABLED)
            self.save_insert_button.config(state=tk.DISABLED)
            self.whole_audio_button.config(state=tk.NORMAL)
            self.search_button.config(state=tk.DISABLED)
            self.validation_pressed = False  # Reset validation flag
            self.current_index = 0  # Reset the index when a new CSV is imported

    def next_file(self):
        self.edit = False
        self.insert = False
        if self.current_file == len(self.files) - 1:
            self.label_text.set("Finished validating all files.")
            self.start_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.next_row_button.config(state=tk.DISABLED)
            self.accept_button.config(state=tk.DISABLED)
            self.start_edit_button.config(state=tk.DISABLED)
            self.save_edit_button.config(state=tk.DISABLED)
            self.review_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
            self.start_insert_button.config(state=tk.DISABLED)
            self.save_insert_button.config(state=tk.DISABLED)
            self.drop_button.config(state=tk.DISABLED)
            self.add_note_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
        elif self.finished_file:
            self.current_file += 1
            self.current_index = 0
            self.import_data(True)
            self.label_text.set("Press the 'Start' button to begin the next file")
        
    def mark_qc_label(self, label, qc_label_value):
        # Check if there's a value in Column1 before updating quality_check_label
        if pd.notna(self.df.at[self.current_index, 'word']):
            self.df.at[self.current_index, 'editor'] = self.initials
            if self.df.loc[self.current_index, 'quality_check_label'] != 'insert':
                self.df.at[self.current_index, 'quality_check_label'] = qc_label_value
            self.validation_pressed = True  # Set validation flag 
            
            if label == 'add_note':  
              # Open a dialog for entering text
                user_input = simpledialog.askstring("Input", "Add note in space below:")
                if user_input is not None:
                    self.df.at[self.current_index, 'note'] = user_input

            self.root.update()
            self.save_data()
            
    def mark_edit_label(self, label, data):
        # Check if there's a value in Column1 before updating quality_check_label
        if pd.notna(self.df.at[self.current_index, 'word']):
            self.df.at[self.current_index, 'editor'] = self.initials

            if label == 'drop':
                self.df = self.df.drop(self.current_index).reset_index(drop=True)
                self.current_index -= 1
            else:
                if label == 'edit':
                    if self.edit:
                        self.edit_data(data)
                        self.save_edit_button.config(state=tk.DISABLED)
                    else:
                        self.edit = True
                        self.start_edit_button.config(state=tk.DISABLED)
                        self.save_edit_button.config(state=tk.NORMAL)
                elif label == 'insert':
                    if self.insert:
                        if data != '':
                            self.insert_data(data)
                            self.save_insert_button.config(state=tk.DISABLED)
                            self.blue_end_line.set_visible(False)
                            self.blue_start_line.set_visible(False)
                            self.blue_highlight_space.set_visible(False)
                        else:
                            messagebox.showinfo("Insert Popup", "Make you've input a word into the space below")
                    else:
                        self.insert = True
                        self.start_insert_button.config(state=tk.DISABLED)
                        self.save_insert_button.config(state=tk.NORMAL)
            
            self.root.update()
            
            # Save the data
            self.save_data()
            
    def edit_data(self, data):
        if data == '':
            data = self.word
            confidence = self.df.loc[self.current_index, 'confidence']
        else:
            confidence = np.nan
        if self.onset_position == None:
            self.onset_position = self.df.loc[self.current_index, 'onset']
        if self.offset_position == None:
            self.offset_position = self.df.loc[self.current_index, 'offset']
        edit_label = 'edit'
        if self.df.loc[self.current_index, 'quality_check_label'] == 'insert':
            edit_label = 'insert'
        self.df.loc[self.current_index] = [data, self.start_section, self.end_section, confidence] + [edit_label] + [np.nan] + [self.initials] + [np.nan] * (self.df.shape[1] - 7)
        
    def insert_data(self, data):
        index_to_insert = self.current_index + 1 
        
        # Create a new row with None values
        new_row = [data, self.insert_start_section, self.insert_end_section] + [np.nan] + ['insert'] + [np.nan] + [self.initials] + [np.nan] * (self.df.shape[1] - 7)  
        
        # Adjust as needed# Convert the new row into a DataFrame
        new_df = pd.DataFrame([new_row], columns=self.df.columns)
        
        # Concatenate the existing DataFrame with the new DataFrame
        self.df = pd.concat([self.df.iloc[:index_to_insert], new_df, self.df.iloc[index_to_insert:]], ignore_index=True)

# Main program
if __name__ == "__main__":
    # Create a root window for entering initials
    initials_root = tk.Tk()
    initials_app = InitialsEntryApp(initials_root, initials_callback=lambda initials: initials_root.destroy())
    initials_root.mainloop()

    # Use the entered initials stored in the InitialsEntryApp instance
    entered_initials = initials_app.entered_initials

    # Create a root window for the audio player app
    audio_player_root = tk.Tk()
    app = AudioPlayerApp(audio_player_root, entered_initials)
    audio_player_root.mainloop()
    