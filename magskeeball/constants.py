from enum import Enum

FPS = 20


# these map to the physical pins on the arduino except QUIT
class Button(Enum):
    QUIT = 0
    NULL_01 = 1
    B1000L = 2
    B1000R = 3
    B500 = 4
    B400 = 5
    B300 = 6
    B200 = 7
    B100 = 8
    RETURN = 9
    CONFIG = 10
    START = 11
    SELECT = 12
    NULL_13 = 13
    NULL_14 = 14
    NULL_15 = 15
    NULL_16 = 16
    NULL_17 = 17
    NULL_18 = 18
    NULL_19 = 19


B = Button
BUTTON = Button

POINTS = {
    Button.B1000L: 1000,
    Button.B1000R: 1000,
    Button.B500: 500,
    Button.B400: 400,
    Button.B300: 300,
    Button.B200: 200,
    Button.B100: 100,
}

COLORS = {
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "YELLOW": (255, 255, 0),
    "GREEN": (0, 255, 0),
    "CYAN": (0, 255, 255),
    "BLUE": (50, 50, 255),
    "MAGENTA": (255, 0, 255),
    "PINK": (255, 150, 150),
    "WHITE": (255, 255, 255),
    "GRAY": (128, 128, 128),
    "PURPLE": (100, 0, 255),
    "ORANGE": (255, 69, 0),
}

BALL_COLORS = [
    "RED",
    "RED",
    "YELLOW",
    "YELLOW",
    "GREEN",
    "GREEN",
    "GREEN",
    "GREEN",
    "GREEN",
    "GREEN",
]
