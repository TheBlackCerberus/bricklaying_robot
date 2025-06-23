from .common import Position
from .brick import Brick, BrickState
from .wall import Wall
from ..constants import ROBOT_REACH_WIDTH, ROBOT_REACH_HEIGHT


class Robot:
    def __init__(self) -> None:
        self.position = Position(ROBOT_REACH_WIDTH / 2, 0)
        self.reach_width = ROBOT_REACH_WIDTH
        self.reach_height = ROBOT_REACH_HEIGHT
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
    
    def can_reach_brick(self, brick: Brick) -> bool:
        """Check if robot can reach a brick from current position"""
        x_min, y_min, x_max, y_max = self.reach_area
        # Check if brick is fully within reach
        return (x_min <= brick.position.x and 
                brick.position.x + brick.width <= x_max and
                y_min <= brick.position.y and 
                brick.position.y + brick.height <= y_max)
    
    def move_to(self, x: float, y: float) -> None:
        """Move robot to new position"""
        if x != self.position.x or y != self.position.y:
            self.movement_count += 1
            self.position.x = x
            self.position.y = y
            self.current_stride_id += 1
    
    def get_reachable_bricks(self, wall: Wall) -> list[Brick]:
        """Get all bricks reachable from current position"""
        return [b for b in wall.bricks if self.can_reach_brick(b) and b.state == BrickState.PLANNED]