import re


def replace_keys(text, values):
    # Define a regular expression pattern to match ##key##
    pattern = r'##(\w+)##'

    # Define a function to use in re.sub() for replacement
    def replace(match):
        key = match.group(1)
        return str(values.get(key, match.group(0)))

    # Use re.sub() to replace occurrences of ##key## with corresponding values
    result = re.sub(pattern, replace, text)
    return result


# Read in template
file_path = 'dispersion_template.py'
with open(file_path, 'r') as file:
    file_content = file.read()

for elements_in_thickness in [2]:
    for nodes_per_wavelength in [6]:
        # Define your values dictionary
        my_values = {
            'element_type': "'continuum'",
            'elements_thickness': elements_in_thickness,
            'nodes_wavelength': nodes_per_wavelength,
        }

        # Replace keys in the text
        updated_content = replace_keys(file_content, my_values)

        # Write the updated content to a new file
        new_file_path = 'dispersion_no_boundary_long_t{:02d}_w{:02d}.py'.format(elements_in_thickness, nodes_per_wavelength)
        with open(new_file_path, 'w') as file:
            file.write(updated_content)
