from ..algos.naive_build import naive_build_algorithm
from ..models.wall import Wall
from ..models.robot import Robot
from ..models.brick import Brick
from ..models.stride import StrideManager
from ..configs.config import load_wall_config, Config
from ..bonds.stretcher_bond import calculate_stretcher_bond
import pytest


@pytest.fixture
def test_config() -> Config:
    return load_wall_config("test_small_wall")


@pytest.fixture
def wall_with_bricks(test_config: Config) -> Wall:
    wall = Wall(test_config)
    Brick.configure(test_config)
    bricks = calculate_stretcher_bond(wall, test_config)

    for brick in bricks:
        wall.add_brick(brick)

    return wall


@pytest.fixture
def robot(test_config: Config) -> Robot:
    return Robot(test_config)


@pytest.fixture
def stride_manager() -> StrideManager:
    return StrideManager()


def test_naive_build_algorithm_creates_strides(
    wall_with_bricks: Wall,
    robot: Robot,
    stride_manager: StrideManager,
    test_config: Config,
) -> None:
    strides, movements = naive_build_algorithm(
        wall_with_bricks, robot, stride_manager, test_config
    )

    assert len(strides) > 0
    total_bricks_in_strides = sum(len(stride.bricks) for stride in strides)
    assert total_bricks_in_strides == len(wall_with_bricks.bricks)

    assert len(movements) > 0

    if movements:
        assert movements[0].from_pos.x == robot.reach_width / 2
        assert movements[0].from_pos.y == 0


def test_naive_build_algorithm_coverage(
    wall_with_bricks: Wall,
    robot: Robot,
    stride_manager: StrideManager,
    test_config: Config,
) -> None:
    strides, _ = naive_build_algorithm(
        wall_with_bricks, robot, stride_manager, test_config
    )

    total_bricks_in_strides = 0
    for stride in strides:
        total_bricks_in_strides += len(stride.bricks)

    assert total_bricks_in_strides == len(wall_with_bricks.bricks)
