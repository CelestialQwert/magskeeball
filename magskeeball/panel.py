# from .common import *
from PIL import Image, ImageFont, ImageDraw
import sys
import pygame
import platform
import time

from . import constants as const
from . import resources

REAL = 0
EMULATED = 1
BOTH = 2


class Panel:

    def __init__(self, scale=6):

        if platform.system() != "Windows":
            self.init_real_panel()
            self.buffer_canvas = Image.new("RGB", (192, 32))
            self.real_panel = True
            self.emulated_panel = False
            print("Hello LED panel!")
        else:
            self.init_emulated_panel(scale)
            self.real_panel = False
            self.emulated_panel = True
            print("Hello emulated panel!")

        self.canvas = Image.new("RGB", (96, 64))
        self.draw = ImageDraw.Draw(self.canvas)
        self.paste = self.canvas.paste

        self.res = resources.ResourceManager()
        self.res.load_fonts()

    def init_real_panel(self):
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.chain_length = 6
        self.options.parallel = 1
        self.options.brightness = 50
        self.options.hardware_mapping = "adafruit-hat-pwm"
        self.options.drop_privileges = False
        self.matrix = RGBMatrix(options=self.options)

    def init_emulated_panel(self, scale):
        pygame.display.init()
        self.e_size = tuple([x * scale for x in (96, 64)])
        self.emu_panel = pygame.display.set_mode(self.e_size)
        pygame.display.set_caption("MAGskeeball (virtual score panel)")

    def update(self):
        if self.real_panel:
            top = self.canvas.crop((0, 0, 96, 32))
            bottom = self.canvas.crop((0, 32, 96, 64))
            self.buffer_canvas.paste(top, (0, 0))
            self.buffer_canvas.paste(bottom, (96, 0))
            self.matrix.SetImage(self.buffer_canvas, 0, 0)
        if self.emulated_panel:
            data = self.canvas.resize(self.e_size, Image.NEAREST).tobytes()
            mode = self.canvas.mode
            pyg_canvas = pygame.image.fromstring(data, self.e_size, mode)
            self.emu_panel.fill((0, 0, 0))
            self.emu_panel.blit(pyg_canvas, (0, 0))
            pygame.display.update()

    def paste(self, image, coords):
        self.canvas.paste(image, coords)

    def clear(self):
        self.draw.rectangle((0, 0, 96, 64), fill=(0, 0, 0))

    def fill(self, color):
        self.draw.rectangle((0, 0, 96, 64), fill=color)

    def draw_text(self, pos, text, font, color):
        if isinstance(color, str):
            colour_tuple = const.COLORS[color]
        else:
            colour_tuple = color
        self.draw.text(pos, str(text), font=self.res.fonts[font], fill=colour_tuple)

    def draw_time(self, pos=(7, 6), display_time=0, color="WHITE"):
        posx, posy = pos
        minutes = display_time // (60 * const.FPS)
        seconds = (display_time // const.FPS) % 60
        fraction = round(100.0 / const.FPS * (display_time % const.FPS))
        fill_col = const.COLORS[color]

        self.draw_text((posx, posy), f"{minutes:01d}", "Digital14", color)
        self.draw_text((21 + posx, posy), f"{seconds:02d}", "Digital14", color)
        self.draw_text((56 + posx, posy), f"{fraction:02d}", "Digital14", color)
        self.draw.rectangle([14 + posx, 12 + posy, 17 + posx, 15 + posy], fill=fill_col)
        self.draw.rectangle([14 + posx, 3 + posy, 17 + posx, 6 + posy], fill=fill_col)
        self.draw.rectangle([49 + posx, 15 + posy, 52 + posx, 18 + posy], fill=fill_col)

    def draw_message_screen(self, message, font="Medium", color="WHITE"):
        self.clear()
        self.draw_text((2, 2), message, font, color)
        self.update()
