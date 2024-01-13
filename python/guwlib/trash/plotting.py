import matplotlib.pyplot as plt
from matplotlib.transforms import Affine2D
import matplotlib.patches as patches
import numpy as np

# conversion factors
inches_to_mm = 25.4
mm_to_inches = 1.0 / inches_to_mm
mm_to_points = 72 / inches_to_mm


def add_linear_dimensioning(start_coordinate, end_coordinate, custom_transform, scaling,
                            color='silver', line_width_mm=0.2, offset=5):

    # calculate the transform
    x1, y1 = start_coordinate
    x2, y2 = end_coordinate
    e_x = np.array([[x2 - x1], [y2 - y1]])
    e_x = e_x / np.linalg.norm(e_x)
    e_y = np.array([[-y2 + y1], [x2 - x1]])
    e_y = e_y / np.linalg.norm(e_y)

    length = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    angle_deg = np.arctan2(e_x[1], e_x[0]) * 180.0 / np.pi

    transform = np.hstack((e_x, e_y))
    e_0 = np.array([[x1], [y1]])

    offset=offset/scaling

    # plot the linear dimensioning line
    plot_data = e_0 + transform @ np.array([[0 - 2/scaling, length + 2/scaling], [offset, offset]])
    plt.plot(plot_data[0, :], plot_data[1, :], linewidth=line_width_mm * mm_to_points, color=color,
             transform=custom_transform)

    # add arrow heads
    arrow_kwargs = {
        'linewidth': 0,
        'head_width': (5.0 / 4.0) / scaling,
        'head_length': 5.0 / scaling,
        'fc': color,
        'length_includes_head': True
    }
    plot_data = e_0 + transform @ np.array([[0, length], [offset, offset]])
    plt.arrow(float(plot_data[0, 0]), float(plot_data[1, 0]),
              plot_data[0, 1] - plot_data[0, 0], plot_data[1, 1] - plot_data[1, 0], transform=custom_transform, **arrow_kwargs)
    plt.arrow(float(plot_data[0, 1]), float(plot_data[1, 1]),
              plot_data[0, 0] - plot_data[0, 1], plot_data[1, 0] - plot_data[1, 1], transform=custom_transform, **arrow_kwargs)

    # add text
    affine_transform = np.vstack([np.hstack([transform, np.array([[x1], [y1]])]), [0, 0, 1]])
    plt.text(length / 2, offset + 2/scaling, f'\\texttt{{{length:.2f}}}',
             transform=Affine2D(matrix=affine_transform) + custom_transform,
             rotation=angle_deg[0], rotation_mode='anchor', horizontalalignment='center', color=color)

    # plot the helper lines
    plot_data = e_0 + transform @ np.array([[0, 0], [0, offset + 2/scaling]])
    plt.plot(plot_data[0, :], plot_data[1, :], linewidth=line_width_mm * mm_to_points, transform=custom_transform,
             color=color)
    plot_data = e_0 + transform @ np.array([[length, length], [0, offset + 2/scaling]])
    plt.plot(plot_data[0, :], plot_data[1, :], linewidth=line_width_mm * mm_to_points, transform=custom_transform,
             color=color)


# general drawing settings ---------------------------------------------------------------------------------------------
plot_width_mm = 160
plot_height_mm = 120
line_thickness_mm = 0.2

# dimensions of the technical drawing
approximate_size = 1

# set a transform / scale for the technical drawing
margin = 10
plot_size = np.min([plot_height_mm, plot_width_mm]) - margin*2
scale = plot_size / approximate_size
translate = np.array([[plot_width_mm/2], [plot_height_mm/2]])
custom_transform = (Affine2D().scale(scale)).translate(translate[0], translate[1])


fig, ax = plt.subplots(figsize=(plot_width_mm * mm_to_inches, plot_height_mm * mm_to_inches))
ax.set_position([0, 0, 1, 1])



ax.axis('off')
ax.set_xlim((0, plot_width_mm))
ax.set_ylim((0, plot_height_mm))

width = 1
height = 0.8

rectangle = patches.Rectangle((-width/2, -height/2), width, height, linewidth=line_thickness_mm * mm_to_points,
                              edgecolor='black', facecolor='whitesmoke',
                              transform=custom_transform + plt.gca().transData)

ax.add_patch(rectangle)
# ax.plot([-width/2, width/2], [height*0.6, height*0.6], linewidth=line_thickness_mm * MM_TO_POINTS,
#         transform=custom_transform + plt.gca().transData)

add_linear_dimensioning([-width/2, height/2], [width/2, -height/2],
                        scaling=scale,
                        custom_transform=custom_transform + plt.gca().transData,
                        line_width_mm=line_thickness_mm,
                        color='silver',
                        offset=2)

add_linear_dimensioning([-width/2, height/2], [width/2, height/2],
                        scaling=scale,
                        custom_transform=custom_transform + plt.gca().transData,
                        line_width_mm=line_thickness_mm,
                        color='silver')



#
# add_linear_dimensioning([40, 100], [120, 100], line_width_mm=line_thickness_mm/2,
#                         color='silver')
# add_linear_dimensioning([120, 100], [120, 20], line_width_mm=line_thickness_mm/2,
#                         color='silver')

# ax.plot([-400, -400, 400, 400, -400], [-400, 400, 400, -400, -400], transform=custom_transform + plt.gca().transData)


# Speichere den Plot als PGF-Datei
# plt.savefig('plot.pgf', bbox_inches=None, pad_inches=0)

plt.show()
