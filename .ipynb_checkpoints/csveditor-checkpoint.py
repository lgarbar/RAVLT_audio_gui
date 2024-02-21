import tkinter as tk
from tkinter import ttk
import pandas as pd

class CsvEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Editor")
        self.current_row_index = 0  # Track the current row index

        # Create a frame for the CSV display
        self.csv_frame = ttk.Frame(root)
        self.csv_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create a Text widget to display the CSV content
        self.csv_text = tk.Text(self.csv_frame, wrap="none")
        self.csv_text.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar for the Text widget
        scrollbar_y = ttk.Scrollbar(self.csv_frame, command=self.csv_text.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.csv_text["yscrollcommand"] = scrollbar_y.set

        # Create buttons for navigation and editing
        self.next_button = ttk.Button(root, text="Next", command=self.next_row)
        self.next_button.grid(row=1, column=0, pady=5)

        self.prev_button = ttk.Button(root, text="Previous", command=self.prev_row)
        self.prev_button.grid(row=2, column=0, pady=5)

        # Load CSV data
        self.load_csv("edited/sub-M10902762_ses-MOBI1A_task-ravlt1_run-001_lsl/Block1Recall_timestamped_edited_file_edited_file.csv")

    def load_csv(self, file_path):
        # Load CSV file using pandas
        self.df = pd.read_csv(file_path)

        # Display CSV content in the Text widget
        self.display_csv()

    def display_csv(self):
        # Clear the Text widget
        self.csv_text.delete(1.0, "end")
        
        # Display the CSV content as a dataframe in the Text widget
        csv_string = self.df.iloc[:, :].to_string(index=True)
        lines = csv_string.split('\n')
        
        for i, line in enumerate(lines, start=1):
            if i == self.current_row_index + 2:  # Add 2 to account for the header row
                # Highlight the current row (adjust the formatting as needed)
                self.csv_text.insert("end", line + "\n", "highlight")
            else:
                self.csv_text.insert("end", line + "\n")
                
        # Configure the tag for highlighting
        self.csv_text.tag_configure("highlight", background="yellow")

    def next_row(self):
        # Update the current row index and redisplay the CSV
        self.current_row_index = (self.current_row_index + 1) % len(self.df)
        self.display_csv()

    def prev_row(self):
        # Update the current row index and redisplay the CSV
        self.current_row_index = (self.current_row_index - 1) % len(self.df)
        self.display_csv()

if __name__ == "__main__":
    root = tk.Tk()
    app = CsvEditorApp(root)
    root.mainloop()
