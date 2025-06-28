from ..models.wall import Wall
from ..models.common import Position
from ..models.brick import Brick
from ..configs.config import Config


def calculate_flemish_bond(wall: Wall, config: Config) -> list[Brick]:
    """
    Calculates the positions of the bricks for Flemish Bond.

    Pattern:
    - Course 0 (even): Full, Half, full .. Half, Full
    - Course 1 (odd): Half, Quarter, Full, Half, ..., Half, Quarter, Half
    - Repeat pattern
    """

    wall_height = config["wall"]["height"]
    wall_width = config["wall"]["width"]
    course_height = config["joints"]["bed_joint"] + config["bricks"]["full"]["height"]

    full_length = config["bricks"]["full"]["length"]
    half_length = config["bricks"]["half"]["length"]
    quarter_length = config["bricks"]["quarter"]["length"]
    head_joint = config["joints"]["head_joint"]

    brick_list: list[Brick] = []
    brick_id = 0
    num_courses = int(wall_height / course_height)

    for course in range(num_courses):
        y_pos = course * course_height

        if y_pos + config["bricks"]["full"]["height"] > wall.height:
            break

        x_pos = 0.0
        bricks_in_course: list[Brick] = []

        if course % 2 == 0:
            brick_type_cycle = ["full", "half"]
            position_in_pattern = 0

            while x_pos < wall_width:
                brick_type = brick_type_cycle[position_in_pattern % 2]

                if brick_type == "full" and x_pos + full_length <= wall_width:
                    brick = Brick(
                        id=brick_id, brick_type="full", position=Position(x_pos, y_pos)
                    )
                    bricks_in_course.append(brick)
                    brick_id += 1
                    x_pos += full_length + head_joint

                elif brick_type == "half" and x_pos + half_length <= wall_width:
                    brick = Brick(
                        id=brick_id, brick_type="half", position=Position(x_pos, y_pos)
                    )
                    bricks_in_course.append(brick)
                    brick_id += 1
                    x_pos += half_length + head_joint

                else:
                    # Try to fit remaining space with quarter brick
                    if x_pos + quarter_length <= wall_width:
                        brick = Brick(
                            id=brick_id,
                            brick_type="quarter",
                            position=Position(x_pos, y_pos),
                        )
                        bricks_in_course.append(brick)
                        brick_id += 1
                    break

                position_in_pattern += 1

        else:
            # Odd course: Start with half, quarter, then alternate full-half pattern
            # 1. Start with half brick
            if x_pos + half_length <= wall_width:
                brick = Brick(
                    id=brick_id, brick_type="half", position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += half_length + head_joint

            # 2. Then quarter brick
            if x_pos + quarter_length <= wall_width:
                brick = Brick(
                    id=brick_id, brick_type="quarter", position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += quarter_length + head_joint

            # 3. Then alternate full-half pattern
            brick_type_cycle = ["full", "half"]
            position_in_pattern = 0

            ending_pattern_space = quarter_length + head_joint + half_length

            while x_pos < (wall_width - ending_pattern_space):
                brick_type = brick_type_cycle[position_in_pattern % 2]

                if (
                    brick_type == "full"
                    and x_pos + full_length + head_joint
                    <= wall_width - ending_pattern_space
                ):
                    brick = Brick(
                        id=brick_id, brick_type="full", position=Position(x_pos, y_pos)
                    )
                    bricks_in_course.append(brick)
                    brick_id += 1
                    x_pos += full_length + head_joint

                elif (
                    brick_type == "half"
                    and x_pos + half_length + head_joint
                    <= wall_width - ending_pattern_space
                ):
                    brick = Brick(
                        id=brick_id, brick_type="half", position=Position(x_pos, y_pos)
                    )
                    bricks_in_course.append(brick)
                    brick_id += 1
                    x_pos += half_length + head_joint

                else:
                    break

                position_in_pattern += 1

            # 4. Add ending pattern: quarter, half
            # Add quarter brick
            if x_pos + quarter_length <= wall_width:
                brick = Brick(
                    id=brick_id, brick_type="quarter", position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += quarter_length + head_joint

                # Add half brick (final brick)
                if x_pos + half_length <= wall_width:
                    brick = Brick(
                        id=brick_id, brick_type="half", position=Position(x_pos, y_pos)
                    )
                    bricks_in_course.append(brick)
                    brick_id += 1

        brick_list.extend(bricks_in_course)

    return brick_list
