from .models.wall import Wall
from .models.brick import Brick, BrickState
from .models.robot import Robot
from .models.stride import StrideManager, Stride
from .configs.config import Config
import pygame


class PygameRenderer:
    """Simple pygame-based renderer with scaling"""

    def __init__(
        self, config: Config, target_scale: float = 0.4, debug_mode: bool = False
    ):
        pygame.init()

        self.config = config
        self.target_scale = target_scale
        self.debug_mode = debug_mode

        # Default window size
        self.window_width = 1200
        self.window_height = 800

        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Wall Visualization")

        self.COLORS = {
            "background": (240, 240, 240),
            "wall_background": (255, 255, 255),
            "planned_brick": (200, 200, 200),
            "built_brick": (180, 100, 50),
            "brick_outline": (100, 100, 100),
            "text": (0, 0, 0),
            "grid": (230, 230, 230),
        }

        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)

        self._calculate_layout()

    def _calculate_layout(self):
        # Reserve space for info panel and legend
        info_panel_height = 120
        legend_width = 110
        base_margin = 30

        available_width = self.window_width - (legend_width + 2 * base_margin)
        available_height = self.window_height - (info_panel_height + 2 * base_margin)
        wall_width_mm = self.config["wall"]["width"]
        wall_height_mm = self.config["wall"]["height"]

        scale_x = available_width / wall_width_mm
        scale_y = available_height / wall_height_mm

        self.scale = min(scale_x, scale_y, self.target_scale)

        self.wall_width_px = int(wall_width_mm * self.scale)
        self.wall_height_px = int(wall_height_mm * self.scale)

        remaining_width = available_width - self.wall_width_px
        remaining_height = available_height - self.wall_height_px

        self.wall_x = base_margin + remaining_width // 2
        self.wall_y = base_margin + remaining_height // 2

        # Legend positioning (right side)
        self.legend_x = self.window_width - legend_width
        self.legend_y = base_margin

        # Info panel positioning (bottom)
        self.info_x = base_margin
        self.info_y = self.window_height - info_panel_height + 10

    def mm_to_px(self, mm: float) -> int:
        return int(mm * self.scale)

    def render_wall(
        self,
        wall: Wall,
        robot: Robot | None = None,
        stride_manager: StrideManager | None = None,
    ):

        self.screen.fill(self.COLORS["background"])

        wall_rect = pygame.Rect(
            self.wall_x, self.wall_y, self.wall_width_px, self.wall_height_px
        )
        pygame.draw.rect(self.screen, self.COLORS["wall_background"], wall_rect)
        pygame.draw.rect(self.screen, self.COLORS["brick_outline"], wall_rect, 2)

        if self.debug_mode:
            self._draw_grid()

        brick_to_stride: dict[int, Stride] = {}
        if stride_manager:
            for stride in stride_manager.strides:
                for brick in stride.bricks:
                    brick_to_stride[brick.id] = stride

        for course in range(wall.num_courses):
            course_bricks = wall.get_bricks_in_course(course)
            for brick in course_bricks:
                stride_color = None
                if brick.id in brick_to_stride:
                    stride = brick_to_stride[brick.id]
                    stride_color = stride.color
                self._draw_brick(brick, stride_color)

        if stride_manager:
            self._draw_stride_legend(stride_manager)

        self._draw_info_panel(wall, robot)
        pygame.display.flip()

    def _draw_brick(
        self, brick: Brick, stride_color: tuple[int, int, int] | None = None
    ):

        brick_config = self.config["bricks"][brick.brick_type]

        # Calculate course number for positioning
        course_height = (
            self.config["joints"]["bed_joint"] + self.config["bricks"]["full"]["height"]
        )
        course_num = int(brick.position.y / course_height)

        x_px = self.wall_x + self.mm_to_px(brick.position.x)
        # Flip Y coordinate since pygame Y increases downward
        y_px = (
            self.wall_y
            + self.wall_height_px
            - self.mm_to_px((course_num + 1) * course_height)
        )

        length_px = self.mm_to_px(brick_config["length"])
        height_px = self.mm_to_px(brick_config["height"])

        brick_rect = pygame.Rect(x_px, y_px, length_px, height_px)

        if stride_color and brick.state == BrickState.BUILT:
            color = stride_color
        elif brick.state == BrickState.BUILT:
            color = self.COLORS["built_brick"]
        else:
            color = self.COLORS["planned_brick"]

        pygame.draw.rect(self.screen, color, brick_rect)
        pygame.draw.rect(self.screen, self.COLORS["brick_outline"], brick_rect, 1)

        if self.debug_mode and length_px > 15:
            text = self.small_font.render(str(brick.id), True, self.COLORS["text"])
            text_rect = text.get_rect(center=brick_rect.center)
            self.screen.blit(text, text_rect)

    def _draw_grid(self):
        # Vertical lines every 100mm
        for x_mm in range(0, int(self.config["wall"]["width"]), 100):
            x_px = self.wall_x + self.mm_to_px(x_mm)
            pygame.draw.line(
                self.screen,
                self.COLORS["grid"],
                (x_px, self.wall_y),
                (x_px, self.wall_y + self.wall_height_px),
            )

        # Horizontal lines per course
        course_height = (
            self.config["joints"]["bed_joint"] + self.config["bricks"]["full"]["height"]
        )
        for course in range(int(self.config["wall"]["height"] // course_height) + 1):
            y_mm = course * course_height
            y_px = self.wall_y + self.wall_height_px - self.mm_to_px(y_mm)
            pygame.draw.line(
                self.screen,
                self.COLORS["grid"],
                (self.wall_x, y_px),
                (self.wall_x + self.wall_width_px, y_px),
            )

    def _draw_stride_legend(self, stride_manager: StrideManager):
        title = self.font.render("Strides:", True, self.COLORS["text"])
        self.screen.blit(title, (self.legend_x, self.legend_y))

        for i, stride in enumerate(stride_manager.strides):
            y = self.legend_y + 25 + i * 20

            color_rect = pygame.Rect(self.legend_x, y, 15, 15)
            pygame.draw.rect(self.screen, stride.color, color_rect)
            pygame.draw.rect(self.screen, self.COLORS["brick_outline"], color_rect, 1)

            text = self.small_font.render(
                f"S{stride.id + 1}", True, self.COLORS["text"]
            )
            self.screen.blit(text, (self.legend_x + 20, y))

    def _draw_info_panel(self, wall: Wall, robot: Robot | None = None):
        wall_info = f"Wall: {wall.width:.0f}mm × {wall.height:.0f}mm ({wall.num_courses} courses)"
        text = self.font.render(wall_info, True, self.COLORS["text"])
        self.screen.blit(text, (self.info_x, self.info_y))

        brick_info = f"Bricks: {len(wall.built_bricks)}/{wall.total_bricks} ({wall.completion_percentage:.1f}%)"
        text = self.font.render(brick_info, True, self.COLORS["text"])
        self.screen.blit(text, (self.info_x, self.info_y + 25))

        if robot:
            robot_info = f"Robot: ({robot.position.x:.0f}, {robot.position.y:.0f})"
            text = self.font.render(robot_info, True, self.COLORS["text"])
            self.screen.blit(text, (self.info_x, self.info_y + 50))

        scale_info = f"Scale: 1mm = {self.scale:.2f}px"
        text = self.small_font.render(scale_info, True, self.COLORS["text"])
        scale_y = self.info_y + 75 if robot else self.info_y + 50
        self.screen.blit(text, (self.info_x, scale_y))

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
            elif event.type == pygame.VIDEORESIZE:
                self.window_width = event.w
                self.window_height = event.h
                self.screen = pygame.display.set_mode(
                    (self.window_width, self.window_height), pygame.RESIZABLE
                )
                self._calculate_layout()
        return True

    def cleanup(self):
        pygame.quit()
