from enum import Enum
from dataclasses import dataclass
from .common import Position
from ..configs.config import Config, BrickDimensions
from typing import ClassVar


class BrickType(Enum):
    FULL = "full"
    HALF = "half"


class BrickState(Enum):
    PLANNED = "planned"
    BUILT = "built"


@dataclass
class Brick:
    id: int
    brick_type: str 
    position: Position
    state: BrickState = BrickState.PLANNED
    stride_id: int | None = None

    # Class-level config 
    _brick_configs: ClassVar[dict[str, BrickDimensions]] = {}

    @classmethod
    def configure(cls, config: Config) -> None:
        """Configure all brick types from config"""
        cls._brick_configs = config['bricks']
    
    @property
    def width(self) -> float:
        return self._brick_configs[self.brick_type]['width']

    @property  
    def length(self) -> float:
        return self._brick_configs[self.brick_type]['length']

    @property
    def height(self) -> float:
        return self._brick_configs[self.brick_type]['height']

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
