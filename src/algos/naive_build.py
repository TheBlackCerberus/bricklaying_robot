from ..models.wall import Wall
from ..models.robot import Robot
from ..models.brick import Brick
from ..models.stride import StrideManager, Stride
from ..models.common import Position, Movement
from ..configs.config import Config


def naive_build_algorithm(
    wall: Wall, robot: Robot, stride_manager: StrideManager, config: Config
) -> tuple[list[Stride], list[Movement]]:
    """
    Simple grid pattern using center-based reach.

    Moves robot in a zig-zag pattern, starting from the leftmost position.

    # With center-based reach, we can use simpler positioning since
    # we don't need to worry about boundary bricks as much.
    """

    wall_width = config["wall"]["width"]
    wall_height = config["wall"]["height"]
    robot_reach_width = config["robot"]["reach_width"]
    robot_reach_height = config["robot"]["reach_height"]

    movements: list[Movement] = []
    strides: list[Stride] = []

    x_positions: list[float] = []
    x = robot_reach_width / 2
    while x <= wall_width:
        x_positions.append(x)
        x += robot_reach_width

    # Add a final position to ensure we can reach the rightmost bricks
    # Calculate the rightmost possible robot position that can still reach the wall edge
    rightmost_robot_x = wall_width - robot_reach_width / 2
    if len(x_positions) == 0 or x_positions[-1] < rightmost_robot_x:
        x_positions.append(rightmost_robot_x)

    y_positions: list[float] = []
    y = 0.0
    while y < wall.height:
        y_positions.append(y)
        if y + robot_reach_height >= wall_height:
            break  # Last position
        y += robot_reach_height

    unbuilt_bricks: list[Brick] = list(wall.bricks)

    current_robot_pos = Position(robot.position.x, robot.position.y)

    for y_idx, y_pos in enumerate(y_positions):
        # zig-zag / even -> left to right, odd -> right to left
        x_range = x_positions if y_idx % 2 == 0 else x_positions[::-1]

        for x_pos in x_range:
            # Calculate new position
            new_pos = Position(x_pos, y_pos)
            if current_robot_pos != new_pos:
                movements.append(Movement(current_robot_pos, new_pos))
                current_robot_pos = new_pos

            # Temp
            original_pos = robot.position
            robot.position = current_robot_pos

            reachable: list[Brick] = []
            for brick in unbuilt_bricks[:]:
                if robot.can_reach_brick(brick):
                    reachable.append(brick)

            # Restore
            robot.position = original_pos

            # Create stride and add bricks
            if reachable:
                current_stride: Stride = stride_manager.create_stride(current_robot_pos)
                for brick in reachable:
                    current_stride.add_brick(brick)
                    unbuilt_bricks.remove(brick)
                strides.append(current_stride)

    built_count = wall.total_bricks - len(unbuilt_bricks)
    print(f"Built {built_count}/{wall.total_bricks} bricks")

    return strides, movements
