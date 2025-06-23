# Brick dimensions in mm
FULL_BRICK_LENGTH: int = 210
FULL_BRICK_WIDTH: int = 100
FULL_BRICK_HEIGHT: int = 50

HALF_BRICK_LENGTH: int = 100
HALF_BRICK_WIDTH: int = 100
HALF_BRICK_HEIGHT: int = 50

# Joint dimensions in mm
HEAD_JOINT: int = 10  # Vertical joint between bricks
BED_JOINT: float = 12.5  # Horizontal joint between courses

COURSE_HEIGHT: float = FULL_BRICK_HEIGHT + BED_JOINT  

# Wall dimensions
WALL_WIDTH: int = 2300
WALL_HEIGHT: int = 2000

# Robot capabilities
ROBOT_REACH_WIDTH: int = 800
ROBOT_REACH_HEIGHT: int = 1300