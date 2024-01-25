import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D
import numpy as np

# conversion factors
INCHES_TO_MM = 25.4
MM_TO_INCHES = 1.0 / INCHES_TO_MM
MM_TO_POINTS = 72 / INCHES_TO_MM


def setup_technical_drawing_plot(sketch_width_mm, sketch_height_mm, approximate_size, line_width_mm,
                                 margins=(10, 10, 10, 10)):
    """

    :param sketch_width_mm: The width of the generated matplotlib figure in mm.
    :param sketch_height_mm: The height of the generated matplotlib figure in mm.
    :param approximate_size: The approximate size of the object to be sketched (usually the plate), in mm. Used to
    calculate an appropriate scaling factor.
    :param line_width_mm: The line width to be used for plotting.
    :param margins: The left, right, lower, upper margins.

    :return: (matplotlib.axes._axes.Axes) ax: axes for plotting.
    (dict) plot_settings: plotting settings, i.e. transforms and line width.

    """

    # setup affine transform to scale sketch object to paper size (based on the approximate size) and to center plot
    plot_size = np.min([sketch_height_mm-margins[2]-margins[3], sketch_width_mm-margins[0]-margins[1]])
    scaling_factor = plot_size / approximate_size
    sketch_transform = (Affine2D().translate(-approximate_size/2, -approximate_size/2).scale(scaling_factor).
                        translate(sketch_width_mm/2+margins[0]/2, sketch_height_mm/2+margins[2]/2))

    fig, ax = plt.subplots(figsize=(sketch_width_mm * MM_TO_INCHES, sketch_height_mm * MM_TO_INCHES))
    ax.set_position([0, 0, 1, 1])

    ax.axis('off')
    ax.set_xlim((0, sketch_width_mm))
    ax.set_ylim((0, sketch_height_mm))

    plot_settings = {
        'sketch_transform': sketch_transform,
        'line_width_mm': line_width_mm,
        'scaling_factor': scaling_factor
    }

    return ax, plot_settings


def add_linear_dimensioning(start_coordinate, end_coordinate, plot_settings, line_color='silver',
                            dimensioning_line_offset=5, prefix=''):
    """
    
    """
    # decompose plot_settings
    sketch_transform = plot_settings['sketch_transform']
    line_width_mm = plot_settings['line_width_mm']
    scaling_factor = plot_settings['scaling_factor']

    # settings for the dimensioning arrows
    arrow_kwargs = {
        'linewidth': 0,
        'head_width': 1.25 / scaling_factor,
        'head_length': 5.0 / scaling_factor,
        'fc': line_color,
        'length_includes_head': True
    }

    # calculate a transformation to a local coordinate system aligned with dimensioning line and with its origin
    # in the start_coordinate, using normalized base vectors e_x and e_y
    x1, y1 = start_coordinate
    x2, y2 = end_coordinate
    e_x = np.array([[x2 - x1], [y2 - y1]])
    e_x = e_x / np.linalg.norm(e_x)
    e_y = np.array([[-y2 + y1], [x2 - x1]])
    e_y = e_y / np.linalg.norm(e_y)
    e_0 = np.array([[x1], [y1]])
    local_transform = np.hstack((e_x, e_y))
    y_offset = dimensioning_line_offset/scaling_factor

    # compute length and angle of the dimensioning line
    length = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    angle_deg = np.arctan2(e_x[1], e_x[0]) * 180.0 / np.pi
    
    # plot the linear dimensioning line
    xy_data = e_0 + local_transform @ np.array([[-2/scaling_factor, length + 2/scaling_factor], [y_offset, y_offset]])
    plt.plot(xy_data[0, :], xy_data[1, :], linewidth=line_width_mm * MM_TO_POINTS, color=line_color,
             transform=sketch_transform + plt.gca().transData)

    # add arrow heads
    xy_data = e_0 + local_transform @ np.array([[0, length], [y_offset, y_offset]])
    plt.arrow(float(xy_data[0, 0]), float(xy_data[1, 0]), xy_data[0, 1] - xy_data[0, 0], 
              xy_data[1, 1] - xy_data[1, 0], transform=sketch_transform + plt.gca().transData, **arrow_kwargs)
    plt.arrow(float(xy_data[0, 1]), float(xy_data[1, 1]), xy_data[0, 0] - xy_data[0, 1], 
              xy_data[1, 0] - xy_data[1, 1], transform=sketch_transform + plt.gca().transData, **arrow_kwargs)

    # add text
    if y_offset < 0:
        kwargs = {"verticalalignment": 'top'}
    else:
        kwargs = {}

    text_transform = Affine2D(matrix=np.vstack([np.hstack([local_transform, np.array([[x1], [y1]])]), [0, 0, 1]]))
    plt.text(length / 2, y_offset + 2/scaling_factor*np.sign(y_offset), f'\\texttt{{{prefix}{length*1e3:g}}}',
             transform=text_transform + sketch_transform + plt.gca().transData,
             rotation=angle_deg[0], rotation_mode='anchor', horizontalalignment='center', color=line_color, **kwargs)

    # plot the helper lines
    xy_data = e_0 + local_transform @ np.array([[0, 0], [0, y_offset + 2/scaling_factor*np.sign(y_offset)]])
    plt.plot(xy_data[0, :], xy_data[1, :], linewidth=line_width_mm * MM_TO_POINTS, color=line_color,
             transform=sketch_transform + plt.gca().transData)
    xy_data = e_0 + local_transform @ np.array([[length, length], [0, y_offset + 2/scaling_factor*np.sign(y_offset)]])
    plt.plot(xy_data[0, :], xy_data[1, :], linewidth=line_width_mm * MM_TO_POINTS, color=line_color,
             transform=sketch_transform + plt.gca().transData)

