import os
import exifread
from datetime import datetime

def extract_metadata(file_path):
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f)
        date_taken = tags.get('EXIF DateTimeOriginal')
        if date_taken:
            date_taken = datetime.strptime(str(date_taken), '%Y:%m:%d %H:%M:%S')
            return date_taken
        else:
            return None

def generate_latex_commands(directory):
    latex_commands = []

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            file_path = os.path.join(directory, filename)
            date_taken = extract_metadata(file_path)

            if date_taken:
                # Format date and time with German month names
                formatted_date = date_taken.strftime('%d.%m.%y %H:%M')

                # Create LaTeX commands
                latex_commands.append(
                    fr'\begin{{column}}{{0.5\textwidth}}' + '\n'
                    fr'    \begin{{figure}}[htp]' + '\n'
                    fr'        \begin{{tikzpicture}}' + '\n'
                    fr'            \node[rotate=90] at (0,0) {{{formatted_date}}};' + '\n'
                    fr'        \end{{tikzpicture}}' + '\n'
                    fr'        \includegraphics[trim=0pt 100px 0pt 70px, clip, width=0.75\textwidth, ]{{{filename}}}' + '\n'
                    fr'    \end{{figure}}' + '\n'
                    fr'\end{{column}}' + '\n\n'
                )

    return latex_commands

def main():
    # Replace 'your_directory_path' with the actual path to your directory containing screenshots
    directory_path = 'C:\\Users\\joern\\Downloads\\OneDrive-2024-01-08'

    latex_commands = generate_latex_commands(directory_path)

    # Write LaTeX commands to a file
    with open('output.tex', 'w') as f:
        f.writelines(latex_commands)

if __name__ == "__main__":
    main()
