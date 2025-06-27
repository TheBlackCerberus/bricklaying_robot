from ..models.wall import Wall
from ..models.brick import Brick
from ..models.common import Position
from ..configs.config import load_wall_config, Config
import pytest


@pytest.fixture
def wall_config() -> Config:
    return load_wall_config("test_small_wall")


@pytest.fixture
def wall(wall_config: Config) -> Wall:
    """Create a wall instance for testing"""
    wall = Wall(wall_config)
    Brick.configure(wall_config)
    return wall


def test_is_brick_in_wall(wall: Wall) -> None:
    """Test if bricks are correctly identified as inside or outside the wall"""
    # Test brick inside wall
    brick_inside = Brick(id=1, brick_type="full", position=Position(100, 100))
    assert wall.is_brick_in_wall(brick_inside) is True

    # Test bricks outside various wall boundaries
    brick_left_outside = Brick(id=2, brick_type="full", position=Position(-10, 100))
    assert wall.is_brick_in_wall(brick_left_outside) is False

    brick_right_outside = Brick(
        id=3, brick_type="full", position=Position(wall.width - 10, 100)
    )
    assert wall.is_brick_in_wall(brick_right_outside) is False

    brick_top_outside = Brick(
        id=4, brick_type="full", position=Position(100, wall.height + 10)
    )
    assert wall.is_brick_in_wall(brick_top_outside) is False

    brick_bottom_outside = Brick(id=5, brick_type="full", position=Position(100, -10))
    assert wall.is_brick_in_wall(brick_bottom_outside) is False

    # Test brick exactly at edge
    brick_at_edge = Brick(id=6, brick_type="full", position=Position(0, 0))
    assert wall.is_brick_in_wall(brick_at_edge) is True


def test_column_calculation(wall: Wall) -> None:
    """Test the column calculation functionality"""

    def calculate_column(x_position: float, row: int) -> int:
        return wall._calculate_column(x_position, row)

    # Test column calculations at various positions
    col = calculate_column(0, 0)
    assert col == 0

    min_brick_length = min(brick["length"] for brick in wall.config["bricks"].values())
    head_joint = wall.config["joints"]["head_joint"]
    unit_width = min_brick_length + head_joint

    col = calculate_column(3 * unit_width, 0)
    assert col == 3

    col = calculate_column(3.7 * unit_width, 0)
    assert col == 3

    # Test that row doesn't affect column calculation
    col_row0 = calculate_column(2 * unit_width, 0)
    col_row1 = calculate_column(2 * unit_width, 1)
    assert col_row0 == col_row1


def test_validate_brick_placement(wall: Wall) -> None:
    """Test brick placement validation for overlapping bricks"""
    # Add first brick to wall
    brick1 = Brick(id=1, brick_type="full", position=Position(100, 100))
    wall.add_brick(brick1)

    # Test non-overlapping brick
    brick2 = Brick(id=2, brick_type="full", position=Position(400, 100))
    assert wall.validate_brick_placement(brick2) is True

    # Test direct overlap
    brick3 = Brick(id=3, brick_type="full", position=Position(100, 100))
    assert wall.validate_brick_placement(brick3) is False

    # Test horizontal overlap with head joint
    brick_length = wall.config["bricks"]["full"]["length"]
    head_joint = wall.config["joints"]["head_joint"]

    brick4 = Brick(
        id=4, brick_type="full", position=Position(100 + brick_length - 1, 100)
    )
    assert wall.validate_brick_placement(brick4) is False

    brick5 = Brick(
        id=5,
        brick_type="full",
        position=Position(100 + brick_length + head_joint + 1, 100),
    )
    assert wall.validate_brick_placement(brick5) is True

    # Test vertical overlap with bed joint
    brick_height = wall.config["bricks"]["full"]["height"]
    bed_joint = wall.config["joints"]["bed_joint"]

    brick6 = Brick(
        id=6,
        brick_type="full",
        position=Position(100, 100 + brick_height + bed_joint + 1),
    )
    assert wall.validate_brick_placement(brick6) is True

    brick7 = Brick(
        id=7, brick_type="full", position=Position(100, 100 + brick_height - 10)
    )
    assert wall.validate_brick_placement(brick7) is False
