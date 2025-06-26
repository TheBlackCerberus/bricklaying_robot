from .brick import Brick
from .common import Position


class Stride:
    def __init__(self, id: int, robot_position: Position, color: tuple[int, int, int]):
        self.id: int = id
        self.robot_position: Position = robot_position
        self.bricks: list[Brick] = []
        self.color: tuple[int, int, int] = color

    @property
    def brick_count(self) -> int:
        return len(self.bricks)

    def add_brick(self, brick: Brick) -> None:
        self.bricks.append(brick)
        brick.stride_id = self.id


class StrideManager:
    def __init__(self) -> None:
        self.strides: list[Stride] = []
        self.colors: list[tuple[int, int, int]] = [
            (100, 149, 237),  # Cornflower blue
            (220, 20, 60),    # Crimson
            (255, 165, 0),    # Orange
            (50, 205, 50),    # Lime green
            (138, 43, 226),   # Blue violet
            (255, 20, 147),   # Deep pink
            (0, 191, 255),    # Deep sky blue
            (255, 215, 0),    # Gold
            (128, 0, 128),    # Purple
            (255, 69, 0),     # Red orange
            (46, 139, 87),    # Sea green
            (255, 105, 180),  # Hot pink
            (30, 144, 255),   # Dodger blue
            (255, 140, 0),    # Dark orange
            (147, 112, 219),  # Medium purple
            (220, 220, 220),  # Light gray
        ]
        self.color_index = 0

    def create_stride(self, robot_position: Position) -> Stride:
        stride = Stride(
            id=len(self.strides),
            robot_position=robot_position,
            color=self._get_next_color(),
        )
        self.strides.append(stride)
        return stride

    def _get_next_color(self) -> tuple[int, int, int]:
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        return color
