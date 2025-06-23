from .models.brick import BrickState, Brick, BrickType
from .models.wall import Wall
from .models.common import Position
from .constants import COURSE_HEIGHT, HEAD_JOINT


class AsciiRenderer:
    """Simple ASCII renderer"""

    def __init__(self, debug_mode: bool = False):
        self.BRICK_CHARS: dict[BrickState, str] = {
            BrickState.PLANNED: "░░",
            BrickState.BUILT: "▓▓",
        }
        self.MAX_COURSES_TO_SHOW = 32
        self.debug_mode = debug_mode

    def render_wall(self, wall: Wall):
        """Render wall in simple ASCII format"""
        # Group bricks by course
        courses: dict[int, list[Brick]] = {}
        out_of_bounds_bricks: list[Brick] = []

        for brick in wall.bricks:
            # Check if brick is within wall bounds
            # TODO: add the helper functions for this
            if not wall.is_brick_in_wall(brick):
                out_of_bounds_bricks.append(brick)
                continue

            course_num = int(brick.position.y / COURSE_HEIGHT)
            if course_num not in courses:
                courses[course_num] = []
            courses[course_num].append(brick)

        # Warn about out of bounds bricks
        if out_of_bounds_bricks and self.debug_mode:
            print(f"WARNING: {len(out_of_bounds_bricks)} bricks are out of bounds!")
            for brick in out_of_bounds_bricks:
                print(
                    f"  - Brick {brick.id} at ({brick.position.x}, {brick.position.y})"
                )
            print()

        # Determine how many courses to show
        num_courses = min(len(courses), self.MAX_COURSES_TO_SHOW)

        for course_num in range(num_courses - 1, -1, -1):
            course_bricks = wall.get_bricks_in_course(course_num)
            if not course_bricks:
                continue
            course_bricks = sorted(course_bricks, key=lambda b: b.position.x)

            line: str = ""
            expected_x = 0.0  # Track where we expect the next brick

            for brick in course_bricks:
                # debug
                if self.debug_mode and brick.position.x > expected_x:
                    gap_size = brick.position.x - expected_x
                    line += f"[GAP:{gap_size:.0f}mm] "

                char = self.BRICK_CHARS[brick.state]

                # Full bricks get 4 characters (░░░░ or ▓▓▓▓)
                # Half bricks get 2 characters (░░ or ▓▓)
                if brick.type == BrickType.FULL:
                    line += char * 2  # ░░░░ or ▓▓▓▓
                else:
                    line += char  # ░░ or ▓▓

                line += " "

                # Update expected position
                expected_x = brick.position.x + brick.width + HEAD_JOINT

            print(line.rstrip())


def test_simple_renderer():
    """Test the simple renderer"""

    wall = Wall()

    # Course 0 - starts with full brick
    wall.add_brick(Brick(0, BrickType.FULL, Position(0, 0)))
    wall.add_brick(Brick(1, BrickType.FULL, Position(220, 0)))
    wall.add_brick(Brick(2, BrickType.FULL, Position(440, 0)))
    wall.add_brick(Brick(3, BrickType.FULL, Position(660, 0)))
    wall.add_brick(Brick(4, BrickType.FULL, Position(880, 0)))
    wall.add_brick(Brick(5, BrickType.FULL, Position(1100, 0)))
    wall.add_brick(Brick(6, BrickType.FULL, Position(1320, 0)))
    wall.add_brick(Brick(7, BrickType.FULL, Position(1540, 0)))
    wall.add_brick(Brick(8, BrickType.FULL, Position(1760, 0)))
    wall.add_brick(Brick(9, BrickType.FULL, Position(1980, 0)))
    wall.add_brick(Brick(10, BrickType.HALF, Position(2200, 0)))

    # # Course 1 - starts with half brick
    # wall.add_brick(Brick(5, BrickType.HALF, Position(0, 62.5)))
    # wall.add_brick(Brick(6, BrickType.FULL, Position(110, 62.5)))
    # wall.add_brick(Brick(7, BrickType.FULL, Position(330, 62.5)))
    # wall.add_brick(Brick(8, BrickType.FULL, Position(550, 62.5)))
    # wall.add_brick(Brick(9, BrickType.FULL, Position(770, 62.5)))

    # wall.add_brick(Brick(10, BrickType.FULL, Position(0, 125)))
    # wall.add_brick(Brick(11, BrickType.FULL, Position(110, 125)))

    wall.bricks[0].state = BrickState.BUILT
    wall.bricks[1].state = BrickState.BUILT

    renderer = AsciiRenderer(debug_mode=True)
    renderer.render_wall(wall)


if __name__ == "__main__":
    test_simple_renderer()
