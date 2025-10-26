import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((960, 540), pygame.RESIZABLE, display=2)
clock = pygame.time.Clock()
running = True
dt = 0


class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 20

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


class Joystick:
    def __init__(self, index):
        self.py_joy_inst = pygame.joystick.Joystick(index)

        self.values = {
            axis: [] for axis in ("ls_x", "ls_y", "rs_x", "rs_y", "lt", "rt")
        }
        self.smoothed_axes = {
            axis: 0 for axis in ("ls_x", "ls_y", "rs_x", "rs_y", "lt", "rt")
        }
        self.buttons = {}

    def get_input(
        self, smooth_type: int = 0, smoothing_factor: int = 1, deadzone: float = 0
    ):
        """
        Updates button and axis values\n
        smoothing_factor must be greater than 0\n
        deadzone typically under 0.1\n
        smooth_type:\n
        \t0 - No axis smoothing
        \t1 - Joystick smoothing only
        \t2 - Trigger smoothing only
        \t3 - Joystick & Trigger smoothing
        """

        self.buttons = {
            "cross": self.py_joy_inst.get_button(0),
            "circle": self.py_joy_inst.get_button(1),
            "square": self.py_joy_inst.get_button(2),
            "triangle": self.py_joy_inst.get_button(3),
            "share": self.py_joy_inst.get_button(4),
            "ps": self.py_joy_inst.get_button(5),
            "options": self.py_joy_inst.get_button(6),
            "l_stick_click": self.py_joy_inst.get_button(7),
            "r_stick_click": self.py_joy_inst.get_button(8),
            "lb": self.py_joy_inst.get_button(9),
            "rb": self.py_joy_inst.get_button(10),
            "up": self.py_joy_inst.get_button(11),
            "down": self.py_joy_inst.get_button(12),
            "left": self.py_joy_inst.get_button(13),
            "right": self.py_joy_inst.get_button(14),
            "t_pad_click": self.py_joy_inst.get_button(15),
        }
        axes = {
            "ls_x": self.py_joy_inst.get_axis(0),
            "ls_y": self.py_joy_inst.get_axis(1),
            "rs_x": self.py_joy_inst.get_axis(2),
            "rs_y": self.py_joy_inst.get_axis(3),
            "lt": (self.py_joy_inst.get_axis(4) + 1) / 2,
            "rt": (self.py_joy_inst.get_axis(5) + 1) / 2,
        }

        match smooth_type:
            case 0:
                for a in axes:
                    self.smoothed_axes[a] = self._smooth_axis(
                        axes[a], self.values[a], smoothing_factor=1, deadzone=0
                    )
            case 1:
                for a in axes:
                    if a in ["lt", "rt"]:
                        self.smoothed_axes[a] = self._smooth_axis(
                            axes[a], self.values[a], smoothing_factor=1, deadzone=0
                        )
                    self.smoothed_axes[a] = self._smooth_axis(
                        axes[a], self.values[a], smoothing_factor, deadzone
                    )
            case 2:
                for a in axes:
                    if a not in ["lt", "rt"]:
                        self.smoothed_axes[a] = self._smooth_axis(
                            axes[a], self.values[a], smoothing_factor=1, deadzone=0
                        )
                    self.smoothed_axes[a] = self._smooth_axis(
                        axes[a], self.values[a], smoothing_factor, deadzone
                    )
            case 3:
                for a in axes:
                    self.smoothed_axes[a] = self._smooth_axis(
                        axes[a], self.values[a], smoothing_factor, deadzone
                    )

        # circle correction
        uncircle_factor_ls = math.sqrt(
            self.smoothed_axes["ls_x"] ** 2 + self.smoothed_axes["ls_y"] ** 2
        )
        if uncircle_factor_ls**2 > 1:
            self.smoothed_axes["ls_x"] *= 1 / uncircle_factor_ls
            self.smoothed_axes["ls_y"] *= 1 / uncircle_factor_ls

        uncircle_factor_rs = math.sqrt(
            self.smoothed_axes["rs_x"] ** 2 + self.smoothed_axes["rs_y"] ** 2
        )
        if uncircle_factor_rs**2 > 1:
            self.smoothed_axes["rs_x"] *= 1 / uncircle_factor_rs
            self.smoothed_axes["rs_y"] *= 1 / uncircle_factor_rs

    def _smooth_axis(
        self, axis: float, values: list, smoothing_factor: int, deadzone: float
    ):
        """
        Smoothing factor must be int greater than 0\n
        Deadzone 0->1 (typically around 0.1 or less)
        """
        if -deadzone < axis < deadzone:
            axis = 0

        values.append(axis)
        if len(values) > smoothing_factor:
            values.pop(0)
        return sum(values) / len(values)


pygame.joystick.init()

player = [Joystick(i) for i in range(pygame.joystick.get_count())]

while running:

    if pygame.joystick.get_count() != len(player):
        player = [Joystick(i) for i in range(pygame.joystick.get_count())]

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((220, 220, 220))

    # Text instance
    text_print = TextPrint()

    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    l_x_center_point = screen.get_width() * (4 / 10)
    r_x_center_point = screen.get_width() * (7 / 10)
    y_center_point = screen.get_height() * (6 / 10)
    radius = min(screen.get_width() / 7, screen.get_height() / 2)
    small_radius_factor = 0.2

    if len(player) >= 1:
        player[0].get_input(smooth_type=1, smoothing_factor=5, deadzone=0.05)

        for btn, val in player[0].buttons.items():
            text_print.tprint(screen, f"{btn}: {val}")
        for ax, val in player[0].smoothed_axes.items():
            text_print.tprint(screen, f"{ax}: {val:.2f}")

        # Left Background Circle
        pygame.draw.circle(
            screen,
            (200, 200, 200),
            (l_x_center_point, y_center_point),
            radius,
        )

        # Right Background Circle
        pygame.draw.circle(
            screen,
            (200, 200, 200),
            (r_x_center_point, y_center_point),
            radius,
        )

        # Left stick circle
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (
                l_x_center_point
                + player[0].smoothed_axes["ls_x"] * radius * (1 - small_radius_factor),
                y_center_point
                + player[0].smoothed_axes["ls_y"] * radius * (1 - small_radius_factor),
            ),
            radius * small_radius_factor,
        )

        # Right stick circle
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (
                r_x_center_point
                + player[0].smoothed_axes["rs_x"] * radius * (1 - small_radius_factor),
                y_center_point
                + player[0].smoothed_axes["rs_y"] * radius * (1 - small_radius_factor),
            ),
            radius * small_radius_factor,
        )

        # Left Background Rect
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            pygame.Rect(
                l_x_center_point - radius * 0.8,
                y_center_point - radius - 50,
                radius * 1.6,
                20,
            ),
        )

        # Left Trigger Rect
        pygame.draw.rect(
            screen,
            (200, 100, 100),
            pygame.Rect(
                l_x_center_point - radius * 0.8,
                y_center_point - radius - 50,
                radius * 1.6 * player[0].smoothed_axes["lt"],
                20,
            ),
        )

        # Right Background Rect
        pygame.draw.rect(
            screen,
            (200, 100, 100),
            pygame.Rect(
                r_x_center_point - radius * 0.8,
                y_center_point - radius - 50,
                radius * 1.6,
                20,
            ),
        )

        # Right Trigger Rect
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            pygame.Rect(
                r_x_center_point - radius * 0.8,
                y_center_point - radius - 50,
                radius * 1.6 * (1 - player[0].smoothed_axes["rt"]),
                20,
            ),
        )

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS
    # dt is delta time in seconds since last frame, used for framerate-independent physics.
    dt = clock.tick(120) / 1000

pygame.quit()
