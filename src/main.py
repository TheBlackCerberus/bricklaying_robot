from .renderer import PygameRenderer
from .models.wall import Wall
from .models.brick import Brick, BrickState
from .models.robot import Robot
from .models.stride import StrideManager
from .configs.config import load_wall_config, Config
from .bonds.stretcher_bond import calculate_stretcher_bond
from .bonds.english_cross_bond import calculate_english_cross_bond
from .bonds.flemish_bond import calculate_flemish_bond
from .bonds.wild_bond import calculate_wild_bond
from .algos.naive_build import naive_build_algorithm
import pygame
import argparse


def get_bond_calculator(bond_type: str):
    bond_calculators = {
        "stretcher": calculate_stretcher_bond,
        "english_cross": calculate_english_cross_bond,
        "flemish": calculate_flemish_bond,
        "wild": calculate_wild_bond,
    }

    if bond_type not in bond_calculators:
        available = ", ".join(bond_calculators.keys())
        raise ValueError(f"Unknown bond type '{bond_type}'. Available: {available}")

    return bond_calculators[bond_type]


def get_algorithm(algo_name: str):
    algorithms = {
        "naive_build": naive_build_algorithm,
    }

    if algo_name not in algorithms:
        available = ", ".join(algorithms.keys())
        raise ValueError(f"Unknown algorithm '{algo_name}'. Available: {available}")

    return algorithms[algo_name]


def main():
    parser = argparse.ArgumentParser(description="Bricklaying Robot Visualization")
    parser.add_argument(
        "--wall",
        default="stretcher_bond_wall",
        help="Wall configuration (stretcher_bond_wall, english_cross_bond_wall, flemish_bond_wall, wild_bond_wall)",
    )
    parser.add_argument(
        "--algo", default="naive_build", help="Build algorithm (naive_build)"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.4,
        help="Maximum scale factor - wall auto-fits to window but won't exceed this value (0.1-1.0, default: 0.4)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Start in debug mode (shows grid and brick IDs)",
    )

    args = parser.parse_args()

    # Validate scale
    if args.scale < 0.1 or args.scale > 1.0:
        print(f"Error: Scale factor {args.scale} is out of range. Use 0.1-1.0")
        return

    try:
        config: Config = load_wall_config(args.wall)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Determine bond type from config name
    bond_type = "stretcher"
    if "english_cross" in args.wall:
        bond_type = "english_cross"
    elif "flemish" in args.wall:
        bond_type = "flemish"
    elif "stretcher" in args.wall:
        bond_type = "stretcher"
    elif "wild" in args.wall:
        bond_type = "wild"

    print("=" * 50)
    print("Config")
    print("=" * 50)
    print(f"Loading wall: {args.wall}")
    print(f"Bond type: {bond_type}")
    print(f"Algorithm: {args.algo}")
    print(f"Scale: {args.scale}")
    print("=" * 50)

    wall = Wall(config)
    robot = Robot(config)
    stride_manager = StrideManager()
    Brick.configure(config)

    try:
        bond_calculator = get_bond_calculator(bond_type)
        bricks = bond_calculator(wall, config)
    except ValueError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error calculating bond pattern: {e}")
        return

    # Bond & Brick validation
    failed_bricks = 0
    for brick in bricks:
        if not wall.try_add_brick(brick):
            print(
                f"Failed to add brick {brick.id}, {brick.position.x}, {brick.position.y}"
            )
            failed_bricks += 1

    if failed_bricks > 0:
        print(f"❌ Configuration Error: {failed_bricks} bricks failed validation")
        print(
            "💡 This indicates the wall configuration isn't suitable for this bond pattern"
        )
        print(
            f"   Please adjust the wall configuration in: src/configs/{args.wall}.yaml"
        )
        return

    for brick in wall.bricks:
        brick.state = BrickState.PLANNED

    print("Calculating build algorithm...")
    try:
        algorithm = get_algorithm(args.algo)
        strides, movements = algorithm(wall, robot, stride_manager, config)
    except ValueError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error running build algorithm: {e}")
        return

    print("=" * 50)
    print("Stride info")
    print("=" * 50)
    print(f"Generated {len(strides)} strides with {len(movements)} movements")
    print("Stride positions:")
    for i, stride in enumerate(strides):
        print(
            f"  Stride {i+1}: ({stride.robot_position.x:.0f}, {stride.robot_position.y:.0f}) - {len(stride.bricks)} bricks"
        )
    print("=" * 50)

    # Reset robot to initial position
    robot.position.x = robot.reach_width / 2
    robot.position.y = 0

    current_brick_index = 0
    current_stride_index = 0
    current_brick_in_stride = 0
    robot_mode = False

    renderer = PygameRenderer(config, target_scale=args.scale, debug_mode=args.debug)

    print("Wall Builder")
    print("=" * 50)
    print("Building Modes:")
    print("- Manual Mode (default): Build brick by brick")
    print("- Robot Mode: Follow robot algorithm with stride colors")
    print()
    print("Controls:")
    print("Manual Mode:")
    print("  - ENTER: Build next brick")
    print("  - SPACE: Build all remaining bricks")
    print("Robot Mode:")
    print("  - ENTER: Build next brick in current stride")
    print("  - S: Complete current stride and move to next")
    print("  - A: Auto-play robot algorithm (continuous)")
    print("Common:")
    print("  - M: Toggle between Manual/Robot mode")
    print("  - R: Reset (all bricks back to planned)")
    print("  - D: Toggle debug mode (grid + brick IDs)")
    print("  - ESC: Quit")
    print()
    print("Press ENTER to start building...")

    auto_play = False
    auto_play_timer = 0
    auto_play_delay = 30

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    # Toggle debug mode
                    renderer.debug_mode = not renderer.debug_mode
                elif event.key == pygame.K_m:
                    # Toggle robot mode
                    robot_mode = not robot_mode
                    auto_play = False
                    mode_name = "Robot Algorithm" if robot_mode else "Manual"
                    print(f"Switched to {mode_name} mode")
                    if robot_mode and current_stride_index < len(strides):
                        stride = strides[current_stride_index]
                        robot.position.x = stride.robot_position.x
                        robot.position.y = stride.robot_position.y
                        print(
                            f"Robot moved to stride {current_stride_index + 1} position: ({robot.position.x:.0f}, {robot.position.y:.0f})"
                        )
                elif event.key == pygame.K_a and robot_mode:
                    auto_play = not auto_play
                    status = "started" if auto_play else "stopped"
                    print(f"Auto-play {status}")
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if not robot_mode:
                        # Manual mode
                        if current_brick_index < len(wall.bricks):
                            wall.bricks[current_brick_index].state = BrickState.BUILT
                            current_brick_index += 1
                            built_count = sum(
                                1 for b in wall.bricks if b.state == BrickState.BUILT
                            )
                            progress = built_count / len(wall.bricks) * 100
                            print(
                                f"Built brick at ({wall.bricks[current_brick_index].position.x}, {wall.bricks[current_brick_index].position.y}) {current_brick_index}/{len(wall.bricks)} ({progress:.1f}%)"
                            )

                            if current_brick_index >= len(wall.bricks):
                                print("🎉 Wall completed!")
                    else:
                        # Robot mode: Build next brick in current stride
                        if current_stride_index < len(strides):
                            stride = strides[current_stride_index]
                            if current_brick_in_stride < len(stride.bricks):
                                brick = stride.bricks[current_brick_in_stride]
                                brick.state = BrickState.BUILT
                                current_brick_in_stride += 1

                                built_in_stride = current_brick_in_stride
                                total_in_stride = len(stride.bricks)
                                built_count = sum(
                                    1
                                    for b in wall.bricks
                                    if b.state == BrickState.BUILT
                                )
                                progress = built_count / len(wall.bricks) * 100

                                print(
                                    f"🤖 Built brick {built_in_stride}/{total_in_stride} in stride {current_stride_index + 1} ({progress:.1f}% total)"
                                )

                                if current_brick_in_stride >= len(stride.bricks):
                                    print(
                                        f"✅ Stride {current_stride_index + 1} completed!"
                                    )
                                    current_stride_index += 1
                                    current_brick_in_stride = 0

                                    if current_stride_index < len(strides):
                                        next_stride = strides[current_stride_index]
                                        robot.position.x = next_stride.robot_position.x
                                        robot.position.y = next_stride.robot_position.y
                                        print(
                                            f"🤖 Robot moved to stride {current_stride_index + 1} position: ({robot.position.x:.0f}, {robot.position.y:.0f})"
                                        )
                                    else:
                                        print("🤖 Robot algorithm completed! 🎉")
                elif event.key == pygame.K_s and robot_mode:
                    # Robot mode: Complete current stride
                    if current_stride_index < len(strides):
                        stride = strides[current_stride_index]
                        for i in range(current_brick_in_stride, len(stride.bricks)):
                            stride.bricks[i].state = BrickState.BUILT

                        built_count = sum(
                            1 for b in wall.bricks if b.state == BrickState.BUILT
                        )
                        progress = built_count / len(wall.bricks) * 100
                        print(
                            f"🤖 Completed stride {current_stride_index + 1} ({len(stride.bricks)} bricks, {progress:.1f}% total)"
                        )

                        current_stride_index += 1
                        current_brick_in_stride = 0

                        if current_stride_index < len(strides):
                            next_stride = strides[current_stride_index]
                            robot.position.x = next_stride.robot_position.x
                            robot.position.y = next_stride.robot_position.y
                            print(
                                f"🤖 Robot moved to stride {current_stride_index + 1} position: ({robot.position.x:.0f}, {robot.position.y:.0f})"
                            )
                        else:
                            print("🤖 Robot algorithm completed! 🎉")
                elif event.key == pygame.K_SPACE and not robot_mode:
                    # Manual mode: Build all remaining bricks
                    remaining = len(wall.bricks) - sum(
                        1 for b in wall.bricks if b.state == BrickState.BUILT
                    )
                    if remaining > 0:
                        for brick in wall.bricks:
                            brick.state = BrickState.BUILT
                        current_brick_index = len(wall.bricks)
                        print(
                            f"Built {remaining} remaining bricks - Wall completed! 🎉"
                        )
                elif event.key == pygame.K_r:
                    # Reset all bricks to planned
                    for brick in wall.bricks:
                        brick.state = BrickState.PLANNED
                    current_brick_index = 0
                    current_stride_index = 0
                    current_brick_in_stride = 0
                    robot.position.x = 0
                    robot.position.y = 0
                    auto_play = False
                    print("Reset - All bricks back to planned state, robot at origin")
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                renderer.window_width = event.w
                renderer.window_height = event.h
                renderer.screen = pygame.display.set_mode(
                    (renderer.window_width, renderer.window_height), pygame.RESIZABLE
                )

        # Auto-play logic
        if auto_play and robot_mode:
            auto_play_timer += 1
            if auto_play_timer >= auto_play_delay:
                auto_play_timer = 0
                if current_stride_index < len(strides):
                    stride = strides[current_stride_index]
                    if current_brick_in_stride < len(stride.bricks):
                        # Build next brick in stride
                        brick = stride.bricks[current_brick_in_stride]
                        brick.state = BrickState.BUILT
                        current_brick_in_stride += 1

                        if current_brick_in_stride >= len(stride.bricks):
                            current_stride_index += 1
                            current_brick_in_stride = 0

                            if current_stride_index < len(strides):
                                next_stride = strides[current_stride_index]
                                robot.position.x = next_stride.robot_position.x
                                robot.position.y = next_stride.robot_position.y
                            else:
                                auto_play = False
                                print("🤖 Robot algorithm completed! 🎉")

        robot_for_render = robot if robot_mode else None
        stride_manager_for_render = stride_manager if robot_mode else None

        renderer.render_wall(wall, robot_for_render, stride_manager_for_render)
        clock.tick(60)

    renderer.cleanup()
    print("Demo finished.")


if __name__ == "__main__":
    main()
