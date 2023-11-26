import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import shutil
import threading
from tkinter import ttk


class App:
    def __init__(self, root):
        self.root = root
        root.title("Abaqus ODB Batch export")
        width = 662
        height = 435
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        align_string = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(align_string)
        root.resizable(width=False, height=False)

        self.folder_list = []  # List to store full file paths
        self.list_box = tk.Listbox(root, selectmode=tk.MULTIPLE)  # Allow multiple selections
        self.list_box["borderwidth"] = "1px"
        self.list_box["fg"] = "#333333"
        self.list_box["justify"] = "left"
        self.list_box.place(x=20, y=20, width=499, height=400)

        button_add_files = tk.Button(root)
        button_add_files["anchor"] = "w"
        button_add_files["bg"] = "#f0f0f0"
        button_add_files["fg"] = "#000000"
        button_add_files["justify"] = "center"
        button_add_files["text"] = "+ add folder"
        button_add_files["relief"] = "raised"
        button_add_files.place(x=530, y=20, width=110, height=30)
        button_add_files["command"] = self.button_add_clicked

        button_add_files = tk.Button(root)
        button_add_files["anchor"] = "w"
        button_add_files["bg"] = "#f0f0f0"
        button_add_files["fg"] = "#000000"
        button_add_files["justify"] = "center"
        button_add_files["text"] = "+ add project"
        button_add_files["relief"] = "raised"
        button_add_files.place(x=530, y=60, width=110, height=30)
        button_add_files["command"] = self.button_add_project_clicked

        button_remove_files = tk.Button(root)
        button_remove_files["anchor"] = "w"
        button_remove_files["bg"] = "#f0f0f0"
        button_remove_files["fg"] = "#000000"
        button_remove_files["justify"] = "center"
        button_remove_files["text"] = "- remove folder"
        button_remove_files.place(x=530, y=100, width=110, height=30)
        button_remove_files["command"] = self.button_remove_clicked

        button_up = tk.Button(root)
        button_up["anchor"] = "w"
        button_up["bg"] = "#f0f0f0"
        button_up["fg"] = "#000000"
        button_up["justify"] = "center"
        button_up["text"] = "˄ move up"
        button_up.place(x=530, y=220, width=110, height=30)
        button_up["command"] = self.button_move_up

        button_down = tk.Button(root)
        button_down["anchor"] = "w"
        button_down["bg"] = "#f0f0f0"
        button_down["fg"] = "#000000"
        button_down["justify"] = "center"
        button_down["text"] = "˅ move down"
        button_down.place(x=530, y=260, width=110, height=30)
        button_down["command"] = self.button_move_down

        button_process = tk.Button(root)
        button_process["anchor"] = "w"
        button_process["bg"] = "#f0f0f0"
        button_process["fg"] = "#000000"
        button_process["justify"] = "center"
        button_process["text"] = "> export time data"
        button_process["font"] = ('TkDefaultFont', 9, 'bold')
        button_process.place(x=530, y=390, width=110, height=30)
        button_process["command"] = self.button_process_clicked
        self.button_process = button_process

        pb = ttk.Progressbar(
            root,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )
        self.pb_place_attributes = {
            'x': 530,
            'y': 350,
            'width': 110,
            'height': 30
        }
        self.progress_bar = pb

    def button_add_clicked(self):
        folder_path = filedialog.askdirectory()
        self.folder_list.append(folder_path)
        self.list_box.insert(tk.END, os.path.basename(folder_path))

    def button_add_project_clicked(self):
        folder_path = filedialog.askdirectory()
        sub_folders = get_sub_folders(folder_path)
        for sub_folder in sub_folders:
            self.folder_list.append(sub_folder)
            self.list_box.insert(tk.END, "{}\\{}".format(os.path.basename(folder_path), os.path.basename(sub_folder)))

    def button_remove_clicked(self):
        selected_indices = self.list_box.curselection()
        if selected_indices:
            self.remove_folder(selected_indices)

    def remove_folder(self, selected_indices):
        selected_indices = list(selected_indices)
        selected_indices.sort(reverse=True)  # Delete items from the end to avoid index shifts
        for selected_index in selected_indices:
            selected_file = self.folder_list[selected_index]
            self.folder_list.pop(selected_index)
            self.list_box.delete(selected_index)
            print(f"Removed file: {selected_file}")

    def button_move_up(self):
        selected_indices = self.list_box.curselection()
        if selected_indices:
            for selected_index in selected_indices:
                if selected_index > 0:
                    selected_file = self.folder_list[selected_index]
                    self.folder_list[selected_index] = self.folder_list[selected_index - 1]
                    self.folder_list[selected_index - 1] = selected_file
                    self.list_box.delete(selected_index)
                    self.list_box.insert(selected_index - 1, os.path.basename(selected_file))

    def button_move_down(self):
        selected_indices = self.list_box.curselection()
        if selected_indices:
            selected_indices = list(selected_indices)
            selected_indices.sort(reverse=True)  # Move down from the end to avoid conflicts
            for selected_index in selected_indices:
                if selected_index < len(self.folder_list) - 1:
                    selected_folder = self.folder_list[selected_index]
                    self.folder_list[selected_index] = self.folder_list[selected_index + 1]
                    self.folder_list[selected_index + 1] = selected_folder
                    self.list_box.delete(selected_index)
                    self.list_box.insert(selected_index + 1, os.path.basename(selected_folder))

    def button_process_clicked(self):
        self.button_process.config(state="disabled")

        while len(self.folder_list):

            output_folder = self.folder_list[0]

            # Run the command in CMD
            py_script_name = "history_export_helper.py"
            command = f"abaqus cae noGUI={py_script_name} -- \"{output_folder}\" \"{output_folder}_history\""
            print(command)
            proc = subprocess.Popen(command, shell=True)
            self.progress_bar.place(**self.pb_place_attributes)
            self.progress_bar.start()
            original_list_box_text = self.list_box.get(0)
            self.list_box.delete(0)
            self.list_box.insert(0, "{} (processing ...)".format(original_list_box_text))
            while proc.poll() is None:
                root.update()
            self.progress_bar.stop()
            self.progress_bar.place_forget()

            self.remove_folder([0])

        self.button_process.config(state="active")


def run_command(command):
    process = subprocess.Popen(command, shell=True)
    process.communicate()  # Wait for the command to complete


def get_sub_folders(folder_path):
    sub_folders = []

    # Check if the provided path is a directory
    if os.path.isdir(folder_path):
        # Get a list of all items (files and subfolders) in the directory
        items = os.listdir(folder_path)

        # Iterate through each item
        for item in items:
            item_path = os.path.join(folder_path, item)

            # Check if the item is a directory
            if os.path.isdir(item_path):
                # If it is a directory, add it to the list of subfolders
                sub_folders.append(item_path)

    return sub_folders


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
