# -*- coding: utf-8 -*-
"""
The functions in this module help to partition a rectangle with rectilinear cut-outs (as depicted in (a) for example)
into pure rectilinear partitions (figure (c)). This can be useful for meshing in ABAQUS. The implemented algorithm
starts by creating an array of cells by simply extending all edges of the cut-outs to the border of the rectangle, as
depicted in (b). These cells can then be iteratively merged into bigger cells.::

    ┌────────────────────┐      ┌──┬──────┬──┬───┬───┐       ┌─────────┬──────┬───┐
    │         ┌──────┐   │      ├──┼──────┼──┼───┼───┤       │         ├──────┼───┤
    │         │      │   │      │  │      │  │   │   │       │         │      │   │
    │         │      │   │      │  │      │  │   │   │       │         │      │   │
    │         └──────┘   │      ├──┼──────┼──┼───┼───┤       │         ├──┬───┴───┤
    │  ┌─────────┐       │      ├──┼──────┼──┼───┼───┤       ├──┬──────┴──┤       │
    │  │         │       │      │  │      │  │   │   │       │  │         │       │
    │  └─────────┘       │      ├──┼──────┼──┼───┼───┤       │  ├─────────┤       │
    └────────────────────┘      └──┴──────┴──┴───┴───┘       └──┴─────────┴───────┘
    (a)                         (b)                          (c)

"""
import heapq


def partition_rectangle_with_rectilinear_cutouts(rectangle_width, rectangle_length, cut_outs):
    """
    Partitions a rectangle with cut-out rectangular regions into simple, pure rectilinear regions (deterministic).

    This is useful to create partitions in ABAQUS that can be meshed with structured meshes. Note that the
    implementation is rather brute-force and might take a while to compute if >20 cut-outs need to be considered.

    :param float rectangle_width: Width (x) of the outer rectangle.
    :param float rectangle_length: Length (y) of the outer rectangle.
    :param list[list[float, float, float, float]] cut_outs: A list of the cut-outs, defined by their lower-left and
    upper-right diagonal corners ([left, bottom, right, top]).

    :return: A list of the created rectilinear partitions, defined by their lower-left and upper-right diagonal corners
    ([left, bottom, right, top]).
    :rtype: list[list[float, float, float, float]]
    """

    # generate the primitive partition into elementary cells
    cells, n_cells_x, n_cells_y = __generate_cell_array(rectangle_width, rectangle_length, cut_outs)
    area_total = rectangle_width * rectangle_length
    number_of_cells = len(cells)

    # merge elementary cells into partitions until no more elementary cells (active cells) exist
    while any(row[4] for row in cells[:number_of_cells]):

        # for each cell, obtain all possible combinations (steps) this cell could be merged with its neighbours
        all_possible_steps = []
        for cell_id in range(number_of_cells):
            if cells[cell_id][4]:
                all_possible_steps.extend(__get_best_merge_options_for_given_cell(cell_id, cells, n_cells_x, n_cells_y, area_total))

        # column 7 of all_possible_steps contains the optimization objective (prioritize merging cells into big
        # partitions with good aspect ratio)
        all_possible_steps = sorted(all_possible_steps, key=lambda col: col[7], reverse=False)

        # pick the best step, i.e. the one that will result in the biggest merged cell
        unique_possible_steps = [all_possible_steps[0]]
        for row in all_possible_steps[1:]:
            if row[7] != unique_possible_steps[-1][7]:
                unique_possible_steps.append(row)

        # merge cells by updating the cells list
        __carry_out_step(unique_possible_steps[0], cells, n_cells_x)

    # return the results, the merged cells (partitions) are at the end of the cells list
    cells = [cell[0:4] for cell in cells[number_of_cells:]]
    return cells


def __generate_cell_array(rectangle_width, rectangle_length, cut_outs):
    """
    Returns a list of elementary rectangular cells that partition the plate with cutout rectangles into a grid of simple
    rectangular regions, as a first step of the rectilinear partitioning algorithm. The elementary cells can later be
    joined to create a partitioning scheme with less and larger cells.

    :param float rectangle_width: Width (x) of the outer rectangle.
    :param float rectangle_length: Length (y) of the outer rectangle.
    :param list[list[float, float, float, float]] cut_outs: A list of the cutouts, defined by their lower-left and
    upper-right diagonal corners ([left, bottom, right, top]).

    :return: A list of the created cells, defined by their lower-left and upper-right diagonal corners and their status
    ([left, bottom, right, top, is_active]). Inactive cells are not part of the rectangle. Also returns the number of
    cells in horizontal and vertical direction.
    :rtype: tuple[list[list[float, float, float, float, bool]], int, int]
    """

    # create a list of all vertices in x- and y-direction to create a grid
    vertices_x = [0, rectangle_width]
    vertices_y = [0, rectangle_length]

    for cut_out in cut_outs:
        left, bottom, right, top = (cut_out[0], cut_out[1], cut_out[2], cut_out[3])
        vertices_x.extend([left, right])
        vertices_y.extend([bottom, top])

    # remove doubles
    vertices_x = sorted(list(set(vertices_x)))
    vertices_y = sorted(list(set(vertices_y)))

    # populate the grid with cells, and mark cells that lie within a cut-out region as inactive
    cell_list = []
    n_cells_x = len(vertices_x) - 1
    n_cells_y = len(vertices_y) - 1

    for i in range(n_cells_y):
        for j in range(n_cells_x):
            left, right, top, bottom = (vertices_x[j], vertices_x[j + 1], vertices_y[i + 1], vertices_y[i])

            # check if the cell lies withing any cut-out region
            is_active = True
            for cut_out in cut_outs:
                if cut_out[0] <= left < cut_out[2]:
                    if cut_out[1] <= bottom < cut_out[3]:
                        is_active = False

            cell_list.append([left, bottom, right, top, is_active])

    return cell_list, n_cells_x, n_cells_y


# ----------------------------------------------------------------------------------------------------------------------

def __get_possible_cell_expansions(cell_id, cells, n_cells_x, n_cells_y):
    """
    Analyzes how the given cell could be expanded to the left, right, top or bottom without intersecting the border,
    cut-out regions or already merged cells. Returns all possible combinations.

    :param int cell_id: List index of the cell to analyze.
    :param list[list[float, float, float, float, bool]] cells: List of all cells.
    :param int n_cells_x: Number of grid elementary cells in horizontal direction.
    :param int n_cells_y: Number of grid elementary cells in vertical direction.
    :return: All possible combinations of cell-expansions, where a cell-expansion is provided in the form
    [expand_n_cells_x, expand_n_cells_low, expand_n_cells_top].
    :rtype: list[list[int, int, int]]
    """

    this_row = cell_id // n_cells_x
    all_expand_data = [[], []]
    # x expand ---------------------------------------------------------------------------------------------------------
    for j, direction_x in enumerate([-1, 1]):
        continue_expand_x = True
        last_max_iy = [float("inf")] * 2
        ix = 0
        while continue_expand_x:
            expand_data = [None] * 3
            x_neighbour_id = cell_id + direction_x * ix
            if ((x_neighbour_id // n_cells_x != this_row)  # out of this row
                    or cells[x_neighbour_id][4] is False):
                continue_expand_x = False
            else:
                expand_data[0] = direction_x * ix
                # y expand ---------------------------------------------------------------------------------------------
                for k, direction_y in enumerate([1, -1]):
                    continue_expand_y = True
                    iy = 0
                    while continue_expand_y:
                        y_neighbour_id = x_neighbour_id - iy * direction_y * n_cells_x
                        if (y_neighbour_id < 0
                                or y_neighbour_id >= n_cells_y * n_cells_x
                                or cells[y_neighbour_id][4] is False
                                or iy == last_max_iy[k]):
                            continue_expand_y = False
                            last_max_iy[k] = iy
                        else:
                            iy += 1
                    expand_data[k+1] = -(iy - 1) * direction_y
                all_expand_data[j].append(expand_data)
                # ------------------------------------------------------------------------------------------------------
            ix += 1
    return all_expand_data


def __get_best_merge_options_for_given_cell(cell_id, cells, n_cells_x, n_cells_y, area_total):
    """
    For a given cell and the list of all cells, this function computes all possible combinations the given cell could
    be expanded in vertical and horizontal direction by merging with its neighbour cells. The combinations are rated
    based on the size and aspect ratio of the resulting merged cell, and the best 5 options are returned.

    :param int cell_id: List index of the cell to analyze.
    :param list[list[float, float, float, float, bool]] cells: List of all cells.
    :param int n_cells_x: Number of grid elementary cells in horizontal direction.
    :param int n_cells_y: Number of grid elementary cells in vertical direction.
    :param float area_total: Total outer rectangle area.
    :return: The 5 top options to merge the cell with its neighbours, defined by [cell_id, x_min, x_max,
    y_min, y_max, area, aspect_ratio, objective], where x and y min and max define the dimensions of the merged cell.
    :rtype: list[list[int, int, int, int, int, float, float, float]]
    """
    expand_data = __get_possible_cell_expansions(cell_id, cells, n_cells_x, n_cells_y)
    possible_steps_list = []
    for negative_x in expand_data[0]:
        for positive_x in expand_data[1]:
            this_x_min = negative_x[0]
            this_x_max = positive_x[0]
            y_min = max(negative_x[1], positive_x[1])
            y_max = min(negative_x[2], positive_x[2])
            for this_y_min in range(abs(y_min) + 1):
                for this_y_max in range(y_max + 1):
                    left = cells[cell_id + this_x_min][0]
                    bottom = cells[cell_id - n_cells_x * this_y_min][1]
                    right = cells[cell_id + this_x_max][2]
                    top = cells[cell_id + n_cells_x * this_y_max][3]
                    w = right - left
                    h = top - bottom
                    area = w * h
                    short_side, long_side = (w, h) if w < h else (h, w)
                    aspect_ratio = long_side / short_side
                    objective = 1 - (1 / (0.1 * (aspect_ratio - 1) + 1)) * area / area_total
                    possible_steps_list.append([cell_id, this_x_min, this_x_max, -this_y_min, this_y_max, area,
                                                aspect_ratio, objective])

    top_entries = heapq.nsmallest(min(5, len(possible_steps_list)), possible_steps_list, key=lambda x: x[7])
    return top_entries


def __carry_out_step(step_definition, cells, n_cells_x):
    """
    Executes a step definition, i.e. merging the given cell with its neighbouring cells by deactivating all primary
    cells in-place and creating a new, merged one with the given dimensions.

    :param list step_definition: Definition of the merging step to be carried out, defined by the cell id and the
    dimensions of the new, merged cell or partition.
    :param list[list[float, float, float, float, bool]] cells: List of all cells.
    :param int n_cells_x: Number of cells in horizontal direction.
    :return: None
    """
    this_cell_id = step_definition[0]

    x_min = step_definition[1]
    x_max = step_definition[2]
    y_min = step_definition[3]
    y_max = step_definition[4]

    # deactivate all primary cells within the new merged cell
    for y in range(y_max - y_min + 1):
        for x in range(x_max - x_min + 1):
            cell_id = this_cell_id + (y_min + y) * n_cells_x + (x_min + x)
            cells[cell_id][4] = False

    # create a new cell with dimensions of the merged cell
    left = cells[this_cell_id + x_min][0]
    right = cells[this_cell_id + x_max][2]
    bottom = cells[this_cell_id + n_cells_x * y_min][1]
    top = cells[this_cell_id + n_cells_x * y_max][3]
    cells.append([left, bottom, right, top, True])
