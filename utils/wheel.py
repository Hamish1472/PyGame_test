import pygame

pygame.init()
pygame.joystick.init()

# Set initial window
screen = pygame.display.set_mode((300, 300), pygame.RESIZABLE, display=2)
clock = pygame.time.Clock()
running = True


class TextPrint:
    def __init__(self):
        self.font = pygame.font.Font(None, 25)
        self.line_height = 20
        self.reset()

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10


class Joystick:
    def __init__(self, index):
        self.js = pygame.joystick.Joystick(index)
        self.js.init()
        self.values = {axis: [] for axis in ("steer", "brake", "throttle")}
        self.smoothed_axes = {axis: 0 for axis in ("steer", "brake", "throttle")}
        self.buttons = {}
        self.hat = (0, 0)

    def get_input(self):
        self.buttons = {
            "shift_down": self.js.get_button(0),
            "shift_up": self.js.get_button(1),
            "triangle": self.js.get_button(2),
            "circle": self.js.get_button(3),
            "square": self.js.get_button(4),
            "cross": self.js.get_button(5),
            "dial_down": self.js.get_button(6),
            "dial_up": self.js.get_button(7),
            "r2": self.js.get_button(8),
            "l2": self.js.get_button(9),
            "l1": self.js.get_button(10),
            "r1": self.js.get_button(11),
            "ps": self.js.get_button(12),
        }
        axes = {
            "steer": self.js.get_axis(0),
            "brake": self.js.get_axis(1),
            "throttle": self.js.get_axis(2),
        }
        self.hat = self.js.get_hat(0)
        for a in axes:
            self.smoothed_axes[a] = self._smooth_axis(axes[a], self.values[a])

    def _smooth_axis(self, value, buf, smoothing=10):
        if -0.05 < value < 0.05:
            value = 0
        buf.append(value)
        if len(buf) > smoothing:
            buf.pop(0)
        return sum(buf) / len(buf)


# Create joystick instance
wheel = Joystick(0)
text_print = TextPrint()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((200, 200, 200))
    text_print.reset()

    wheel.get_input()

    # Print joystick data
    for k, v in wheel.buttons.items():
        text_print.tprint(screen, f"{k}: {v}")
    for k, v in wheel.smoothed_axes.items():
        text_print.tprint(screen, f"{k}: {v:.2f}")
    text_print.tprint(screen, f"hat: {wheel.hat}")

    # Resize window to fit content height
    text_height = text_print.y + 20
    width, _ = screen.get_size()
    if text_height != screen.get_height():
        screen = pygame.display.set_mode((width, text_height), pygame.RESIZABLE)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
