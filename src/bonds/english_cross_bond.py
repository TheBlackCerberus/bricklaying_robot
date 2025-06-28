from ..models.wall import Wall
from ..models.common import Position
from ..models.brick import Brick
from ..configs.config import Config


def calculate_english_cross_bond(wall: Wall, config: Config) -> list[Brick]:
    """
    Calculates the positions of the bricks for English Cross Bond.

    Pattern:
    - Course 0 (even): All full bricks
    - Course 1 (odd): Half, Quarter, Half, Half, ..., Half, Quarter, Half
    - Repeat pattern
    """
    wall_height = config["wall"]["height"]
    course_height = config["joints"]["bed_joint"] + config["bricks"]["full"]["height"]
    full_brick_length = config["bricks"]["full"]["length"]
    half_brick_length = config["bricks"]["half"]["length"]
    quarter_brick_length = config["bricks"]["quarter"]["length"]
    head_joint = config["joints"]["head_joint"]

    brick_list: list[Brick] = []
    brick_id = 0
    num_courses = int(wall_height / course_height)

    for course in range(num_courses):
        y_pos = course * course_height

        if y_pos + config["bricks"]["full"]["height"] > wall.height:
            break

        if course % 2 == 0:
            # EVEN COURSE: All full bricks
            x_pos = 0.0

            while x_pos < wall.width:
                remaining = wall.width - x_pos

                if remaining >= full_brick_length:
                    brick = Brick(
                        id=brick_id, brick_type="full", position=Position(x_pos, y_pos)
                    )
                    brick_list.append(brick)
                    brick_id += 1
                    x_pos += full_brick_length + head_joint
                else:
                    # Fill remaining space with smaller brick if possible
                    if remaining >= half_brick_length:
                        brick = Brick(
                            id=brick_id,
                            brick_type="half",
                            position=Position(x_pos, y_pos),
                        )
                        brick_list.append(brick)
                        brick_id += 1
                    elif remaining >= quarter_brick_length:
                        brick = Brick(
                            id=brick_id,
                            brick_type="quarter",
                            position=Position(x_pos, y_pos),
                        )
                        brick_list.append(brick)
                        brick_id += 1
                    break

        else:
            # ODD COURSE: Half, Quarter, Half, Half, ..., Half, Quarter, Half
            x_pos = 0.0

            # 1. Start with half brick
            if x_pos + half_brick_length <= wall.width:
                brick = Brick(
                    id=brick_id, brick_type="half", position=Position(x_pos, y_pos)
                )
                brick_list.append(brick)
                brick_id += 1
                x_pos += half_brick_length + head_joint

            # 2. Then quarter brick
            if x_pos + quarter_brick_length <= wall.width:
                brick = Brick(
                    id=brick_id, brick_type="quarter", position=Position(x_pos, y_pos)
                )
                brick_list.append(brick)
                brick_id += 1
                x_pos += quarter_brick_length + head_joint

            # 3. Then all half bricks until near the end
            while x_pos < wall.width:
                remaining = wall.width - x_pos

                # Check if we can fit ending pattern: quarter + half
                if remaining >= quarter_brick_length + head_joint + half_brick_length:
                    # Check if this would be the last section
                    remaining_after_half = remaining - (half_brick_length + head_joint)
                    if (
                        remaining_after_half
                        < quarter_brick_length + head_joint + half_brick_length
                    ):
                        brick = Brick(
                            id=brick_id,
                            brick_type="quarter",
                            position=Position(x_pos, y_pos),
                        )
                        brick_list.append(brick)
                        brick_id += 1
                        x_pos += quarter_brick_length + head_joint

                        # Add final half brick
                        brick = Brick(
                            id=brick_id,
                            brick_type="half",
                            position=Position(x_pos, y_pos),
                        )
                        brick_list.append(brick)
                        brick_id += 1
                        break
                    else:
                        # Place regular half brick
                        brick = Brick(
                            id=brick_id,
                            brick_type="half",
                            position=Position(x_pos, y_pos),
                        )
                        brick_list.append(brick)
                        brick_id += 1
                        x_pos += half_brick_length + head_joint

                elif remaining >= half_brick_length:
                    # Only half brick fits - this is the last brick
                    brick = Brick(
                        id=brick_id, brick_type="half", position=Position(x_pos, y_pos)
                    )
                    brick_list.append(brick)
                    brick_id += 1
                    break

                elif remaining >= quarter_brick_length:
                    # Only quarter brick fits
                    brick = Brick(
                        id=brick_id,
                        brick_type="quarter",
                        position=Position(x_pos, y_pos),
                    )
                    brick_list.append(brick)
                    brick_id += 1
                    break
                else:
                    break

    return brick_list
