import yaml
from pathlib import Path
from typing import TypedDict


class BrickDimensions(TypedDict):
    width: float
    length: float
    height: float

class JointsConfig(TypedDict):
    head_joint: float
    bed_joint: float


class BricksConfig(TypedDict):
    full: BrickDimensions
    half: BrickDimensions
    quarter: BrickDimensions


class WallConfig(TypedDict):
    width: float
    height: float


class RobotConfig(TypedDict):
    reach_width: float
    reach_height: float


class Config(TypedDict):
    name: str
    bricks: dict[str, BrickDimensions]
    joints: JointsConfig
    wall: WallConfig
    robot: RobotConfig


def load_wall_config(config_name: str) -> Config:
    config_path = Path(f"src/configs/{config_name}.yaml")

    with open(config_path, "r") as file:
        data = yaml.safe_load(file)  

    return data 
