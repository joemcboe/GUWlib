import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import shutil
import threading
from tkinter import ttk

guw_module_path = ".."


class App:
    def __init__(self, root):
        self.root = root
        root.title("Abaqus GUW batch submitter")
        width = 662
        height = 435
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        align_string = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(align_string)
        root.resizable(width=False, height=False)

        self.file_list = []  # List to store full file paths
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
        button_add_files["text"] = "+ add files"
        button_add_files["relief"] = "raised"
        button_add_files.place(x=530, y=20, width=110, height=30)
        button_add_files["command"] = self.button_add_clicked

        button_remove_files = tk.Button(root)
        button_remove_files["anchor"] = "w"
        button_remove_files["bg"] = "#f0f0f0"
        button_remove_files["fg"] = "#000000"
        button_remove_files["justify"] = "center"
        button_remove_files["text"] = "- remove file"
        button_remove_files.place(x=530, y=60, width=110, height=30)
        button_remove_files["command"] = self.button_remove_clicked

        button_up = tk.Button(root)
        button_up["anchor"] = "w"
        button_up["bg"] = "#f0f0f0"
        button_up["fg"] = "#000000"
        button_up["justify"] = "center"
        button_up["text"] = "˄ move up"
        button_up.place(x=530, y=180, width=110, height=30)
        button_up["command"] = self.button_move_up

        button_down = tk.Button(root)
        button_down["anchor"] = "w"
        button_down["bg"] = "#f0f0f0"
        button_down["fg"] = "#000000"
        button_down["justify"] = "center"
        button_down["text"] = "˅ move down"
        button_down.place(x=530, y=220, width=110, height=30)
        button_down["command"] = self.button_move_down

        button_process = tk.Button(root)
        button_process["anchor"] = "w"
        button_process["bg"] = "#f0f0f0"
        button_process["fg"] = "#000000"
        button_process["justify"] = "center"
        button_process["text"] = "> batch process"
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
        file_paths = filedialog.askopenfilenames(filetypes=[("Python Files", "*.py")])
        for file_path in file_paths:
            self.file_list.append(file_path)
            # Display an abbreviated version of the filepath in the listbox
            self.list_box.insert(tk.END, os.path.basename(file_path))

    def button_remove_clicked(self):
        selected_indices = self.list_box.curselection()
        if selected_indices:
            self.remove_file(selected_indices)

    def remove_file(self, selected_indices):
        selected_indices = list(selected_indices)
        selected_indices.sort(reverse=True)  # Delete items from the end to avoid index shifts
        for selected_index in selected_indices:
            selected_file = self.file_list[selected_index]
            self.file_list.pop(selected_index)
            self.list_box.delete(selected_index)
            print(f"Removed file: {selected_file}")

    def button_move_up(self):
        selected_indices = self.list_box.curselection()
        if selected_indices:
            for selected_index in selected_indices:
                if selected_index > 0:
                    selected_file = self.file_list[selected_index]
                    self.file_list[selected_index] = self.file_list[selected_index - 1]
                    self.file_list[selected_index - 1] = selected_file
                    self.list_box.delete(selected_index)
                    self.list_box.insert(selected_index - 1, os.path.basename(selected_file))

    def button_move_down(self):
        selected_indices = self.list_box.curselection()
        if selected_indices:
            selected_indices = list(selected_indices)
            selected_indices.sort(reverse=True)  # Move down from the end to avoid conflicts
            for selected_index in selected_indices:
                if selected_index < len(self.file_list) - 1:
                    selected_file = self.file_list[selected_index]
                    self.file_list[selected_index] = self.file_list[selected_index + 1]
                    self.file_list[selected_index + 1] = selected_file
                    self.list_box.delete(selected_index)
                    self.list_box.insert(selected_index + 1, os.path.basename(selected_file))

    def button_process_clicked(self):
        self.button_process.config(state="disabled")

        while len(self.file_list):

            script_path = self.file_list[0]

            # Extract original_path and script_name
            original_path, script_name = os.path.split(script_path)
            script_name = os.path.splitext(script_name)[0]  # Remove the file extension

            # Create a new directory with the script_name
            new_directory = os.path.join(original_path, "results_{}".format(script_name))
            os.makedirs(new_directory, exist_ok=True)

            # Change directory to original_path
            os.chdir(guw_module_path)

            # Run the command in CMD
            command = f"abaqus cae noGUI=\"{script_path}\""
            print(command)
            proc = subprocess.Popen(command, shell=True)
            self.progress_bar.place(**self.pb_place_attributes)
            self.progress_bar.start()
            original_list_box_text = self.list_box.get(0)
            self.list_box.delete(0)
            self.list_box.insert(0, "{} (writing *.inp-file ...)".format(original_list_box_text))
            while proc.poll() is None:
                root.update()
            self.progress_bar.stop()
            self.progress_bar.place_forget()

            # Look for new *.inp files in original_path
            inp_files = [f for f in os.listdir(original_path) if f.endswith(".inp")]

            # Copy the script to the new_directory
            shutil.copy(script_path, os.path.join(new_directory, script_name + ".py"))

            # Move the *.inp files to the new_directory
            for inp_file in inp_files:
                inp_file_directory = os.path.join(new_directory, os.path.splitext(inp_file)[0])
                os.makedirs(inp_file_directory, exist_ok=True)
                shutil.move(os.path.join(original_path, inp_file), os.path.join(inp_file_directory, inp_file))

            for j, inp_file in enumerate(inp_files):
                inp_file_directory = os.path.join(new_directory, os.path.splitext(inp_file)[0])
                os.chdir(inp_file_directory)
                cmd = "abaqus job={} interactive".format(os.path.splitext(inp_file)[0])

                proc = subprocess.Popen(cmd, shell=True)
                self.progress_bar.place(**self.pb_place_attributes)
                self.progress_bar.start()
                self.list_box.delete(0)
                self.list_box.insert(0, "{} (running job {}...)".format(original_list_box_text, j))
                while proc.poll() is None:
                    root.update()
                self.progress_bar.stop()
                self.progress_bar.place_forget()

            self.remove_file([0])

        self.button_process.config(state="active")


def run_command(command):
    process = subprocess.Popen(command, shell=True)
    process.communicate()  # Wait for the command to complete


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
