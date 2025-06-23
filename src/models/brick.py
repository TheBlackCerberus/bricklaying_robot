from enum import Enum
from dataclasses import dataclass
from .common import Position
from ..constants import FULL_BRICK_LENGTH, HALF_BRICK_LENGTH, FULL_BRICK_HEIGHT


class BrickType(Enum):
    FULL = "full"
    HALF = "half"


class BrickState(Enum):
    PLANNED = "planned"
    BUILT = "built"


@dataclass
class Brick:
    id: int
    type: BrickType
    position: Position
    state: BrickState = BrickState.PLANNED

    @property
    def width(self) -> float:
        return FULL_BRICK_LENGTH if self.type == BrickType.FULL else HALF_BRICK_LENGTH

    @property
    def height(self) -> float:
        return FULL_BRICK_HEIGHT

    @property
    def center(self) -> Position:
        return Position(
            self.position.x + self.width / 2, self.position.y + self.height / 2
        )

    @property
    def bottom_left(self) -> Position:
        return Position(self.position.x, self.position.y)

    @property
    def bottom_right(self) -> Position:
        return Position(self.position.x + self.width, self.position.y)

    @property
    def top_left(self) -> Position:
        return Position(self.position.x, self.position.y + self.height)

    @property
    def top_right(self) -> Position:
        return Position(self.position.x + self.width, self.position.y + self.height)

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within this brick"""
        return (
            self.bottom_left.x <= x <= self.bottom_right.x
            and self.bottom_left.y <= y <= self.top_left.y
        )
