import json


def parse_line(line):
    # Split the line into components
    components = line.split()

    # Extract relevant information
    material_name = components[0]
    density = float(components[1])
    youngs_modulus = float(components[2])
    poissons_ratio = float(components[3])

    if (float(components[4]) != 0.0) and (float(components[5]) != 0.0):
        return None, None

    # Create a dictionary for the material
    material_data = {
        "density": density,
        "youngs_modulus": youngs_modulus,
        "poissons_ratio": poissons_ratio
    }

    return material_name, material_data


def txt_to_json(input_file, output_file):
    materials_data = {}

    # Read the input TXT file
    with open(input_file, 'r') as file:
        for line in file:
            material_name, material_data = parse_line(line)
            materials_data[material_name] = material_data

    # Write the data to the output JSON file
    if material_name is not None:
        with open(output_file, 'w') as json_file:
            json.dump(materials_data, json_file, indent=2)


# Example usage
input_file = 'input.txt'
output_file = 'output.json'
txt_to_json(input_file, output_file)
