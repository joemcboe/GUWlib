import heapq


def partition_rectangle_with_rectilinear_cutouts(rectangle_width, rectangle_length, bounding_box_list):
    """
    Partitions a rectangle with cut-out rectangular regions into simple, pure rectangular regions:

    ┌────────────────────┐      ┌─────────┬──────────┐
    │         ┌──────┐   │      │         ┢━━━━━━┱───┤
    │         │      │   │      │         ┃      ┃   │
    │         │      │   │      │         ┃      ┃   │
    │         └──────┘   │      │         ┡━━┯━━━┹───┤
    │  ┌─────────┐       │      ├──┲━━━━━━┷━━┪       │
    │  │         │       │      │  ┃         ┃       │
    │  └─────────┘       │      │  ┡━━━━━━━━━┩       │
    └────────────────────┘      └──┴─────────┴───────┘

    This is useful to create partitions in ABAQUS that can be meshed with structured meshes. Note that the
    implementation is rather brute-force and might take a while to compute if >20 cut-outs need to be considered.

    :param float rectangle_width: Width (x) of the outer rectangle.
    :param float rectangle_length: Length (y) of the outer rectangle.
    :param bounding_box_list:
    :return:
    """
    cells, n_cells_x, n_cells_y = __generate_cell_array(rectangle_width, rectangle_length, bounding_box_list)
    area_total = rectangle_width * rectangle_length
    number_of_cells = len(cells)
    number_of_steps = 0

    while any(row[4] for row in cells[:number_of_cells]):  # still any active cells

        all_possible_steps = []
        for cell_id in range(number_of_cells):
            if cells[cell_id][4]:
                all_possible_steps.extend(__get_all_rectangles(cell_id, cells, n_cells_x, n_cells_y, area_total))

        all_possible_steps = sorted(all_possible_steps, key=lambda col: col[7], reverse=False)
        unique_possible_steps = [all_possible_steps[0]]
        for row in all_possible_steps[1:]:
            if row[7] != unique_possible_steps[-1][7]:
                unique_possible_steps.append(row)

        __carry_out_step(unique_possible_steps[0], cells, n_cells_x)
        number_of_steps += 1

    cells = [cell[0:4] for cell in cells[number_of_cells:]]

    return cells


def __generate_cell_array(plate_width, plate_length, bounding_boxes):
    """
    Returns a list of elementary rectangular cells that partition the plate with cut-out rectangles into simple
    rectangular regions, as a first step of the rectilinear partitioning algorithm. The elementary cells can later be
    joined to create a partitioning scheme with less and larger cells.

    ┌────────────────────┐      ┏━━┯━━━━━━┯━━┯━━━┯━━━┓
    │         ┌──────┐   │      ┠──┼──────┼──╆━━━╅───┨
    │         │      │   │      ┃  │      │  ┃   ┃   ┃
    │         │      │   │      ┃  │      │  ┃   ┃   ┃
    │         └──────┘   │      ┠──┼──────┼──╄━━━╃───┨
    │  ┌─────────┐       │      ┠──╆━━━━━━╅──┼───┼───┨
    │  │         │       │      ┃  ┃      ┃  │   │   ┃
    │  └─────────┘       │      ┠──╄━━━━━━╃──┼───┼───┨
    └────────────────────┘      ┗━━┷━━━━━━┷━━┷━━━┷━━━┛

    :param plate_width:
    :param plate_length:
    :param bounding_boxes:
    :return:

    holes is a list of form:
      [[left, bottom, right, top],
       [left, bottom, right, top],
        ...,]
          where (left, bottom) are the (x, y) coordinates of the lower left corner of the bounding box
          and (right, top) are the (x, y) coordinates of the upper right corner of the bounding box
    """

    # create a list of all vertices in x- and y-direction to create a grid
    vertices_x = [0, plate_width]
    vertices_y = [0, plate_length]

    for bounding_box in bounding_boxes:
        left, bottom, right, top = (bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
        vertices_x.extend([left, right])
        vertices_y.extend([bottom, top])

    # remove doubles
    vertices_x = sorted(list(set(vertices_x)))
    vertices_y = sorted(list(set(vertices_y)))

    # populate the grid with cells, and mark cells that lie within a bounding box as inactive
    cell_list = []
    n_cells_x = len(vertices_x) - 1
    n_cells_y = len(vertices_y) - 1

    for i in range(n_cells_y):
        for j in range(n_cells_x):
            left, right, top, bottom = (vertices_x[j], vertices_x[j + 1], vertices_y[i + 1], vertices_y[i])

            # check if the cell lies withing any bounding box
            is_active = True
            for bounding_box in bounding_boxes:
                if bounding_box[0] <= left < bounding_box[2]:
                    if bounding_box[1] <= bottom < bounding_box[3]:
                        is_active = False

            cell_list.append([left, bottom, right, top, is_active])

    return cell_list, n_cells_x, n_cells_y


# ----------------------------------------------------------------------------------------------------------------------

def __get_max_expand(cell_id, cell_list, n_cells_x, n_cells_y):
    """
    For a given cell with ID cell_id and a list of all cells cell_list, this function computes all possible combinations
    the given cell could be expanded in vertical and horizontal direction by merging with its neighbour cells.
    :param cell_id:
    :param cell_list:
    :param n_cells_x:
    :param n_cells_y:
    :return:
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
                    or cell_list[x_neighbour_id][4] is False):
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
                                or cell_list[y_neighbour_id][4] is False
                                or iy == last_max_iy[k]):
                            continue_expand_y = False
                            last_max_iy[k] = iy
                        else:
                            iy += 1
                    expand_data[1 + k] = -(iy - 1) * direction_y
                all_expand_data[j].append(expand_data)
                # ------------------------------------------------------------------------------------------------------
            ix += 1
    return all_expand_data


def __get_all_rectangles(cell_id, cell_list, n_cells_x, n_cells_y, area_total):
    expand_data = __get_max_expand(cell_id, cell_list, n_cells_x, n_cells_y)
    possible_steps_list = []
    for negative_x in expand_data[0]:
        for positive_x in expand_data[1]:
            this_x_min = negative_x[0]
            this_x_max = positive_x[0]
            y_min = max(negative_x[1], positive_x[1])
            y_max = min(negative_x[2], positive_x[2])
            for this_y_min in range(abs(y_min) + 1):
                for this_y_max in range(y_max + 1):
                    left = cell_list[cell_id + this_x_min][0]
                    right = cell_list[cell_id + this_x_max][2]
                    bottom = cell_list[cell_id - n_cells_x * this_y_min][1]
                    top = cell_list[cell_id + n_cells_x * this_y_max][3]
                    w = right - left
                    h = top - bottom
                    area = w * h
                    short_side, long_side = (w, h) if w < h else (h, w)
                    aspect_ratio = long_side / short_side
                    weight = 1 - (1 / (0.1 * (aspect_ratio - 1) + 1)) * area / area_total
                    possible_steps_list.append([cell_id, this_x_min, this_x_max, -this_y_min, this_y_max, area,
                                                aspect_ratio, weight])

    top_entries = heapq.nsmallest(min(5, len(possible_steps_list)), possible_steps_list, key=lambda x: x[7])
    return top_entries


def __carry_out_step(step_definition, cell_array, n_cells_x):
    """
    Executes a step definition, i.e. merging the given cell with its neighbouring cells by deactivating all primary
    cells and creating a new, merged one.

    :param step_definition:
    :param cell_array:
    :param n_cells_x:
    :return:
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
            cell_array[cell_id][4] = False

    # create a new cell with dimensions of the merged cell
    left = cell_array[this_cell_id + x_min][0]
    right = cell_array[this_cell_id + x_max][2]
    bottom = cell_array[this_cell_id + n_cells_x * y_min][1]
    top = cell_array[this_cell_id + n_cells_x * y_max][3]
    cell_array.append([left, bottom, right, top, True])
