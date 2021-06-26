#!/opt/homebrew/bin/python3

import subprocess
from dataclasses import dataclass
import os
from screeninfo import get_monitors
import sys

DEBUG = False

EXTENSION = "applescript"
# EXTENSION = "scpt"

UPWARDS = "upwards"
DOWNWARDS = "downwards"
LEFTWARDS = "leftwards"
RIGHTWARDS = "rightwards"
SHIFT_COMMANDS = (UPWARDS, DOWNWARDS, LEFTWARDS, RIGHTWARDS)

FULL = "enter"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
RESIZE_COMMANDS = (FULL, UP, DOWN, LEFT, RIGHT)


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


@dataclass
class Box:
    _x: int
    _y: int
    _width: int
    _height: int

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def __str__(self):
        return f"{{x:{self.x}, y:{self.y}, w:{self.width}, h:{self.height}}}"

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def right(self):
        return self.x + self.width

    @property
    def desktop(self):
        return DESKTOP_BOXES[0]

    @property
    def height_fit(self):
        """Return how many of these windows would fit vertically"""
        return self.desktop.height / self.height

    @property
    def width_fit(self):
        """Return how many of these windows would fit horizontally"""
        return self.desktop.width / self.width

    @property
    def is_at_top(self):
        return self.y == self.desktop.y

    @property
    def is_at_left(self):
        return self.x == self.desktop.x

    @property
    def is_at_right(self):
        return self.right == self.desktop.right

    @property
    def is_at_bottom(self):
        return self.bottom == self.desktop.bottom

    def apply_to_front_window(self):
        run_applescript("set_box", self.x, self.y, self.width, self.height)

    def resize_to_screen_proportion(self, x, y, width, height):
        """Set params to None to leave as-is"""
        desktop = self.desktop
        if x is None:
            new_x = self.x
        else:
            new_x = desktop.x + desktop.width * x
        if y is None:
            new_y = self.y
        else:
            new_y = desktop.y + desktop.height * y
        if width is None:
            new_width = self.width
        else:
            new_width = desktop.width * width
        if height is None:
            new_height = self.height
        else:
            new_height = desktop.height * height

        new_box = Box(
            x=new_x,
            y=new_y,
            width=new_width,
            height=new_height,
        )
        log(f"proportionally: {x}, {y}, {width}, {height}")
        log(f"actually: {new_box}")
        new_box.apply_to_front_window()

    def shift(self, direction):
        if direction == UPWARDS:
            new_box = Box(
                x=self.x, y=self.y - self.height, width=self.width, height=self.height
            )
        elif direction == DOWNWARDS:
            new_box = Box(
                x=self.x, y=self.y + self.height, width=self.width, height=self.height
            )
        elif direction == LEFTWARDS:
            new_box = Box(
                x=self.x - self.width, y=self.y, width=self.width, height=self.height
            )
        elif direction == RIGHTWARDS:
            new_box = Box(
                x=self.x + self.width, y=self.y, width=self.width, height=self.height
            )
        new_box.apply_to_front_window()

    def resize(self, direction):
        log(f"resizing {self} inside {self.desktop}")
        if direction == UP:
            if self.is_at_top:
                new_height = 1 / (self.height_fit + 1)
                self.resize_to_screen_proportion(None, None, None, new_height)
            else:
                self.resize_to_screen_proportion(0, 0, 1, 0.5)
        elif direction == DOWN:
            if self.is_at_bottom:
                new_height = 1 / (self.height_fit + 1)
                self.resize_to_screen_proportion(None, 1 - new_height, None, new_height)
            else:
                self.resize_to_screen_proportion(0, 0.5, 1, 0.5)
        elif direction == LEFT:
            if self.is_at_left:
                new_width = 1 / (self.width_fit + 1)
                self.resize_to_screen_proportion(None, None, new_width, None)
            else:
                self.resize_to_screen_proportion(0, 0, 0.5, 1)
        elif direction == RIGHT:
            if self.is_at_right:
                new_width = 1 / (self.width_fit + 1)
                self.resize_to_screen_proportion(1 - new_width, None, new_width, None)
            else:
                self.resize_to_screen_proportion(0.5, 0, 0.5, 1)
        elif direction == FULL:
            self.resize_to_screen_proportion(0, 0, 1, 1)
        else:
            self.resize_to_screen_proportion(0.1, 0.1, 0.8, 0.8)


class DesktopBox(Box):
    MENUBAR_HEIGHT = 25

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y + self.MENUBAR_HEIGHT

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height - self.MENUBAR_HEIGHT


def get_desktop_boxes() -> list[Box]:
    return [
        DesktopBox(x=monitor.x, y=monitor.y, width=monitor.width, height=monitor.height)
        for monitor in get_monitors()
    ]


DESKTOP_BOXES = get_desktop_boxes()


class AppleScriptException(Exception):
    pass


def run_applescript(script, *args):
    p = subprocess.Popen(
        ["/usr/bin/osascript", f"{script}.{EXTENSION}"] + [str(arg) for arg in args],
        cwd=os.path.dirname(os.path.realpath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    out, err = p.communicate()
    if err:
        raise AppleScriptException(err)
    return out.strip().split(", ")


def get_front_window_box() -> Box:
    out = run_applescript("get_box")
    out = [int(x) for x in out]
    return Box(x=out[0], y=out[1], width=out[2], height=out[3])


if __name__ == "__main__":
    param = os.environ.get("KMVAR_macro", "").lower()
    if not param:
        try:
            param = sys.argv[1]
        except IndexError:
            param = ""

    box = get_front_window_box()
    for command in SHIFT_COMMANDS:
        if command in param:
            box.shift(command)
            break
    else:
        for command in RESIZE_COMMANDS:
            if command in param:
                box.resize(command)
                break
        else:
            box.resize(None)
