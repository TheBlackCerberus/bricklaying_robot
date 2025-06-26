from dataclasses import dataclass


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Movement:
    from_pos: Position
    to_pos: Position

    def __str__(self) -> str:
        return (f"({self.from_pos.x:.0f}, {self.from_pos.y:.0f}) → "
                f"({self.to_pos.x:.0f}, {self.to_pos.y:.0f})")
