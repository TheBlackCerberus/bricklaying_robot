from .models.wall import Wall
from .models.robot import Robot
from .models.common import Position
from .models.brick import BrickState, Brick, BrickType
from .renderer import AsciiRenderer
from .constants import (
    WALL_HEIGHT,
    COURSE_HEIGHT,
    FULL_BRICK_HEIGHT,
    HALF_BRICK_LENGTH,
    HEAD_JOINT,
    FULL_BRICK_LENGTH,
)
import os


def calculate_brick_positions_stretcher_bond(wall: Wall) -> list[Brick]:

    brick_list: list[Brick] = []
    brick_id = 0

    num_courses = int(WALL_HEIGHT / COURSE_HEIGHT)

    for c in range(num_courses):

        # calc the y for course to include bed joints
        y_pos = c * COURSE_HEIGHT

        if y_pos + FULL_BRICK_HEIGHT > wall.height:
            break

        # odd numbers
        starts_with_half = c % 2 == 1

        x_pos = 0
        bricks_in_course: list[Brick] = []

        if starts_with_half:
            if x_pos + HALF_BRICK_LENGTH <= wall.width:
                brick = Brick(
                    id=brick_id, type=BrickType.HALF, position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += HALF_BRICK_LENGTH + HEAD_JOINT

        while x_pos < wall.width:
            remaining_space = wall.width - x_pos

            if remaining_space >= FULL_BRICK_LENGTH:
                brick = Brick(
                    id=brick_id, type=BrickType.FULL, position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += FULL_BRICK_LENGTH + HEAD_JOINT

            # If full brick doesn't fit, try half brick
            # this is a bit random and doesn't follow
            elif remaining_space >= HALF_BRICK_LENGTH:
                brick = Brick(
                    id=brick_id, type=BrickType.HALF, position=Position(x_pos, y_pos)
                )
                bricks_in_course.append(brick)
                brick_id += 1
                x_pos += HALF_BRICK_LENGTH + HEAD_JOINT

            else:
                # No more bricks fit in this course
                break

        brick_list.extend(bricks_in_course)

    return brick_list


def main() -> None:
    wall = Wall()
    robot = Robot()

    # Brick layout
    bricks: list[Brick] = calculate_brick_positions_stretcher_bond(wall=wall)
    for brick in bricks:
        wall.add_brick(brick)

    renderer = AsciiRenderer()
    current_brick_index = 0

    while current_brick_index < len(bricks):
        # fresh screen
        os.system("cls" if os.name == "nt" else "clear")

        # Show current state
        print(f"Building Progress: {current_brick_index}/{len(bricks)} bricks")
        print(f"Wall Progress: {wall.completion_percentage:.2f}%")
        print(f"Robot Position: ({robot.position.x}, {robot.position.y})")
        print("-" * 50)

        renderer.render_wall(wall)

        # user input
        input("Press ENTER to place next brick...")

        # Build next brick
        brick = bricks[current_brick_index]
        brick.state = BrickState.BUILT
        current_brick_index += 1
    
    # Final display when all bricks are built
    if current_brick_index >= len(bricks):
        os.system("cls" if os.name == "nt" else "clear")
        print("🎉 Wall construction complete!")
        print(f"Wall Progress: {wall.completion_percentage:.2f}%")
        print(f"Final Progress: {len(bricks)}/{len(bricks)} bricks")
        print(f"Robot Position: ({robot.position.x}, {robot.position.y})")
        print("-" * 50)
        renderer.render_wall(wall)


if __name__ == "__main__":
    main()
