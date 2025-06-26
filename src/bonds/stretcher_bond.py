from ..models.wall import Wall
from ..models.common import Position
from ..models.brick import Brick
from ..configs.config import Config


def calculate_stretcher_bond(
    wall: Wall, config: Config
) -> list[Brick]:
    """
    Calculates the positions of the bricks for the stretcher bond.
    """

    wall_height = config['wall']['height']
    course_height = config['joints']['bed_joint'] + config['bricks']['full']['height']
    full_brick_length = config['bricks']['full']['length']
    half_brick_length = config['bricks']['half']['length']
    full_brick_height = config['bricks']['full']['height']
    head_joint = config['joints']['head_joint']

    brick_list: list[Brick] = []
    brick_id = 0

    num_courses = int(wall_height / course_height)

    for c in range(num_courses):

        # calc the y for course to include bed joints
        y_pos = c * course_height

        if y_pos + full_brick_height > wall.height:
            break

        # odd numbers
        starts_with_half = c % 2 == 1

        x_pos = 0.0
        bricks_in_course: list[Brick] = []

        if starts_with_half:
            if x_pos + half_brick_length <= wall.width:
                brick = Brick(
                    id=brick_id, 
                    brick_type="half", 
                    position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += half_brick_length + head_joint

        while x_pos < wall.width:
            remaining_space = wall.width - x_pos

            if remaining_space >= full_brick_length:
                brick = Brick(
                    id=brick_id, 
                    brick_type="full", 
                    position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += full_brick_length + head_joint

            # If full brick doesn't fit, try half brick
            elif remaining_space >= half_brick_length:
                brick = Brick(
                    id=brick_id, 
                    brick_type="half", 
                    position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += half_brick_length + head_joint

            else:
                # No more bricks fit in this course
                break

        brick_list.extend(bricks_in_course)

    return brick_list
