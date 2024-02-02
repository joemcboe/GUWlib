import numpy as np
import os
from guwlib.guw_objects.material import Material


def read_dispersion_data_from_txt_file(txt_file_path, thickness):
    """
    Helper to read in dispersion data from a text file, formatted as by the DLR Dispersion Calculator. Material
    thickness is taken into account when returning the data.

    :param str txt_file_path: Path to the .TXT file with formatted dispersion data.
    :param float thickness: Material thickness in m.
    :return: Dispersion data. Access the data like this: dispersion_data[mode_order][property].
    :rtype: dict
    """
    raw_data = np.loadtxt(txt_file_path, delimiter=',', skiprows=1)
    num_columns = np.shape(raw_data)[1]
    dispersion_data = [{} for _ in range(num_columns // 8)]

    # header of the .TXT file should look like this:
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
    Finds the dispersion data text files by material name for symmetric / antisymmetric modes relative to this script.

    :param str material_name: Material name to find the dispersion data text files for.
    :return: Paths to symmetric / antisymmetric modes dispersion data text files.
    :rtype: tuple[str, str]
    :raise: IOError, if the files cannot be located.
    """
    script_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(os.path.dirname(script_path))

    symmetric_path = os.path.join(parent_dir, 'data', '{}_S_Lamb.txt'.format(material_name))
    asymmetric_path = os.path.join(parent_dir, 'data', '{}_A_Lamb.txt'.format(material_name))

    if not os.path.exists(symmetric_path):
        raise IOError("{} not found.".format(symmetric_path))

    if not os.path.exists(asymmetric_path):
        raise IOError("{} not found.".format(asymmetric_path))

    return symmetric_path, asymmetric_path


def get_minimal_lamb_wavelength_in_frequency_range(material, thickness, frequency_range):
    """
    Calculate the minimal wavelength within a given frequency range for a given material and thickness. Checks all
    modes that may occur in the provided frequency band (A0, S0, A1, S1, ...).

    :param Material material: Material for which to get the minimal wavelength.
    :param float thickness: The thickness of the material in m.
    :param [float, float] frequency_range: A tuple representing the frequency range (min_freq, max_freq).
    :return: The minimal wavelength and the corresponding frequency within frequency_range.
    :rtype: tuple[float, float]
    """

    # read in the dispersion data
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
    Finds the minimum value of y(x) and its argument for limits(0) <= x <= limits(1).
    If limits[0] or limits[1] are not elements of x, this function tries to find interpolated y-values directly
    at the boundaries of the interval (only if values outside the interval are available).

    :param np.ndarray x: x-values
    :param np.ndarray y: y-values
    :param (float, float) limits: limits, i.e. (x_lower, x_upper)
    :return: (y_min, x_min) for y(x_min) = y_min
    :rtype: float
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

