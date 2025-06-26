from .brick import Brick, BrickState
from ..configs.config import Config


class Wall:
    def __init__(self, config: Config) -> None:
        self.width: float = config['wall']['width']
        self.height: float = config['wall']['height']
        self.config = config  
        self.bricks: list[Brick] = []
        self.brick_grid: dict[tuple[int, int], Brick] = {}  # (row, col) -> Brick

    def add_brick(self, brick: Brick) -> None:
        """Add a brick to the wall"""
        course_height = self.config['joints']['bed_joint'] + self.config['bricks']['full']['height']
        self.bricks.append(brick)
        row = int(brick.position.y / course_height)
        col = self._calculate_column(brick.position.x, row)
        self.brick_grid[(row, col)] = brick

    def _calculate_column(self, x_position: float, row: int) -> int:
        """Calculate which column a brick belongs to based on x position.

        TODO: This is the stretcher bond
        """
        half_brick_length = self.config['bricks']['half']['length']
        full_brick_length = self.config['bricks']['full']['length']
        head_joint = self.config['joints']['head_joint']
        
        # For stretcher bond, odd rows are offset
        is_offset_row = row % 2 == 1

        if is_offset_row:
            # Offset rows: half, full, full ...
            if x_position < half_brick_length:
                return 0  # First half brick
            else:
                adjusted_x = x_position - half_brick_length - head_joint
                return 1 + int(adjusted_x / (full_brick_length + head_joint))
        else:
            # Normal rows: full, full, full...
            return int(x_position / (full_brick_length + head_joint))

    def get_brick_at_position(self, x: float, y: float) -> Brick | None:
        """Get brick at specific coordinates"""
        for brick in self.bricks:
            if brick.contains_point(x, y):
                return brick
        return None

    def get_brick_at_grid(self, row: int, col: int) -> Brick | None:
        """Get brick at specific grid position"""
        return self.brick_grid.get((row, col))

    def get_bricks_in_region(
        self, x: float, y: float, width: float, height: float
    ) -> list[Brick]:
        """Get all bricks within a rectangular region (stride)"""
        return [
            brick
            for brick in self.bricks
            if (
                x <= brick.position.x <= x + width
                and y <= brick.position.y <= y + height
                and brick.position.x + brick.width <= x + width
                and brick.position.y + brick.height <= y + height
            )
        ]

    def get_bricks_in_course(self, course: int) -> list[Brick]:
        """Get all bricks in a specific course (row)"""
        course_height = self.config['joints']['bed_joint'] + self.config['bricks']['full']['height']
        return [
            brick
            for brick in self.bricks
            if int(brick.position.y / course_height) == course
        ]

    def validate_brick_placement(self, brick: Brick) -> bool:
        """Check if a brick can be placed without overlapping existing bricks"""
        for existing_brick in self.bricks:
            if self._bricks_overlap(brick, existing_brick):
                return False
        return True

    def is_brick_in_wall(self, brick: Brick) -> bool:
        if (
            brick.position.x < 0
            or brick.position.x + brick.width > self.width
            or brick.position.y < 0
            or brick.position.y + brick.height > self.height
        ):
            return False
        return True

    def _bricks_overlap(self, brick1: Brick, brick2: Brick) -> bool:
        """Check if two bricks overlap (accounting for joints)"""
        head_joint = self.config['joints']['head_joint']
        return not (
            brick1.position.x + brick1.width + head_joint <= brick2.position.x
            or brick2.position.x + brick2.width + head_joint <= brick1.position.x
            or brick1.position.y + brick1.height <= brick2.position.y
            or brick2.position.y + brick2.height <= brick1.position.y
        )

    @property
    def num_courses(self) -> int:
        """Calculate number of courses that fit in wall height"""
        course_height = self.config['joints']['bed_joint'] + self.config['bricks']['full']['height']
        return int(self.height / course_height)

    @property
    def total_bricks(self) -> int:
        return len(self.bricks)

    @property
    def built_bricks(self) -> list[Brick]:
        return [b for b in self.bricks if b.state == BrickState.BUILT]

    @property
    def unbuilt_bricks(self) -> list[Brick]:
        return [b for b in self.bricks if b.state == BrickState.PLANNED]

    @property
    def completion_percentage(self) -> float:
        if not self.bricks:
            return 0.0
        return len(self.built_bricks) / len(self.bricks) * 100
