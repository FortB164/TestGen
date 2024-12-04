import os
import tkinter as tk
from tkinter import filedialog, messagebox

def select_and_filter_files():
    # Hide the main Tkinter window
    root = tk.Tk()
    root.withdraw()

    # Directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    while True:
        # Ask the user to select a directory
        file_path = filedialog.askdirectory(title="Select a directory containing code files")
        
        if not file_path:
            messagebox.showinfo("No Directory Selected", "You did not select a directory.")
            return

        # Check if the selected directory is the same as the script's directory
        if os.path.abspath(file_path) == script_directory:
            messagebox.showwarning("Invalid Directory", "You cannot select the same directory as the script. Please select a different directory.")
        else:
            break  # Valid directory selected, exit the loop

    # List of programming file extensions
    extensions = ('.cpp', '.py', '.java', '.c', '.js', '.html', '.css', '.swift', '.go', '.cs', 
                  '.kt', '.pl', '.php', '.rb', '.lua', '.sh', '.sql', '.r', '.tcl', '.vb')

    # List files with the specified extensions
    files = [os.path.join(file_path, file) for file in os.listdir(file_path) if file.endswith(extensions) and '_test' not in file]

    if not files:
        messagebox.showinfo("No Files Found", "No programming files found in the selected directory.")
    else:
        # Display the list of files
        print(f"Programming files in '{file_path}':")
        for f in files:
            print(f)

        # Save results to a file in the same directory as UI.py
        save_path = os.path.join(script_directory, "programming_files_list.txt")

        with open(save_path, 'w') as file:
            file.write("\n".join(files))

        messagebox.showinfo("File Saved", f"Results saved to: {save_path}")

# Run the function
if __name__ == "__main__":
    select_and_filter_files()
