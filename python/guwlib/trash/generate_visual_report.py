import sys

import numpy as np

import guwlib
from guwlib.functions_utility.technical_drawing import *
from guwlib.guw_objects.defects import *

directory_path = '../../models/alu3a/'
sys.path.append(directory_path)

# import the model file
from alu3a_central_2_hole10_top import MyModel, PHASED_ARRAY_RADIUS
# from alu3a_central_hole15_top import MyModel, PHASED_ARRAY_RADIUS
# from alu3a_central_hole10_top import MyModel, PHASED_ARRAY_RADIUS
# from alu3a_farfield_hole10_top import MyModel, PHASED_ARRAY_RADIUS
# from alu3a_crack_45_central_top import MyModel, PHASED_ARRAY_RADIUS
# from alu3a_pristine_top import MyModel, PHASED_ARRAY_RADIUS

model = MyModel()
model.setup_parameters()

filename = model.__module__

# sketch the model
# plate ----------------------------------------------------------------------------------------------------------------
ax, plot_settings = setup_technical_drawing_plot(sketch_width_mm=160,
                                                 sketch_height_mm=140,
                                                 approximate_size=model.plate.width,
                                                 line_width_mm=0.2)

rectangle = patches.Rectangle((0, 0), model.plate.width, model.plate.length,
                              linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                              edgecolor='black', facecolor='whitesmoke',
                              transform=plot_settings['sketch_transform'] + plt.gca().transData)
ax.add_patch(rectangle)

add_linear_dimensioning(start_coordinate=[0, model.plate.length],
                        end_coordinate=[model.plate.width, model.plate.length],
                        plot_settings=plot_settings)
add_linear_dimensioning(start_coordinate=[model.plate.width, model.plate.length],
                        end_coordinate=[model.plate.width, 0],
                        plot_settings=plot_settings)

# transducers ----------------------------------------------------------------------------------------------------------
add_linear_dimensioning(start_coordinate=[model.plate.width / 2, model.plate.length / 2 - PHASED_ARRAY_RADIUS],
                        end_coordinate=[model.plate.width / 2, model.plate.length / 2 + PHASED_ARRAY_RADIUS],
                        dimensioning_line_offset=25,
                        plot_settings=plot_settings,
                        prefix='⌀')

circle = patches.Circle((model.plate.width / 2, model.plate.length / 2),
                        radius=PHASED_ARRAY_RADIUS,
                        linestyle=(0, (3, 5, 1, 5)),
                        edgecolor='silver', facecolor='None',
                        linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                        transform=plot_settings['sketch_transform'] + plt.gca().transData)
ax.add_patch(circle)

for i, transducer in enumerate(model.transducers):
    circle = patches.Circle((transducer.position_x, transducer.position_y),
                            linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                            radius=transducer.radius, edgecolor='black', facecolor='grey',
                            transform=plot_settings['sketch_transform'] + plt.gca().transData,
                            zorder=10)
    ax.add_patch(circle)
    e_r = np.array([[transducer.position_x-model.plate.width/2], [transducer.position_y-model.plate.length/2]])
    e_0 = np.array([[model.plate.width/2], [model.plate.length/2]])
    e_t = e_0 + 1.65*e_r
    plt.text(e_t[0], e_t[1], f'P{i+1}',
             horizontalalignment='center', verticalalignment='center',
             color='silver',
             transform=plot_settings['sketch_transform'] + plt.gca().transData)

# defects --------------------------------------------------------------------------------------------------------------
for defect in model.defects:
    if isinstance(defect, Hole):
        circle = patches.Circle((defect.position_x, defect.position_y),
                                linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                                radius=defect.radius, edgecolor='black', facecolor='white',
                                transform=plot_settings['sketch_transform'] + plt.gca().transData,
                                zorder=10)
        ax.add_patch(circle)
        xy_data = ([[defect.position_x, defect.position_x - defect.radius * 3],
                    [defect.position_y, defect.position_y]],
                   [[defect.position_x, defect.position_x],
                    [defect.position_y, defect.position_y - defect.radius * 3]],
                   [[defect.position_x, defect.position_x + defect.radius * 3],
                    [defect.position_y, defect.position_y]],
                   [[defect.position_x, defect.position_x],
                    [defect.position_y, defect.position_y + defect.radius * 3]])
        for plot_data in xy_data:
            ax.plot(plot_data[0], plot_data[1],
                    transform=plot_settings['sketch_transform'] + plt.gca().transData,
                    linestyle=(0, (3, 5, 1, 5)),
                    color='k',
                    linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                    zorder=11)

        if defect.position_x < 0.8*model.plate.width:
            horizontal_alignment = 'left'
            sign = 1
        else:
            horizontal_alignment = 'right'
            sign = -1

        plt.text(defect.position_x + sign*defect.radius*5, defect.position_y,
                 #f'\\texttt{{⌀{defect.radius * 2e3:g}}}\n\\texttt{{({defect.position_x * 1e3:.1f}, {defect.position_y * 1e3:.1f})}}',
                 f'⌀{defect.radius * 2e3:g}\n({defect.position_x * 1e3:.1f}, {defect.position_y * 1e3:.1f})',
                 family="monospace",
                 transform=plot_settings['sketch_transform'] + plt.gca().transData,
                 horizontalalignment=horizontal_alignment, verticalalignment='center', color='silver')

    if isinstance(defect, Crack):
        # set up a transformation matrix
        c = np.cos(defect.angle)
        s = np.sin(defect.angle)
        rot_mat = np.array([[c, s], [-s, c]])
        e_0 = np.array([[defect.position_x], [defect.position_y]])
        xy_data = e_0 + rot_mat @ np.array([[-defect.length/2, defect.length/2], [0, 0]])
        plt.plot(xy_data[0, :], xy_data[1, :],
                 transform=plot_settings['sketch_transform'] + plt.gca().transData,
                 color='k',
                 linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                 )
        for x in np.linspace(-defect.length/2, defect.length/2, 3):
            xy_data = e_0 + rot_mat @ np.array([[x, x], [-2e-3, 2e-3]])
            plt.plot(xy_data[0, :], xy_data[1, :],
                     transform=plot_settings['sketch_transform'] + plt.gca().transData,
                     color='k',
                     linewidth=plot_settings['line_width_mm'] * MM_TO_POINTS,
                     )

        if defect.position_x < 0.8*model.plate.width:
            horizontal_alignment = 'left'
            sign = 1
        else:
            horizontal_alignment = 'right'
            sign = -1

        plt.text(defect.position_x + sign*defect.length*2, defect.position_y,
                 f'l={defect.length * 1e3:g}, $\\alpha$={defect.angle*180/np.pi:g} \n({defect.position_x * 1e3:.1f}, {defect.position_y * 1e3:.1f})',
                 family="monospace",
                 transform=plot_settings['sketch_transform'] + plt.gca().transData,
                 horizontalalignment=horizontal_alignment, verticalalignment='center', color='silver')


plt.savefig(f'{filename}.pgf', bbox_inches=None, pad_inches=0)
# plt.show()

section_title = str.replace(filename, '_', '\\_')
tex_string = f"""
\\section*{{{section_title}.py}}
\\begin{{figure}}[h]
  \\centering
  \\input{{{filename}.pgf}}
\\end{{figure}}

\\noindent
\\begin{{tabular}}{{ll}}
Plattengröße: & {model.plate.length*1e3} $\\times$ {model.plate.width*1e3} $\\times$ {model.plate.thickness*1e3} mm \\\\
Material: & {model.plate.material.name} \\\\
Max. Frequenz: & {model.max_frequency*1e-3} kHz \\\\
Elemente / Wellenlänge: & {model.elements_per_wavelength} 
$\\rightarrow$ Elementgröße Ebenenrichtung: {model.get_element_size_in_plane()*1e3:.3f} mm \\\\
Elemente / Dickenrichtung: & {model.elements_in_thickness_direction} 
$\\rightarrow$ Elementgröße Dickenrichtung: {model.get_element_size_thickness()*1e3:.3f} mm
\\end{{tabular}}


"""

print(tex_string)
