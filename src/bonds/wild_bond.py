from ..models.wall import Wall
from ..models.common import Position
from ..models.brick import Brick
from ..configs.config import Config
import random

# set random seed
random.seed(44)


def calculate_wild_bond(wall: Wall, config: Config) -> list[Brick]:
    """
    Calculate Wild Bond (Wildverband) pattern.

    Rules:
    1. Random mix of full and half bricks
    2. 1/4 brick offset to prevent vertical joint alignment
    3. Maximum 6 consecutive "staggered steps"
    4. No two joints directly above each other
    """
    wall_height = config["wall"]["height"]
    wall_width = config["wall"]["width"]
    course_height = config["joints"]["bed_joint"] + config["bricks"]["full"]["height"]

    full_length = config["bricks"]["full"]["length"]  # 210mm
    half_length = config["bricks"]["half"]["length"]  # 100mm
    quarter_length = config["bricks"]["quarter"]["length"]  # 45mm
    head_joint = config["joints"]["head_joint"]

    brick_list: list[Brick] = []
    brick_id = 0
    num_courses = int(wall_height / course_height)

    course_patterns = _generate_wild_bond_pattern(
        num_courses=num_courses,
        wall_width=wall_width,
        full_length=full_length,
        half_length=half_length,
        quarter_length=quarter_length,
        head_joint=head_joint,
    )

    for course_num, pattern in enumerate(course_patterns):
        y_pos = course_num * course_height
        x_pos = 0.0

        for brick_type in pattern:
            brick = Brick(
                id=brick_id, brick_type=brick_type, position=Position(x_pos, y_pos)
            )
            brick_list.append(brick)
            brick_id += 1

            if brick_type == "full":
                x_pos += full_length + head_joint
            elif brick_type == "half":
                x_pos += half_length + head_joint
            else:  # quarter
                x_pos += quarter_length + head_joint

    return brick_list


def _generate_wild_bond_pattern(
    num_courses: int,
    wall_width: float,
    full_length: float,
    half_length: float,
    quarter_length: float,
    head_joint: float,
) -> list[list[str]]:
    patterns: list[list[str]] = []
    joint_positions_by_course: list[list[float]] = []

    for course in range(num_courses):
        pattern, joint_positions = _calculate_course_pattern(
            course_num=course,
            wall_width=wall_width,
            full_length=full_length,
            half_length=half_length,
            quarter_length=quarter_length,
            head_joint=head_joint,
            previous_joints=(
                joint_positions_by_course[-1] if joint_positions_by_course else []
            ),
        )

        patterns.append(pattern)
        joint_positions_by_course.append(joint_positions)

    return patterns


def _calculate_course_pattern(
    course_num: int,
    wall_width: float,
    full_length: float,
    half_length: float,
    quarter_length: float,
    head_joint: float,
    previous_joints: list[float],
) -> tuple[list[str], list[float]]:
    pattern: list[str] = []
    joint_positions: list[float] = []
    x_pos = 0.0
    consecutive_steps = 0

    # (1/4 brick offset)
    if course_num % 2 == 1:
        pattern.append("quarter")
        x_pos += quarter_length + head_joint
        joint_positions.append(quarter_length)

    while x_pos + half_length <= wall_width:
        remaining = wall_width - x_pos

        options: list[str] = []
        if remaining >= full_length + head_joint:
            options.append("full")
        if remaining >= half_length + head_joint:
            options.append("half")

        if remaining < full_length + head_joint:
            if remaining >= half_length:
                options = ["half"]
            else:
                break

        # No consecutive half bricks
        if pattern and pattern[-1] == "half" and "half" in options:
            options.remove("half")

        if not options:
            if remaining >= quarter_length:
                pattern.append("quarter")
                joint_positions.append(x_pos + quarter_length)
            break

        # Prevent too many teet steps
        if consecutive_steps >= 6 and "full" in options:
            brick_type = "full"
            consecutive_steps = 0
        else:
            index = (course_num + int(x_pos / 100)) % len(options)
            brick_type = options[index]

        length = full_length if brick_type == "full" else half_length
        joint_pos = x_pos + length

        # Check for vertical joint alignment
        aligned = False
        for prev_joint in previous_joints:
            if abs(joint_pos - prev_joint) < 1:
                aligned = True
                break

        # Choose alternative brick type if aligned
        if aligned and len(options) > 1:
            other_type = "half" if brick_type == "full" else "full"
            if other_type in options:
                brick_type = other_type
                length = full_length if brick_type == "full" else half_length
                joint_pos = x_pos + length

        pattern.append(brick_type)
        joint_positions.append(joint_pos)

        x_pos = joint_pos + head_joint

        # Track staggered steps
        if len(joint_positions) >= 2:
            step_diff = abs(joint_positions[-1] - joint_positions[-2])
            if step_diff < half_length:
                consecutive_steps += 1
            else:
                consecutive_steps = 0

    remaining = wall_width - x_pos
    if remaining >= quarter_length:
        pattern.append("quarter")
        joint_positions.append(x_pos + quarter_length)

    return pattern, joint_positions
