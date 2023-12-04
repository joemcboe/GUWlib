import numpy as np
import matplotlib.pyplot as plt
import os
from guwlib.guw_objects.material import Material


def read_dispersion_data_from_txt_file(txt_file_path, thickness):
    """

    :param txt_file_path:
    :param thickness:
    :return:
    """
    raw_data = np.loadtxt(txt_file_path, delimiter=',', skiprows=1)
    num_columns = np.shape(raw_data)[1]
    dispersion_data = [{} for _ in range(num_columns // 8)]

    # header looks like this:
    # A0 f*d (MHz*mm),A0 Phase velocity (m/ms),A0 Energy velocity (m/ms),A0 Propagation time (micsec),
    # A0 Coincidence angle (deg),A0 Wavelength/d (),A0 Wavenumber*d (rad),A0 Attenuation*d (Np/m*mm)
    header = ["frequency", "phase_velocity", "energy_velocity", "propagation_time",
              "coincidence_angle", "wavelength", "wavenumber", "attenuation"]
    factors = [1e6 / (1e3 * thickness), 1 / 1e-3, 1 / 1e-3, 1e-6,
               np.pi / 180, thickness, 1 / thickness, 1]

    # extract data
    for prop_index, prop in enumerate(header):
        for mode, column in enumerate(np.arange(prop_index, num_columns, 8)):
            dispersion_data[mode][prop] = factors[prop_index] * raw_data[:, column]

    return dispersion_data


def get_lamb_dispersion_txt_files_path(material_name):
    """

    :param material_name:
    :return:
    """
    script_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(os.path.dirname(script_path))

    symmetric_path = os.path.join(parent_dir, 'data\\{}_S_Lamb.txt'.format(material_name))
    asymmetric_path = os.path.join(parent_dir, 'data\\{}_A_Lamb.txt'.format(material_name))

    if not os.path.exists(symmetric_path):
        raise FileNotFoundError("{} not found.".format(symmetric_path))

    if not os.path.exists(asymmetric_path):
        raise FileNotFoundError("{} not found.".format(asymmetric_path))

    return symmetric_path, asymmetric_path


def get_minimal_lamb_wavelength(material, thickness, frequency_range):
    """
    Calculate the minimal wavelength within a given frequency range for a given material and thickness.

    :param Material material: An object representing the material with a "material_name" attribute.
    :param float thickness: The thickness of the material.
    :param [float, float] frequency_range: A tuple representing the frequency range (min_freq, max_freq).
    :return: A tuple containing the minimal wavelength and the corresponding frequency within frequency_range.
    """
    symmetric_txt_path, asymmetric_txt_path = get_lamb_dispersion_txt_files_path(material.name)
    symmetric_modes_data = read_dispersion_data_from_txt_file(symmetric_txt_path, thickness)
    asymmetric_modes_data = read_dispersion_data_from_txt_file(asymmetric_txt_path, thickness)

    minimal_wavelength = float('inf')
    minimal_wavelength_frequency = None

    # loop over symmetric and asymmetric modes data
    for dispersion_data in [symmetric_modes_data, asymmetric_modes_data]:
        # loop over all modes (0, 1, 2, ...)
        for mode_order in range(len(dispersion_data)):
            frequencies = dispersion_data[mode_order]["frequency"]
            wavelengths = dispersion_data[mode_order]["wavelength"]

            frequencies_no_nan = frequencies[np.logical_and(~np.isnan(frequencies), ~np.isnan(wavelengths))]
            wavelengths_no_nan = wavelengths[np.logical_and(~np.isnan(frequencies), ~np.isnan(wavelengths))]

            wavelength_min, frequency_argmin = find_min_between_limits(x=frequencies_no_nan, y=wavelengths_no_nan,
                                                                       limits=frequency_range)
            if wavelength_min < minimal_wavelength:
                minimal_wavelength = wavelength_min
                minimal_wavelength_frequency = frequency_argmin

    return minimal_wavelength, minimal_wavelength_frequency


def find_min_between_limits(x, y, limits):
    """

    :param np.ndarray x:
    :param y:
    :param limits:
    :return:
    """
    below_limit = x < limits[0]
    inside_limits = np.logical_and(x >= limits[0], x <= limits[1])
    above_limit = x > limits[1]
    if np.any(inside_limits):
        y_in_limits = y[inside_limits]
        x_in_limits = x[inside_limits]
        if np.any(below_limit):
            boundary_x = limits[0]
            boundary_y = np.interp(boundary_x, x, y)
            y_in_limits = np.insert(y_in_limits, 0, boundary_y)
            x_in_limits = np.insert(x_in_limits, 0, boundary_x)
        if np.any(above_limit):
            boundary_x = limits[1]
            boundary_y = np.interp(boundary_x, x, y)
            y_in_limits = np.append(y_in_limits, boundary_y)
            x_in_limits = np.append(x_in_limits, boundary_x)
        return np.min(y_in_limits), x_in_limits[np.argmin(y_in_limits)]
    else:
        return float('inf'), None


# ----------------------------------------------------------------------------------------------------------------------

# x = np.array([4, 6, 8.0])
# y = np.array([10,  5.0, 0])
#
# limits = [2,7]
#
# y_min, x_argmin = find_min_between_limits(x, y, limits)
# print(y_min, x_argmin)


# thickness = 3e-3
# alu = Material(material_name='AluminumAlloy1100', material_type='isotropic')
# min_lambda, min_lambda_f = get_minimal_lamb_wavelength(alu, thickness, (20e3, 50e3))
# print(min_lambda)
# print(min_lambda_f)
#
# symmetric_txt_path, asymmetric_txt_path = get_lamb_dispersion_txt_files_path(alu.material_name)
# symmetric_modes = read_dispersion_data_from_txt_file(symmetric_txt_path, thickness)
# asymmetric_modes = read_dispersion_data_from_txt_file(asymmetric_txt_path, thickness)
# for mode in range(len(symmetric_modes)):
#     plt.plot(symmetric_modes[mode]['frequency'], symmetric_modes[0]['wavelength'])
#     plt.plot(asymmetric_modes[mode]['frequency'], asymmetric_modes[0]['wavelength'])
# plt.plot(min_lambda_f, min_lambda, 'rx')
# plt.ylim(0, 0.15)
# plt.xlim(0, 100e3)
# plt.show()
