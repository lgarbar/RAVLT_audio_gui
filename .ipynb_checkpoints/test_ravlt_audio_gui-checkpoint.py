import tkinter as tk
from tkinter import filedialog, simpledialog
import os
import pandas as pd
import numpy as np
import time
import os
import shutil

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
        self.audio_segment = None
        self.file_path = None
        self.validation_pressed = False
        self.start_showing_text = False
        self.finished_file = False

        self.initials = initials
        
        # Create an 'edited' folder if it doesn't exist
        self.edited_folder = 'edited'
        os.makedirs(self.edited_folder, exist_ok=True)

        self.create_widgets()

    def create_widgets(self):
        self.start_button = tk.Button(self.root, text="Start", state=tk.DISABLED, command=self.start_playback)
        self.start_button.pack()

        self.restart_button = tk.Button(self.root, text="Restart", state=tk.DISABLED, command=self.restart)
        self.restart_button.pack()

        self.next_button = tk.Button(self.root, text="Next", state=tk.DISABLED, command=self.next_playback)
        self.next_button.pack()

        self.save_button = tk.Button(self.root, text="Save", state=tk.DISABLED, command=self.save_data)
        self.save_button.pack()

        self.import_button = tk.Button(self.root, text="Import", command=lambda: self.import_data(False))
        self.import_button.pack()
        
        self.label_text = tk.StringVar()
        self.label_display_1 = tk.Label(self.root, textvariable=self.label_text)
        self.label_display_1.pack()

        self.space = tk.StringVar()
        self.space.set('Quality Check')
        self.label_display_2 = tk.Label(self.root, textvariable=self.space)
        self.label_display_2.pack()

        self.correct_button = tk.Button(self.root, text="Correct", state=tk.DISABLED, command=lambda: self.mark_qc_label('Correct', 'Correct'), bg='green')
        self.correct_button.pack()

        self.incorrect_button = tk.Button(self.root, text="Incorrect", state=tk.DISABLED, command=lambda: self.mark_qc_label('Incorrect', 'Incorrect'), bg='red')
        self.incorrect_button.pack()

        self.space = tk.StringVar()
        self.space.set('Validation Check')
        self.label_display_3 = tk.Label(self.root, textvariable=self.space)
        self.label_display_3.pack()

        self.valid_button = tk.Button(self.root, text="Valid", state=tk.DISABLED, command=lambda: self.mark_val_label('Valid', 'Valid'), bg='purple')
        self.valid_button.pack()
        
        self.intrusion_button = tk.Button(self.root, text="Intrusion", state=tk.DISABLED, command=lambda: self.mark_val_label('Intrusion', 'Intrusion'), bg='yellow')
        self.intrusion_button.pack()

        self.repetition_button = tk.Button(self.root, text="Repetition", state=tk.DISABLED, command=lambda: self.mark_val_label('Repetition', 'Repetition'), bg='blue')
        self.repetition_button.pack()

        self.off_task_button = tk.Button(self.root, text="Off Task", state=tk.DISABLED, command=lambda: self.mark_val_label('Off Task', 'Off Task'), bg='orange')
        self.off_task_button.pack()

        # self.relabel_entry = tk.Entry(self.root)
        # self.relabel_entry.pack()
        
        self.search_button = tk.Button(self.root, text="Search", command=self.search_data)
        self.search_button.pack()

        self.search_result_label = tk.Label(self.root, text="")
        self.search_result_label.pack()

        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()
        
    def restart(self):
        self.current_index = 0
        self.start_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.import_button.config(state=tk.NORMAL)
        self.correct_button.config(state=tk.DISABLED)
        self.incorrect_button.config(state=tk.DISABLED)
        self.valid_button.config(state=tk.DISABLED)
        self.intrusion_button.config(state=tk.DISABLED)
        self.repetition_button.config(state=tk.DISABLED)
        self.off_task_button.config(state=tk.DISABLED)
        self.word = ''
        self.label_text.set(self.word)
    
    def search_data(self):
        search_query = self.search_entry.get()

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
            self.next_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.import_button.config(state=tk.DISABLED)
            self.qc_checked = False
            self.correct_button.config(state=tk.NORMAL)
            self.incorrect_button.config(state=tk.NORMAL)
            self.val_checked = False
            self.valid_button.config(state=tk.DISABLED)
            self.intrusion_button.config(state=tk.DISABLED)
            self.repetition_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
            
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

    def play_audio_segment(self):
        pygame.init()
        pygame.mixer.init()
    
        try:
            pygame.mixer.music.load(self.audio_file_path)
            print(f"Playing segment from {self.start_time} ms to {self.end_time} ms")
    
            # Start playback
            pygame.mixer.music.play()
    
            # Wait for a short time to allow playback to start
            time.sleep(0.1)
    
            # Set the starting position
            pygame.mixer.music.set_pos(self.start_time / 1000.0)
    
            # Wait for the specified duration
            while pygame.mixer.music.get_pos() < self.end_time - self.start_time:
                time.sleep(0.001)
    
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
        self.next_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.import_button.config(state=tk.NORMAL)
        self.correct_button.config(state=tk.NORMAL)
        self.incorrect_button.config(state=tk.NORMAL)
        self.qc_checked = True
        self.valid_button.config(state=tk.DISABLED)
        self.intrusion_button.config(state=tk.DISABLED)
        self.repetition_button.config(state=tk.DISABLED)
        self.off_task_button.config(state=tk.DISABLED)

        self.display_word()
        self.root.update()

        if AUDIO_ENABLED:
            # Check if there's a valid audio segment
            if self.audio_segment is not None:
                self.play_audio_segment()

    def get_audio_segment(self):
        if AUDIO_ENABLED:
            self.start_time = (self.df.iloc[self.current_index, 1] * 1000) + 200
            self.end_time = (self.df.iloc[self.current_index, 2] * 1000) + 2000
            if self.get_audio_duration(self.audio_file_path) < self.end_time:
                self.end_time = self.get_audio_duration(self.audio_file_path) - 50
            
            # Mock for testing
            print(f"Load and extract audio from {self.audio_file_path} between {self.start_time} and {self.end_time} milliseconds.")

            return True
        else:
            return None

    def display_word(self):
        if self.df is not None and self.current_index < len(self.df):
            if self.start_showing_text:
                self.word = self.df.iloc[self.current_index, 0]
                self.label_text.set(self.word)
                self.audio_segment = self.get_audio_segment()

    def next_playback(self):
        self.root.update()
        self.qc_checked = True
        self.val_checked = True
        # Check if there are more rows in the DataFrame
        if self.current_index < len(self.df) - 1:
            # Move to the next row in the dataframe
            self.current_index += 1
        
            # Display the word for the new row
            self.display_word()
        
            # Play the audio for the new row
            if AUDIO_ENABLED:
                self.play_audio_segment()
        
            # Check if it's the last row and if a validation button has been pressed
            if self.current_index == len(self.df) - 1 and self.validation_pressed:
                self.next_button.config(state=tk.DISABLED)
    
            self.start_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.import_button.config(state=tk.NORMAL)
            self.correct_button.config(state=tk.NORMAL)
            self.incorrect_button.config(state=tk.NORMAL)
            self.valid_button.config(state=tk.DISABLED)
            self.intrusion_button.config(state=tk.DISABLED)
            self.repetition_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
            
        elif self.current_file != len(self.files):
            self.finished_file = True
            self.next_file()
        
        else:
            self.start_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            self.import_button.config(state=tk.NORMAL)
            self.correct_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.DISABLED)
            self.valid_button.config(state=tk.DISABLED)
            self.intrusion_button.config(state=tk.DISABLED)
            self.repetition_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)

            self.label_text.set('')
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
            print('importing the csv')
            try:
                folder_path = filedialog.askdirectory(title="Select Folder")
                self.files = []
                for filename in os.listdir(folder_path):
                    if filename.endswith(".csv"):
                        self.file_path = os.path.join(folder_path, filename)
                        self.files.append(self.file_path)
                self.current_file = 0
                self.files.sort()
            except Exception as e:
                print(e)
                
        self.file_path = self.files[self.current_file]
        # self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        dir = self.file_path.split('/')
        fname = dir[-1].split('_')[0]
        # csv_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        self.audio_file_path = (f"{'/'.join(dir[:-1])}/{fname}.wav")
        if self.file_path:
            self.df = pd.read_csv(self.file_path)
            # Create a copy of the original dataframe (replace this with your logic)
            self.df = self.df.copy()
            
            # Add Column5 if not already present
            if 'quality_check' not in self.df.columns:
                self.df['quality_check'] = pd.Series([float('nan')]*len(self.df), dtype='float')
                
            # Add Column6 if not already present
            if 'quality_check_label' not in self.df.columns:
                self.df['quality_check_label'] = pd.Series([float('nan')]*len(self.df), dtype='float')
            
            # Add Column7 if not already present
            if 'task_data_label' not in self.df.columns:
                self.df['task_data_label'] = pd.Series(['Valid']*len(self.df), dtype='str') 
           
            # # Add Column8 if not already present
            # if 'editor' not in self.df.columns:
            #     self.df['editor'] = pd.Series([float('nan')]*len(self.df), dtype='float')
                
            # Enable buttons after importing data
            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            self.import_button.config(state=tk.DISABLED)
            self.correct_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.DISABLED)
            self.valid_button.config(state=tk.DISABLED)
            self.intrusion_button.config(state=tk.DISABLED)
            self.repetition_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
            self.validation_pressed = False  # Reset validation flag
            self.current_index = 0  # Reset the index when a new CSV is imported

    def next_file(self):
        if self.current_file == len(self.files) - 1:
            self.label_text.set("Finished validating all files.")
            self.start_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            self.import_button.config(state=tk.NORMAL)
            self.correct_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.DISABLED)
            self.valid_button.config(state=tk.DISABLED)
            self.intrusion_button.config(state=tk.DISABLED)
            self.repetition_button.config(state=tk.DISABLED)
            self.off_task_button.config(state=tk.DISABLED)
        elif self.finished_file:
            self.current_file += 1
            self.import_data(True)
            self.label_text.set("Press the 'Start' button to begin the next file")
        
    def mark_qc_label(self, label, qc_label_value):
        # Check if there's a value in Column1 before updating quality_check_label
        if pd.notna(self.df.at[self.current_index, 'word']):
            if self.qc_checked:
                # Mark the label in quality_check and quality_check_label
                self.df.at[self.current_index, 'quality_check'] = float('nan')
                self.df.at[self.current_index, 'quality_check_label'] = qc_label_value
                self.validation_pressed = True  # Set validation flag
        
                if label == 'Incorrect':
                    # Open a dialog for entering text
                    user_input = simpledialog.askstring("Input", "Enter your text:")
                    if user_input is not None:
                        # Convert the user_input to float before assigning
                        self.df.at[self.current_index, 'quality_check'] = user_input
                else:
                    self.df.at[self.current_index, 'quality_check'] = self.word
                self.qc_checked = False
                self.val_checked = True
                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.next_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
                self.import_button.config(state=tk.NORMAL)
                self.correct_button.config(state=tk.DISABLED)
                self.incorrect_button.config(state=tk.DISABLED)
                self.valid_button.config(state=tk.NORMAL)
                self.intrusion_button.config(state=tk.NORMAL)
                self.repetition_button.config(state=tk.NORMAL)
                self.off_task_button.config(state=tk.NORMAL)

                self.root.update()

            # Save the data
            self.save_data()
            
    def mark_val_label(self, label, qc_label_value):
        # Check if there's a value in Column1 before updating quality_check_label
        if pd.notna(self.df.at[self.current_index, 'word']):
            if self.val_checked:
                self.df.at[self.current_index, 'task_data_label'] = label
                self.df.at[self.current_index, 'editor'] = self.initials
                self.val_checked = False
                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.next_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
                self.import_button.config(state=tk.NORMAL)
                self.correct_button.config(state=tk.DISABLED)
                self.incorrect_button.config(state=tk.DISABLED)
                self.valid_button.config(state=tk.DISABLED)
                self.intrusion_button.config(state=tk.DISABLED)
                self.repetition_button.config(state=tk.DISABLED)
                self.off_task_button.config(state=tk.DISABLED)
                
                self.root.update()
                
                # Move to the next word
                self.next_playback()
            

            # Save the data
            self.save_data()

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
    