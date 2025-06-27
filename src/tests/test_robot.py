from ..models.robot import Robot
from ..models.brick import Brick
from ..models.common import Position
from ..configs.config import load_wall_config, Config
import pytest


@pytest.fixture
def test_config() -> Config:
    return load_wall_config("test_small_wall")


@pytest.fixture
def robot(test_config: Config) -> Robot:
    robot = Robot(test_config)
    Brick.configure(test_config)
    return robot


def test_can_reach_brick(robot: Robot) -> None:
    # Brick within reach
    brick_in_reach = Brick(
        id=1,
        brick_type="full",
        position=Position(robot.position.x - 100, robot.position.y + 50),
    )
    assert robot.can_reach_brick(brick_in_reach) is True

    # Brick outside horizontal reach
    brick_too_far_x = Brick(
        id=2,
        brick_type="full",
        position=Position(robot.position.x + 500, robot.position.y + 50),
    )
    assert robot.can_reach_brick(brick_too_far_x) is False

    # Brick outside vertical reach
    brick_too_far_y = Brick(
        id=3,
        brick_type="full",
        position=Position(robot.position.x, robot.position.y + 500),
    )
    assert robot.can_reach_brick(brick_too_far_y) is False

    # Brick at center of robot position
    brick_at_center = Brick(
        id=4,
        brick_type="full",
        position=Position(robot.position.x - 50, robot.position.y),
    )
    assert robot.can_reach_brick(brick_at_center) is True
