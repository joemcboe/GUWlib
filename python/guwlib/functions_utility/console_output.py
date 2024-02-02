from __future__ import print_function
import sys

LINE_LENGTH = 100


def log_info(text):
    """
    Print nicely formatted info-text to sys.__stdout__ and ABAQUS redirected output stream.
    :param str text: Text to print.
    """
    log_helper("Info", text)


def log_warning(text):
    """
    Print nicely formatted warning-text to sys.__stdout__ and ABAQUS redirected output stream.
    :param str text: Text to print.
    """
    log_helper("Warn", text)


def log_error(text):
    """
    Print nicely formatted error-text to sys.__stdout__ and ABAQUS redirected output stream.
    :param str text: Text to print.
    """
    log_helper("Err ", text)


def log_helper(type_of_log, text):
    """
    Print nicely formatted text with max line length of 100 chars to both sys.__stdout__ and ABAQUS redirected output
    stream.
    :param str type_of_log: Type of information to print, e.g. "warn" or "info"-
    :param str text: Text to format and print.
    """
    lines = split_string_with_whitespace(text, LINE_LENGTH - 10)
    # abaqus redirected output stream
    print("\n\n")
    for i in range(len(lines)):
        if i == 0:
            left_str = "  [" + type_of_log + "]  "
        else:
            left_str = " " * 10
        print(left_str + lines[i])
    print("\n\n")

    # standard console output stream
    for i in range(len(lines)):
        if i == 0:
            left_str = "  [" + type_of_log + "]  "
        else:
            left_str = " " * 10
        print(left_str + lines[i], file=sys.__stdout__)
    print("\n")


def split_string_with_whitespace(text, line_length):
    """
    Split a given text into lines with a specified maximum line length.

   :param str text: The input text to be split into lines.
   :param int line_length: The maximum length (in characters) of each line.

   :return: A list of strings representing lines after splitting the input text.
   :rtype: list
    """
    lines = []
    current_line = ""
    remaining_line_length = line_length

    for char in text:
        if char == '\n':
            lines.append(current_line)
            current_line = ""
            remaining_line_length = line_length
        elif char == '\t':
            tab_spaces = 4  # You can adjust this to your preferred tab size
            if remaining_line_length >= tab_spaces:
                current_line += ' ' * tab_spaces
                remaining_line_length -= tab_spaces
            else:
                lines.append(current_line)
                current_line = ' ' * tab_spaces
                remaining_line_length = line_length - tab_spaces
        else:
            current_line += char
            remaining_line_length -= 1

            if remaining_line_length == 0:
                lines.append(current_line)
                current_line = ""
                remaining_line_length = line_length

    if current_line:
        lines.append(current_line)

    return lines
