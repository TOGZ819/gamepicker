import os
import random
import subprocess
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

CONFIG_FILE = "config.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def find_exe_files(directories):
    exe_files = set()
    for directory in directories:
        for subfolder in os.listdir(directory):
            subfolder_path = os.path.join(directory, subfolder)
            if os.path.isdir(subfolder_path):
                for file in os.listdir(subfolder_path):
                    if file.endswith(".exe"):
                        exe_files.add(os.path.join(subfolder_path, file))
    return list(exe_files)

def pick_random_exe(exe_files):
    if not exe_files:
        return None
    return random.choice(exe_files)

def run_exe_file(file_path):
    if file_path:
        print(f"Running: {file_path}")
        subprocess.run(file_path, shell=True)

def save_config(directories):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"directories": directories}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("directories", [])
    return []

class GamePickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Game Picker")
        self.root.geometry("800x500")
        self.root.minsize(600, 400)

        self.selected_folders = load_config()
        self.exe_files = []
        self.search_thread = None

        self.setup_ui()

        self.update_folder_listbox()

        if self.selected_folders:
            self.button_search.configure(state=tk.NORMAL)

    def setup_ui(self):
        self.frame_top = ctk.CTkFrame(self.root, corner_radius=10)
        self.frame_top.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.frame_bottom = ctk.CTkFrame(self.root, corner_radius=10)
        self.frame_bottom.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.label_folders = ctk.CTkLabel(self.frame_top, text="Selected Folders:", font=("Arial", 14, "bold"))
        self.label_folders.pack(pady=(10, 5))

        self.listbox_folders = tk.Listbox(self.frame_top, selectmode=tk.SINGLE, width=60, height=5, font=("Arial", 12))
        self.listbox_folders.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)

        self.button_add_folder = ctk.CTkButton(self.frame_top, text="Add Folder", command=self.add_folder, width=120)
        self.button_add_folder.pack(pady=5, side=tk.LEFT, padx=10)

        self.button_remove_folder = ctk.CTkButton(self.frame_top, text="Remove Selected Folder", command=self.remove_folder, width=180)
        self.button_remove_folder.pack(pady=5, side=tk.LEFT, padx=10)

        self.button_search = ctk.CTkButton(self.frame_bottom, text="Search for .exe Files", command=self.start_search_thread, state=tk.DISABLED, width=150)
        self.button_search.pack(pady=10, side=tk.LEFT, padx=10)

        self.progress_bar = ttk.Progressbar(self.frame_bottom, mode="indeterminate", length=200)
        self.progress_bar.pack(pady=10, side=tk.LEFT, padx=10)

        self.label_status = ctk.CTkLabel(self.frame_bottom, text="No .exe files found.", font=("Arial", 12))
        self.label_status.pack(pady=10, side=tk.LEFT, padx=10)

        self.button_pick_game = ctk.CTkButton(self.frame_bottom, text="Pick and Run a Random Game", command=self.pick_and_run_game, state=tk.DISABLED, width=200)
        self.button_pick_game.pack(pady=10, side=tk.LEFT, padx=10)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.update_folder_listbox()
            self.button_search.configure(state=tk.NORMAL)
            save_config(self.selected_folders)

    def remove_folder(self):
        selected_index = self.listbox_folders.curselection()
        if selected_index:
            self.selected_folders.pop(selected_index[0])
            self.update_folder_listbox()
            save_config(self.selected_folders)
            if not self.selected_folders:
                self.button_search.configure(state=tk.DISABLED)

    def update_folder_listbox(self):
        self.listbox_folders.delete(0, tk.END)
        for folder in self.selected_folders:
            self.listbox_folders.insert(tk.END, folder)

    def start_search_thread(self):
        if not self.selected_folders:
            messagebox.showwarning("No Folders Selected", "Please add folders first.")
            return

        self.button_search.configure(state=tk.DISABLED)
        self.button_pick_game.configure(state=tk.DISABLED)
        self.progress_bar.start()

        self.search_thread = threading.Thread(target=self.search_exe_files, daemon=True)
        self.search_thread.start()

        self.root.after(100, self.check_search_thread)

    def search_exe_files(self):
        self.exe_files = find_exe_files(self.selected_folders)
        self.root.event_generate("<<SearchComplete>>")

    def check_search_thread(self):
        if self.search_thread.is_alive():
            self.root.after(100, self.check_search_thread)
        else:
            self.progress_bar.stop()
            self.button_search.configure(state=tk.NORMAL)
            if self.exe_files:
                self.label_status.configure(text=f"Found {len(self.exe_files)} .exe files.")
                self.button_pick_game.configure(state=tk.NORMAL)
            else:
                self.label_status.configure(text="No .exe files found.")
                self.button_pick_game.configure(state=tk.DISABLED)

    def pick_and_run_game(self):
        if not self.exe_files:
            messagebox.showwarning("No Games Found", "No .exe files were found. Please search again.")
            return

        selected_exe = pick_random_exe(self.exe_files)
        if selected_exe:
            self.label_status.configure(text=f"Running: {os.path.basename(selected_exe)}")
            run_exe_file(selected_exe)
        else:
            self.label_status.configure(text="Failed to pick a game.")

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = GamePickerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")