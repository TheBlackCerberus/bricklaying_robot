from .common import Position
from .brick import Brick, BrickState
from .wall import Wall
from ..configs.config import Config


class Robot:
    def __init__(self, config: Config) -> None:
        self.reach_width = config["robot"]["reach_width"]
        self.reach_height = config["robot"]["reach_height"]
        self.position = Position(self.reach_width / 2, 0)
        self.movement_count = 0
        self.current_stride_id = 0

    @property
    def reach_area(self) -> tuple[float, float, float, float]:
        """Returns current reach area"""
        x_min: float = self.position.x - self.reach_width / 2
        x_max: float = self.position.x + self.reach_width / 2
        y_min: float = self.position.y
        y_max: float = self.position.y + self.reach_height
        return (x_min, y_min, x_max, y_max)

    def _get_brick_center(self, brick: Brick) -> tuple[float, float]:
        return (brick.position.x + brick.width / 2, brick.position.y + brick.height / 2)

    def can_reach_brick(self, brick: Brick) -> bool:
        """Check if robot can reach a brick based on its center position.
        With center-based reach, we can use simpler positioning since
        we don't need to worry about boundary bricks as much.
        It's safe to assume that robot would pick up the brick
        in the center of the brick.
        """
        x_min = self.position.x - self.reach_width / 2
        x_max = self.position.x + self.reach_width / 2
        y_min = self.position.y
        y_max = self.position.y + self.reach_height

        center_x, center_y = self._get_brick_center(brick)

        return x_min <= center_x <= x_max and y_min <= center_y <= y_max

    def move_to(self, x: float, y: float) -> None:
        """Move robot to new position"""
        if x != self.position.x or y != self.position.y:
            self.movement_count += 1
            self.position.x = x
            self.position.y = y
            self.current_stride_id += 1

    def get_reachable_bricks(self, wall: Wall) -> list[Brick]:
        """Get all bricks reachable from current position"""
        return [
            b
            for b in wall.bricks
            if self.can_reach_brick(b) and b.state == BrickState.PLANNED
        ]
