LINE_LENGTH = 80


def log_info(text):
    log_helper("Info", text)


def log_warning(text):
    log_helper("Warn", text)


def log_error(text):
    log_helper("Err ", text)


def log_helper(type_of_log, text):
    lines = split_string_with_whitespace(text, LINE_LENGTH - 10)
    print("\n\n")
    for i in range(len(lines)):
        if i == 0:
            left_str = "  [" + type_of_log + "]  "
        else:
            left_str = " " * 10
        print(left_str + lines[i])
    print("\n\n")


def split_string_with_whitespace(text, line_length):
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
