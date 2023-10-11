import csv
import numpy as np
from .output import *


def get_lamb_wavelength(material, thickness, frequency):
    """
    Returns the wavelength at the requested frequency for a given material/thickness. Reads in a .txt-file exported
    from DC (Dispersion Calculator) that contains the data.

    Params:
        material (string): material, such as 'aluminum'
        thickness (double): plate thickness in m
        frequency (double): request frequency in Hz

    Returns:
        wavelength (double-array): wavelength in m at requested frequency for modes [[S0, S1, S2, ...], [A0, A1, A2, ...]]
    """
    # assign the according data files from DC (dispersion calculator)
    if material == "aluminum":
        csv_file_paths = ['./abaqus_guw/dispersion_curves/AluminiumAlloy1100_S_Lamb.txt',
                          './abaqus_guw/dispersion_curves/AluminiumAlloy1100_A_Lamb.txt']
    else:
        raise ValueError('Material ''{}'' not known or no dispersion relation linked.'.format(material))

    # Read in and format the data from DC text data
    wavelength = []
    for csv_file_path in csv_file_paths:
        raw_data = []
        wavelength_data = []
        with open(csv_file_path) as csvfile:

            csvreader = csv.reader(csvfile, delimiter=',')
            first_row = next(csvreader, None)
            freq_indices = np.arange(0, len(first_row), 8)
            lambda_indices = np.arange(5, len(first_row), 8)
            for row in csvreader:
                raw_data.append(row)

        # Convert to numpy arrays and extract only needed data
        num_data = np.array(raw_data, dtype=float)
        wavelength_data = [np.array([num_data[:, f_ind], num_data[:, l_ind]]).transpose() for f_ind, l_ind in
                           zip(freq_indices, lambda_indices)]

        # Get the interpolated wavelength at the requested frequency
        fd = frequency * 1e-6 * thickness * 1e3  # [MHz * mm] = [Hz * m]
        wavelength_interpolated = []
        for table in wavelength_data:
            table = table[~np.any(np.isnan(table), axis=1)]
            lambda_query = linear_interpolation(table[:, 0], table[:, 1], fd)
            wavelength_interpolated.append(lambda_query * thickness)
        wavelength.append(wavelength_interpolated)

    info_str = "At f = {:.2f} kHz for t = {:.2f} mm:\n".format(frequency * 1e-3, thickness * 1e3)
    i_mode = 0
    modes = ["S", "A"]
    for lst in wavelength:
        j_mode = 0
        for lam in lst:
            if not np.isnan(lam):
                info_str = info_str + ("Lambda = {:.2f} mm ({}{:d})\n".format(lam * 1e3, modes[i_mode], j_mode))
            j_mode = j_mode + 1
        i_mode = i_mode + 1
    log_info(info_str)

    return wavelength


def linear_interpolation(x, y, xq):
    """
    Perform 1D linear interpolation given x, y, and xq values.

    Parameters:
    x (numpy.ndarray): 1D array of x-values.
    y (numpy.ndarray): 1D array of y-values corresponding to x.
    xq (float): The x-value for which interpolation is needed.

    Returns:
    float: Interpolated value at xq or NaN if xq is out of bounds.
    """
    if xq < x.min() or xq > x.max():
        return float('NaN')

    idx = np.searchsorted(x, xq)
    if idx == 0:
        return y[0]
    if idx == len(x):
        return y[-1]

    x0, x1 = x[idx - 1], x[idx]
    y0, y1 = y[idx - 1], y[idx]

    # Linear interpolation formula
    return y0 + (xq - x0) * (y1 - y0) / (x1 - x0)
