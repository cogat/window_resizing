#!/opt/homebrew/bin/python3

import subprocess
from dataclasses import dataclass
import os
from screeninfo import get_monitors
import sys

EXTENSION = "applescript"
# EXTENSION = "scpt"


@dataclass
class Box:
    x: int
    y: int
    width: int
    height: int


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


def set_front_window_box(box: Box):
    run_applescript("set_box", box.x, box.y, box.width, box.height)


def get_desktop_boxes() -> list[Box]:
    return [
        Box(x=monitor.x, y=monitor.y, width=monitor.width, height=monitor.height)
        for monitor in get_monitors()
    ]


def get_desktop_for_box(box: Box) -> Box:
    return get_desktop_boxes()[0]


def resize_to_screen_proportion(x, y, width, height):
    box = get_front_window_box()
    desktop = get_desktop_for_box(box)
    new_box = Box(
        x=desktop.x + desktop.width * x,
        y=desktop.y + desktop.height * y,
        width=desktop.width * width,
        height=desktop.height * height,
    )
    set_front_window_box(new_box)


if __name__ == "__main__":
    param = os.environ.get("KMVAR_macro", "").lower()
    if not param:
        try:
            param = sys.argv[1]
        except IndexError:
            param = ""
    if "enter" in param:
        resize_to_screen_proportion(0, 0, 1, 1)
    elif "left" in param:
        resize_to_screen_proportion(0, 0, 0.5, 1)
    elif "right" in param:
        resize_to_screen_proportion(0.5, 0, 0.5, 1)
    elif "up" in param:
        resize_to_screen_proportion(0, 0, 1, 0.5)
    elif "down" in param:
        resize_to_screen_proportion(0, 0.5, 1, 0.5)
    else:
        resize_to_screen_proportion(0.25, 0.25, 0.5, 0.5)
